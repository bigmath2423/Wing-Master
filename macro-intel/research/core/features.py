"""Reimplementation des modules de l'indicateur SMC sous forme de FEATURES.

Chaque concept de l'indicateur (BOS, CHoCH, sweep de liquidite, FVG, Order
Block, premium/discount, Wyckoff, VWAP, ATR, session, ADX, Fibonacci, tendance
HTF) devient ici une colonne booleenne ou numerique evaluable a CHAQUE bougie.

Pourquoi des features plutot que des modules a activer/desactiver : une ablation
ne fournit qu'UN chiffre par module, confondu avec toutes les interactions, et
mesure sur ~2 000 trades. Une feature evaluee a chaque bougie se mesure sur des
centaines de milliers d'observations et donne une taille d'effet avec son
intervalle de confiance. C'est le meme concept teste avec ~100 fois plus de
puissance statistique.

REGLE ABSOLUE respectee partout : aucune valeur future. Chaque feature a la
bougie i n'utilise que l'information disponible a la CLOTURE de la bougie i.
Les pivots ne sont donc consideres comme connus qu'apres leur confirmation
(decalage de `swing_len` bougies), exactement comme ta.pivothigh en Pine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------
# Indicateurs de base
# --------------------------------------------------------------------------
def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l = df["high"], df["low"]
    up, dn = h.diff(), -l.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n)
    pdi = 100 * pd.Series(plus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * pd.Series(minus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def pivots(df: pd.DataFrame, n: int) -> tuple[pd.Series, pd.Series]:
    """Pivots confirmes, decales de n bougies : disponibles seulement une fois confirmes."""
    h, l = df["high"], df["low"]
    ph = h.rolling(2 * n + 1, center=True).max().eq(h) & h.notna()
    pl = l.rolling(2 * n + 1, center=True).min().eq(l) & l.notna()
    # la valeur n'est connue que n bougies plus tard -> on la publie decalee
    return (h.where(ph).shift(n), l.where(pl).shift(n))


def session_flag(idx: pd.DatetimeIndex, start: int, end: int) -> np.ndarray:
    """Fenetre horaire en heures UTC entieres (start inclus, end exclu)."""
    hh = idx.hour.values
    return (hh >= start) & (hh < end) if start < end else (hh >= start) | (hh < end)


# --------------------------------------------------------------------------
# Passe unique avec etat : structure, zones, liquidite, Wyckoff
# --------------------------------------------------------------------------
@dataclass
class FeatureConfig:
    swing_len: int = 10
    atr_len: int = 14
    struct_lookback: int = 30
    sweep_window: int = 20
    eq_tol_atr: float = 0.15
    fvg_min_atr: float = 0.10
    sweep_range_atr: float = 0.5
    sweep_rej_frac: float = 0.5
    wy_min_quiet: int = 20
    vol_len: int = 20
    vol_fake_mult: float = 0.8
    atr_avg_len: int = 50
    atr_min_mult: float = 0.7
    adx_len: int = 14
    htf_ema_len: int = 50
    htf_rule: str = "1h"
    imb_mult: float = 1.5
    names: list[str] = field(default_factory=list)


def build_features(df: pd.DataFrame, cfg: FeatureConfig | None = None) -> pd.DataFrame:
    """Retourne un DataFrame de features aligne sur df, sans aucun look-ahead."""
    cfg = cfg or FeatureConfig()
    n = len(df)
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)

    a = atr(df, cfg.atr_len).to_numpy(float)
    ph_s, pl_s = pivots(df, cfg.swing_len)
    ph = ph_s.to_numpy(float)
    pl = pl_s.to_numpy(float)

    # --- niveaux de la veille / semaine precedente (periodes CLOTUREES) ---
    day = df.index.normalize()
    dh = df["high"].groupby(day).max()
    dl = df["low"].groupby(day).min()
    pdh = day.map(dh.shift(1)).to_numpy(float)
    pdl = day.map(dl.shift(1)).to_numpy(float)
    week = df.index.to_period("W").to_timestamp()
    wh = df["high"].groupby(week).max()
    wl = df["low"].groupby(week).min()
    pwh = pd.Index(week).map(wh.shift(1)).to_numpy(float)
    pwl = pd.Index(week).map(wl.shift(1)).to_numpy(float)

    # --- sorties ---
    out = {k: np.zeros(n, bool) for k in (
        "bull_bos", "bear_bos", "bull_choch", "bear_choch",
        "bull_sweep", "bear_sweep", "bull_fvg_touch", "bear_fvg_touch",
        "bull_ob_touch", "bear_ob_touch", "in_discount", "in_premium",
        "wy_bull_ctx", "wy_bear_ctx", "bull_imb", "bear_imb",
        "bull_breaker", "bear_breaker",
    )}
    struct_trend = np.zeros(n, np.int8)
    bars_bull_break = np.full(n, 9999, int)
    bars_bear_break = np.full(n, 9999, int)
    bars_bull_sweep = np.full(n, 9999, int)
    bars_bear_sweep = np.full(n, 9999, int)
    break_vol_bull = np.full(n, np.nan)
    break_vol_bear = np.full(n, np.nan)
    range_pos = np.full(n, np.nan)     # position dans le range swing (0=bas, 1=haut)
    fib_r_bull = np.full(n, np.nan)
    fib_r_bear = np.full(n, np.nan)

    vol_sma = pd.Series(v).rolling(cfg.vol_len).mean().to_numpy(float)
    vol_ratio = np.divide(v, vol_sma, out=np.full(n, np.nan), where=(vol_sma > 0))

    # etat
    sh = sl = np.nan          # dernier swing haut / bas confirme
    trend = 0
    b_bull = b_bear = 9999
    s_bull = s_bear = 9999
    fvg_b = (np.nan, np.nan, False)   # top, bot, actif
    fvg_s = (np.nan, np.nan, False)
    ob_b = (np.nan, np.nan, False)
    ob_s = (np.nan, np.nan, False)
    swept_low = swept_high = np.nan
    eqh: list[float] = []
    eql: list[float] = []
    last_ph = last_pl = np.nan
    pdh_done = pdl_done = pwh_done = pwl_done = False
    prev_pdh = prev_pwh = np.nan
    wy_on = False
    wy_top = wy_bot = np.nan
    wy_prior = 0
    wy_phase = 0              # +1 accumulation, -1 distribution, 0 neutre
    wy_quiet = 0
    vb_bull = vb_bear = np.nan

    for i in range(n):
        ai = a[i] if np.isfinite(a[i]) else np.nan
        rng = h[i] - l[i]

        # ---------- Fair Value Gaps ----------
        if i >= 2 and np.isfinite(ai):
            gap_up = l[i] - h[i - 2]
            gap_dn = l[i - 2] - h[i]
            if gap_up > max(cfg.fvg_min_atr * ai, 0):
                fvg_b = (l[i], h[i - 2], True)
            if gap_dn > max(cfg.fvg_min_atr * ai, 0):
                fvg_s = (l[i - 2], h[i], True)
        if fvg_b[2] and c[i] < fvg_b[1]:
            fvg_b = (fvg_b[0], fvg_b[1], False)
        if fvg_s[2] and c[i] > fvg_s[0]:
            fvg_s = (fvg_s[0], fvg_s[1], False)

        # ---------- swings confirmes ----------
        if np.isfinite(ph[i]):
            if np.isfinite(last_ph) and np.isfinite(ai) and abs(ph[i] - last_ph) <= ai * cfg.eq_tol_atr:
                eqh.append(max(ph[i], last_ph))
                eqh = eqh[-6:]
            last_ph = ph[i]
            sh = ph[i]
        if np.isfinite(pl[i]):
            if np.isfinite(last_pl) and np.isfinite(ai) and abs(pl[i] - last_pl) <= ai * cfg.eq_tol_atr:
                eql.append(min(pl[i], last_pl))
                eql = eql[-6:]
            last_pl = pl[i]
            sl = pl[i]

        # ---------- cassure de structure (B1 : niveau stable) ----------
        prev_c = c[i - 1] if i else np.nan
        up_break = np.isfinite(sh) and np.isfinite(prev_c) and prev_c <= sh < c[i]
        dn_break = np.isfinite(sl) and np.isfinite(prev_c) and prev_c >= sl > c[i]
        if up_break:
            if trend == -1:
                out["bull_choch"][i] = True
            else:
                out["bull_bos"][i] = True
            trend = 1
            b_bull = 0
            vb_bull = vol_ratio[i]
            # Order Block haussier : derniere bougie baissiere avant la cassure
            for k in range(1, min(cfg.swing_len, i) + 1):
                if c[i - k] < o[i - k]:
                    ob_b = (h[i - k], l[i - k], True)
                    break
        if dn_break:
            if trend == 1:
                out["bear_choch"][i] = True
            else:
                out["bear_bos"][i] = True
            trend = -1
            b_bear = 0
            vb_bear = vol_ratio[i]
            for k in range(1, min(cfg.swing_len, i) + 1):
                if c[i - k] > o[i - k]:
                    ob_s = (h[i - k], l[i - k], True)
                    break

        # ---------- invalidation / breaker des Order Blocks ----------
        if ob_b[2] and c[i] < ob_b[1]:
            ob_b = (ob_b[0], ob_b[1], False)
            out["bear_breaker"][i] = True
        if ob_s[2] and c[i] > ob_s[0]:
            ob_s = (ob_s[0], ob_s[1], False)
            out["bull_breaker"][i] = True

        # ---------- sweeps de liquidite ----------
        bull_sw = bear_sw = False
        if np.isfinite(sl) and l[i] < sl < c[i] and (not np.isfinite(swept_low) or sl != swept_low):
            swept_low = sl
            bull_sw = True
        if np.isfinite(sh) and h[i] > sh > c[i] and (not np.isfinite(swept_high) or sh != swept_high):
            swept_high = sh
            bear_sw = True
        if np.isfinite(pdh[i]):
            if pdh[i] != prev_pdh:
                pdh_done = pdl_done = False
                prev_pdh = pdh[i]
            if not pdh_done and h[i] > pdh[i] > c[i]:
                pdh_done, bear_sw = True, True
            if not pdl_done and np.isfinite(pdl[i]) and l[i] < pdl[i] < c[i]:
                pdl_done, bull_sw = True, True
        if np.isfinite(pwh[i]):
            if pwh[i] != prev_pwh:
                pwh_done = pwl_done = False
                prev_pwh = pwh[i]
            if not pwh_done and h[i] > pwh[i] > c[i]:
                pwh_done, bear_sw = True, True
            if not pwl_done and np.isfinite(pwl[i]) and l[i] < pwl[i] < c[i]:
                pwl_done, bull_sw = True, True
        for lv in list(eqh):
            if h[i] > lv:
                if c[i] < lv:
                    bear_sw = True
                eqh.remove(lv)
        for lv in list(eql):
            if l[i] < lv:
                if c[i] > lv:
                    bull_sw = True
                eql.remove(lv)
        # qualite du sweep : expansion + rejet
        if np.isfinite(ai) and rng > 0:
            exp_ok = rng >= cfg.sweep_range_atr * ai
            bull_sw = bull_sw and exp_ok and (c[i] - l[i]) >= cfg.sweep_rej_frac * rng
            bear_sw = bear_sw and exp_ok and (h[i] - c[i]) >= cfg.sweep_rej_frac * rng
        if bull_sw:
            s_bull = 0
        if bear_sw:
            s_bear = 0

        # ---------- premium / discount + fibonacci ----------
        if np.isfinite(sh) and np.isfinite(sl) and sh > sl:
            eq = (sh + sl) / 2
            out["in_premium"][i] = c[i] > eq
            out["in_discount"][i] = c[i] < eq
            range_pos[i] = (c[i] - sl) / (sh - sl)
            fib_r_bull[i] = (sh - l[i]) / (sh - sl)
            fib_r_bear[i] = (h[i] - sl) / (sh - sl)

        # ---------- Wyckoff ----------
        if up_break or dn_break:
            wy_quiet = 0
        else:
            wy_quiet += 1
        if not wy_on and wy_quiet >= cfg.wy_min_quiet and np.isfinite(sh) and np.isfinite(sl) and sh > sl and sl <= c[i] <= sh:
            wy_on, wy_top, wy_bot, wy_prior = True, sh, sl, trend
            wy_phase = 1 if trend == -1 else (-1 if trend == 1 else 0)
        if wy_on:
            if l[i] < wy_bot < c[i]:
                wy_phase = 1
            if h[i] > wy_top > c[i]:
                wy_phase = -1
            if c[i] > wy_top or c[i] < wy_bot or up_break or dn_break:
                wy_on = False
        out["wy_bull_ctx"][i] = wy_phase > 0
        out["wy_bear_ctx"][i] = wy_phase < 0

        # ---------- imbalance ----------
        if np.isfinite(ai):
            body = c[i] - o[i]
            out["bull_imb"][i] = body >= cfg.imb_mult * ai
            out["bear_imb"][i] = -body >= cfg.imb_mult * ai

        # ---------- touches de zone ----------
        out["bull_fvg_touch"][i] = fvg_b[2] and l[i] <= fvg_b[0] and h[i] >= fvg_b[1]
        out["bear_fvg_touch"][i] = fvg_s[2] and h[i] >= fvg_s[1] and l[i] <= fvg_s[0]
        out["bull_ob_touch"][i] = ob_b[2] and l[i] <= ob_b[0] and h[i] >= ob_b[1]
        out["bear_ob_touch"][i] = ob_s[2] and h[i] >= ob_s[1] and l[i] <= ob_s[0]
        out["bull_sweep"][i] = bull_sw
        out["bear_sweep"][i] = bear_sw

        struct_trend[i] = trend
        bars_bull_break[i] = b_bull
        bars_bear_break[i] = b_bear
        bars_bull_sweep[i] = s_bull
        bars_bear_sweep[i] = s_bear
        break_vol_bull[i] = vb_bull
        break_vol_bear[i] = vb_bear
        b_bull += 1
        b_bear += 1
        s_bull += 1
        s_bear += 1

    f = pd.DataFrame(out, index=df.index)
    f["atr"] = a
    f["struct_bull"] = struct_trend == 1
    f["struct_bear"] = struct_trend == -1
    f["bull_break_recent"] = bars_bull_break <= cfg.struct_lookback
    f["bear_break_recent"] = bars_bear_break <= cfg.struct_lookback
    f["bull_sweep_recent"] = bars_bull_sweep <= cfg.sweep_window
    f["bear_sweep_recent"] = bars_bear_sweep <= cfg.sweep_window
    f["range_pos"] = range_pos

    # Fibonacci : zone de retracement atteinte
    for side, r in (("bull", fib_r_bull), ("bear", fib_r_bear)):
        f[f"{side}_fib"] = (np.abs(r - 0.705) <= 0.03) | (np.abs(r - 0.618) <= 0.03) | (np.abs(r - 0.786) <= 0.03)

    # Volume de la cassure
    f["bull_vol_ok"] = np.isnan(break_vol_bull) | (break_vol_bull >= cfg.vol_fake_mult)
    f["bear_vol_ok"] = np.isnan(break_vol_bear) | (break_vol_bear >= cfg.vol_fake_mult)
    f["vol_ratio"] = vol_ratio

    # VWAP de session (ancre journaliere)
    tp = (df["high"] + df["low"] + df["close"]) / 3
    grp = df.index.normalize()
    pv = (tp * df["volume"]).groupby(grp).cumsum()
    vv = df["volume"].groupby(grp).cumsum()
    vwap = (pv / vv.replace(0, np.nan)) if df["volume"].notna().any() else pd.Series(np.nan, index=df.index)
    f["above_vwap"] = df["close"] > vwap
    f["below_vwap"] = df["close"] < vwap

    # Regime de volatilite / directionnalite
    aser = pd.Series(a, index=df.index)
    f["atr_ok"] = aser >= aser.rolling(cfg.atr_avg_len).mean() * cfg.atr_min_mult
    f["adx"] = adx(df, cfg.adx_len)
    f["adx_trend"] = f["adx"] >= 20

    # Sessions (UTC)
    f["sess_london"] = session_flag(df.index, 7, 16)
    f["sess_ny"] = session_flag(df.index, 12, 21)
    f["kill_zone"] = session_flag(df.index, 6, 9) | session_flag(df.index, 12, 15)

    # Tendance HTF : EMA sur bougies superieures CLOTUREES (reindexee ffill)
    htf = df["close"].resample(cfg.htf_rule, label="left", closed="left").last().dropna()
    htf_e = ema(htf, cfg.htf_ema_len)
    bull_htf = (htf > htf_e).shift(1).reindex(df.index, method="ffill")
    f["htf_bull"] = bull_htf.fillna(False).astype(bool)
    f["htf_bear"] = (~bull_htf.fillna(True)).astype(bool)

    f["rsi"] = rsi(df["close"], 14)
    return f

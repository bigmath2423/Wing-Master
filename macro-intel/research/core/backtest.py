"""Simulateur de trades et metriques, avec hypotheses volontairement pessimistes.

Choix d'execution (tous defavorables au systeme teste, pour ne jamais surestimer) :
  - entree a la CLOTURE de la bougie de signal, jamais a un prix intra-bougie ;
  - si le stop ET une cible sont touches dans la MEME bougie, le STOP l'emporte ;
  - cout d'execution (spread + slippage) preleve a l'entree ET a chaque sortie
    partielle, en unites de prix ;
  - une seule position a la fois, aucun ajout.

Tout est exprime en R (1 R = risque initial du trade), ce qui rend les
resultats comparables entre timeframes, symboles et regimes de volatilite.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ExitPlan:
    sl_atr: float = 1.5          # distance du stop, en ATR
    tp1_r: float = 1.0           # cibles, en multiples du risque
    tp2_r: float = 2.0
    tp3_r: float = 3.0
    part1: float = 0.5           # fractions fermees a TP1 / TP2 (le reste a TP3)
    part2: float = 0.3
    breakeven_after_tp1: bool = True
    trail_r: float = 0.0         # 0 = TP3 fixe ; >0 = trailing de X R sur le reliquat
    trail_start_r: float = 1.0
    max_bars: int = 0            # 0 = pas de limite de duree


@dataclass
class Costs:
    per_unit: float = 0.30       # cout aller-retour total, en unites de prix
    risk_pct: float = 1.0        # % du capital risque par trade


def simulate(df: pd.DataFrame, atr_s: pd.Series, long_sig: pd.Series,
             short_sig: pd.Series, plan: ExitPlan, costs: Costs) -> pd.DataFrame:
    """Deroule les signaux et retourne la liste des trades (P&L exprime en R)."""
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    a = atr_s.to_numpy(float)
    ls = long_sig.fillna(False).to_numpy(bool)
    ss = short_sig.fillna(False).to_numpy(bool)
    idx = df.index
    n = len(df)
    half_cost = costs.per_unit / 2.0

    trades = []
    i = 0
    while i < n - 1:
        if not (ls[i] or ss[i]) or not np.isfinite(a[i]) or a[i] <= 0:
            i += 1
            continue
        is_long = bool(ls[i])
        entry = c[i]
        risk = plan.sl_atr * a[i]
        if risk <= 0:
            i += 1
            continue
        sl = entry - risk if is_long else entry + risk
        tps = [entry + s * plan.tp1_r * risk, entry + s * plan.tp2_r * risk,
               entry + s * plan.tp3_r * risk] if (s := 1 if is_long else -1) else []
        parts = [plan.part1, plan.part2, max(0.0, 1 - plan.part1 - plan.part2)]

        remaining = 1.0
        realized = 0.0                      # en R, hors couts
        peak = entry
        hit = [False, False, False]
        be_done = False
        j = i + 1
        exit_reason = "fin"
        while j < n:
            # --- le stop d'abord : hypothese pessimiste sur bougie ambigue ---
            stopped = (l[j] <= sl) if is_long else (h[j] >= sl)
            if stopped:
                realized += remaining * ((sl - entry) if is_long else (entry - sl)) / risk
                remaining = 0.0
                exit_reason = "SL" if not be_done else "BE"
                break
            # --- cibles fixes ---
            for k in range(3):
                if hit[k] or parts[k] <= 0:
                    continue
                if k == 2 and plan.trail_r > 0:
                    continue                # le reliquat est gere par le trailing
                reached = (h[j] >= tps[k]) if is_long else (l[j] <= tps[k])
                if reached:
                    hit[k] = True
                    realized += parts[k] * abs(tps[k] - entry) / risk
                    remaining -= parts[k]
                    if k == 0 and plan.breakeven_after_tp1:
                        sl, be_done = entry, True
            if remaining <= 1e-9:
                exit_reason = "TP"
                break
            # --- trailing sur le reliquat ---
            if plan.trail_r > 0 and hit[0]:
                peak = max(peak, h[j]) if is_long else min(peak, l[j])
                moved = ((peak - entry) if is_long else (entry - peak)) / risk
                if moved >= plan.trail_start_r:
                    ts = peak - plan.trail_r * risk if is_long else peak + plan.trail_r * risk
                    sl = max(sl, ts) if is_long else min(sl, ts)
            if plan.max_bars and (j - i) >= plan.max_bars:
                realized += remaining * ((c[j] - entry) if is_long else (entry - c[j])) / risk
                remaining = 0.0
                exit_reason = "temps"
                break
            j += 1

        if remaining > 1e-9:                # fin de donnees
            realized += remaining * ((c[min(j, n - 1)] - entry) if is_long else (entry - c[min(j, n - 1)])) / risk
        n_fills = 1 + sum(hit) + (1 if exit_reason in ("SL", "BE", "temps", "fin") else 0)
        cost_r = n_fills * half_cost / risk
        trades.append(dict(t_in=idx[i], t_out=idx[min(j, n - 1)], sens="long" if is_long else "short",
                           entry=entry, risk_px=risk, bars=min(j, n - 1) - i,
                           R_brut=realized, cout_R=cost_r, R=realized - cost_r,
                           sortie=exit_reason))
        i = min(j, n - 1) + 1
    return pd.DataFrame(trades)


def metrics(tr: pd.DataFrame, label: str = "") -> dict:
    """Metriques demandees + les garde-fous statistiques qui vont avec."""
    if tr is None or tr.empty:
        return dict(nom=label, trades=0)
    r = tr["R"].to_numpy(float)
    w, lo = r[r > 0], r[r <= 0]
    eq = np.cumsum(r)
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    dd = eq - peak
    pf = (w.sum() / abs(lo.sum())) if len(lo) and lo.sum() != 0 else np.inf
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 and r.std() > 0 else np.nan
    return dict(
        nom=label, trades=len(r),
        win_rate=100 * len(w) / len(r),
        profit_factor=pf,
        expectancy_R=r.mean(),
        R_total=r.sum(),
        dd_max_R=dd.min(),
        gain_moy_R=w.mean() if len(w) else 0.0,
        perte_moy_R=lo.mean() if len(lo) else 0.0,
        cout_moy_R=tr["cout_R"].mean(),
        t_stat=t,
    )


def compare(base: dict, variant: dict) -> dict:
    """Delta d'une variante par rapport a la reference."""
    out = {"nom": variant["nom"]}
    for k in ("trades", "win_rate", "profit_factor", "expectancy_R", "R_total", "dd_max_R"):
        b, v = base.get(k), variant.get(k)
        out[k] = v
        if isinstance(b, (int, float)) and isinstance(v, (int, float)) and np.isfinite(b) and np.isfinite(v):
            out["d_" + k] = v - b
    return out

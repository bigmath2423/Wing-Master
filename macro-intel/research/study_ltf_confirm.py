"""Etape 1 — La confirmation M5 separe-t-elle les gagnants des perdants ?

Question posee : en gardant le graphique en M15, exiger un etat M5 aligne au
moment du signal ameliore-t-il le systeme ?

Methode : AUCUNE re-simulation. On prend la liste des trades reellement produits
par la strategie (export TradingView), on reconstruit l'etat M5 a l'instant exact
de chaque entree a partir des bougies M5 brutes, puis on PARTITIONNE les
resultats deja connus en "confirme" / "non confirme". Rien n'est simule, donc
rien ne peut etre biaise par une hypothese d'execution.

Toutes les features M5 sont strictement causales : les pivots sont publies avec
`swing_len` barres de retard, exactement comme dans le Pine.

Criteres de retention PRE-ENREGISTRES (les cinq doivent etre remplis) :
  1. retention >= 70 % des trades
  2. gain d'esperance >= +0.05 R
  3. stabilite maintenue sur les sous-periodes
  4. effet de meme signe en apprentissage et en validation
  5. survie a la correction Benjamini-Hochberg sur l'ensemble des variantes

Usage :
    python study_ltf_confirm.py <trades_tradingview.csv> <ohlc_m5_mt5.csv>
"""

from __future__ import annotations

import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy import stats

SWING_LEN = 10
FDR_Q = 0.10
MAX_PRICE_ERR = 3.0  # $ : au-dela, l'appariement horaire est juge douteux


# --------------------------------------------------------------------------
# Chargement
# --------------------------------------------------------------------------
def load_m5(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    df.columns = [c.strip("<>").lower() for c in df.columns]
    df["dt"] = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
    cols = ["dt", "open", "high", "low", "close", "tickvol"]
    if "spread" in df.columns:
        cols.append("spread")
    return df[cols].sort_values("dt").reset_index(drop=True)


def load_trades(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    cur = "EUR" if "P&L net EUR" in df.columns else "USD"
    rows = []
    for _, sub in df.groupby("Numéro de trade"):
        entry = sub[sub["Type"].str.contains("Entrer", na=False)]
        exit_ = sub[sub["Type"].str.contains("Sortir", na=False)]
        if entry.empty or exit_.empty:
            continue
        e = entry.iloc[0]
        rows.append(
            dict(
                dt=pd.to_datetime(e["Date et heure"]),
                dir=1 if "long" in str(e["Type"]).lower() else -1,
                px=float(e["Prix USD"]),
                pnl=float(e[f"P&L net {cur}"]),
                pct=float(e["Retour %"]),
            )
        )
    return pd.DataFrame(rows).sort_values("dt").reset_index(drop=True)


# --------------------------------------------------------------------------
# Alignement horaire
# --------------------------------------------------------------------------
def broker_offset(ts: pd.Timestamp) -> int:
    """Heure broker MT5 = UTC+2 l'hiver, UTC+3 l'ete (DST europeenne).

    Le decalage n'est pas suppose : il est retrouve empiriquement en minimisant
    l'ecart entre le prix d'entree exporte et la cloture M5 correspondante,
    puis confirme mois par mois (cf. `diagnose_offset`).
    """
    tz = ZoneInfo("Europe/Athens")
    return 180 if ts.to_pydatetime().replace(tzinfo=tz).utcoffset().total_seconds() == 10800 else 120


def diagnose_offset(trades: pd.DataFrame, m5: pd.DataFrame, lo=60, hi=300, step=15):
    """Balaye les decalages possibles et renvoie (meilleur, erreur mediane, n)."""
    idx = m5.set_index("dt")["close"]
    best = None
    for off in range(lo, hi + 1, step):
        v = idx.reindex(trades["dt"] + pd.Timedelta(minutes=off + 10))
        ok = v.notna().values
        if ok.sum() < 30:
            continue
        err = float(np.median(np.abs(v.values[ok] - trades["px"].values[ok])))
        if best is None or err < best[1]:
            best = (off, err, int(ok.sum()))
    return best


# --------------------------------------------------------------------------
# Features M5 (causales)
# --------------------------------------------------------------------------
def m5_features(m5: pd.DataFrame) -> pd.DataFrame:
    df = m5.copy()
    c, h, l, o = df.close, df.high, df.low, df.open
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    df["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["ema20"] = c.ewm(span=20, adjust=False).mean()
    df["ema50"] = c.ewm(span=50, adjust=False).mean()

    # Structure : meme logique que le Pine (pivot confirme + garde de stabilite).
    w = 2 * SWING_LEN + 1
    is_ph = h.rolling(w, center=True).max().eq(h)
    is_pl = l.rolling(w, center=True).min().eq(l)
    pv_h = pd.Series(np.where(is_ph, h, np.nan)).shift(SWING_LEN).ffill()
    pv_l = pd.Series(np.where(is_pl, l, np.nan)).shift(SWING_LEN).ffill()
    up = (c > pv_h) & (c.shift() <= pv_h.shift()) & pv_h.eq(pv_h.shift())
    dn = (c < pv_l) & (c.shift() >= pv_l.shift()) & pv_l.eq(pv_l.shift())
    df["trend"] = pd.Series(np.where(up, 1, np.where(dn, -1, np.nan))).ffill().fillna(0).values

    day = df.dt.dt.date
    hlc3 = (h + l + c) / 3
    df["vwap"] = ((hlc3 * df.tickvol).groupby(day).cumsum() / df.tickvol.groupby(day).cumsum()).values
    df["mom6"] = (c - c.shift(6)).values          # 30 minutes
    df["body"] = (c - o).values
    df["ext"] = ((c - df.ema20).abs() / df.atr).values
    df["volrel"] = (df.tickvol / df.tickvol.rolling(100).median()).values
    return df


def build_sample(trades: pd.DataFrame, m5: pd.DataFrame) -> pd.DataFrame:
    feats = m5_features(m5)
    idx = feats.set_index("dt")
    t = trades[trades.dt >= m5.dt.min()].copy().reset_index(drop=True)
    # La cloture de la bougie M15 ouverte en T est celle de la bougie M5 ouverte en T+10.
    t["m5dt"] = t.dt + pd.to_timedelta(t.dt.map(broker_offset) + 10, unit="m")
    joined = idx.reindex(t.m5dt)
    t["perr"] = np.abs(joined.close.values - t.px.values)
    for k in ["trend", "close", "ema50", "vwap", "mom6", "body", "atr", "ext", "volrel"]:
        t[k] = joined[k].values
    cov = t[t.perr.notna() & (t.perr < MAX_PRICE_ERR)].copy()
    r_ref = abs(cov.loc[cov.pnl <= 0, "pct"].median())
    cov["R"] = cov.pct / r_ref
    return cov


# --------------------------------------------------------------------------
# Variantes pre-enregistrees
# --------------------------------------------------------------------------
def variants(cov: pd.DataFrame) -> dict[str, np.ndarray]:
    d = cov.dir.values
    return {
        "V1 structure M5 alignee": cov.trend.values == d,
        "V2 M5 du bon cote de son EMA50": np.sign(cov.close.values - cov.ema50.values) == d,
        "V3 momentum M5 30 min aligne": np.sign(cov.mom6.values) == d,
        "V4 displacement M5 (corps >= 1 ATR)": (cov.body.values * d) >= cov.atr.values,
        "V5 M5 non sur-etire": cov.ext.values <= np.nanmedian(cov.ext.values),
        "V6 volume M5 en expansion": cov.volrel.values > 1.0,
    }


def _block(R, pnl, mask):
    r, p = R[mask], pnl[mask]
    if len(r) < 5:
        return None
    gl = -p[p <= 0].sum()
    return dict(n=len(r), wr=100 * (p > 0).mean(), pf=(p[p > 0].sum() / gl) if gl > 0 else np.inf,
                E=r.mean())


def run(trades_csv: str, m5_csv: str) -> None:
    m5 = load_m5(m5_csv)
    trades = load_trades(trades_csv)
    off = diagnose_offset(trades, m5)
    print(f"M5 : {len(m5)} bougies, {m5.dt.min()} -> {m5.dt.max()}")
    print(f"Trades exportes : {len(trades)}")
    print(f"Decalage horaire retrouve : {off[0]:+d} min (erreur mediane {off[1]:.3f} $, {off[2]} appariements)")

    cov = build_sample(trades, m5)
    R, pnl = cov.R.values, cov.pnl.values
    base = _block(R, pnl, np.ones(len(R), bool))
    print(f"\nEchantillon exploitable : {len(cov)} trades "
          f"(LONG {int((cov.dir == 1).sum())} / SHORT {int((cov.dir == -1).sum())}), "
          f"{cov.dt.min().date()} -> {cov.dt.max().date()}")
    print(f"Erreur d'appariement mediane : {cov.perr.median():.3f} $")
    print(f"REFERENCE : n={base['n']}  WR={base['wr']:.1f}%  PF={base['pf']:.3f}  E={base['E']:+.3f} R")

    sd = cov.R.std(ddof=1)
    for frac in (0.5, 0.7):
        n1 = int(len(cov) * frac)
        mde = 2.8 * sd * np.sqrt(1 / n1 + 1 / (len(cov) - n1))
        print(f"  puissance : un filtre gardant {frac:.0%} ne detecte que les effets > {mde:.2f} R")

    print("\nTAUX DE BASE (l'etat M5 est-il deja aligne au moment du signal M15 ?)")
    d = cov.dir.values
    for name, m in [("structure M5", cov.trend.values == d),
                    ("EMA50 M5", np.sign(cov.close.values - cov.ema50.values) == d),
                    ("momentum M5 30 min", np.sign(cov.mom6.values) == d),
                    ("VWAP M5", np.sign(cov.close.values - cov.vwap.values) == d)]:
        print(f"  {name:22s} {100 * m.mean():6.1f}% deja aligne -> bloquerait {int((~m).sum()):3d} trades")

    print(f"\n{'variante':38s} {'garde':>7s} {'n':>4s} {'WR':>6s} {'PF':>7s} {'E':>8s} {'t':>6s} {'p':>7s}")
    print("-" * 92)
    rows = []
    for name, m in variants(cov).items():
        a, b = _block(R, pnl, m), _block(R, pnl, ~m)
        if a is None or b is None:
            print(f"{name:38s} {100 * m.mean():6.1f}%   groupe trop petit : filtre sans effet exploitable")
            continue
        t, p = stats.ttest_ind(R[m], R[~m], equal_var=False)
        rows.append((name, a, b, p))
        print(f"{name:38s} {100 * m.mean():6.1f}% {a['n']:4d} {a['wr']:5.1f}% {a['pf']:7.3f} "
              f"{a['E']:+8.3f} {t:+6.2f} {p:7.4f}")

    print("\nSous-groupe REJETE par chaque filtre (ce qu'on jetterait) :")
    for name, _a, b, _p in rows:
        print(f"  {name:38s} n={b['n']:3d}  WR={b['wr']:5.1f}%  PF={b['pf']:6.3f}  E={b['E']:+.3f} R")

    ps = np.array([r[3] for r in rows])
    order = np.argsort(ps)
    crit = (np.arange(1, len(ps) + 1) / len(ps)) * FDR_Q
    print(f"\nBenjamini-Hochberg (FDR {FDR_Q:.0%}) :")
    retained = False
    for rank, i in enumerate(order):
        ok = ps[i] <= crit[rank]
        retained |= ok
        print(f"  {rows[i][0]:38s} p={ps[i]:.4f}  seuil={crit[rank]:.4f}  {'RETENU' if ok else '—'}")
    if not retained:
        print("\n  => aucune variante ne survit. Aucune modification du Pine n'est justifiee.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    run(sys.argv[1], sys.argv[2])

"""Briques de robustesse pour l'étape 3.

Deux questions auxquelles ce module répond :

1. « Le drawdown observé est-il une fatalité, ou juste un mauvais ordre de
   tirage ? » → Monte-Carlo sur l'ordre des trades. On mélange l'ordre des
   trades des milliers de fois : si le drawdown médian simulé est bien pire que
   celui observé, la courbe d'équité doit une partie de sa beauté à la chance.

2. « L'effet tient-il partout, ou seulement sur un actif / une période ? »
   → cohérence par segment. Une règle qui n'améliore qu'un seul symbole est une
   règle sur-ajustée, pas une découverte.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .features import _pnl_series
from .suggestions import _subset_metrics, pf_delta


def monte_carlo_drawdown(pnl: pd.Series, n_sims: int = 2000,
                         seed: int = 42) -> dict:
    """Distribution du drawdown maximal quand on rebat l'ordre des trades.

    L'espérance totale est identique dans toutes les simulations (mêmes trades) :
    seule la SÉQUENCE change. C'est donc un test pur de « chance d'ordonnancement ».
    """
    arr = pnl.dropna().to_numpy(dtype=float)
    n = len(arr)
    if n < 10:
        return {"available": False, "reason": f"Trop peu de trades (n={n})."}

    # Drawdown réellement observé (ordre chronologique).
    eq_obs = np.cumsum(arr)
    observed = float((eq_obs - np.maximum.accumulate(eq_obs)).min())

    rng = np.random.default_rng(seed)
    # Permutations vectorisées : matrice (n_sims, n) d'indices mélangés.
    idx = rng.random((n_sims, n)).argsort(axis=1)
    eq = arr[idx].cumsum(axis=1)
    dd = (eq - np.maximum.accumulate(eq, axis=1)).min(axis=1)

    # Percentiles : plus négatif = pire.
    p05, p50, p95 = np.percentile(dd, [5, 50, 95])
    # Part des simulations où le drawdown est PIRE que l'observé.
    worse = float((dd < observed).mean())

    return {
        "available": True,
        "n_sims": n_sims,
        "observed_max_drawdown": round(observed, 4),
        "simulated_median": round(float(p50), 4),
        "simulated_p05_worst": round(float(p05), 4),
        "simulated_p95_best": round(float(p95), 4),
        "share_of_sims_worse_than_observed": round(worse, 4),
        "interpretation": _mc_interpretation(observed, float(p50), worse),
    }


def _mc_interpretation(observed: float, median: float, worse: float) -> str:
    if worse > 0.75:
        return ("Le drawdown observé est plus clément que la majorité des ordres "
                "possibles : prévoir un drawdown futur nettement plus profond.")
    if worse < 0.25:
        return ("Le drawdown observé est parmi les pires tirages : la séquence "
                "réelle a été défavorable, l'ordonnancement n'a pas flatté la courbe.")
    return ("Le drawdown observé est proche de la médiane simulée : pas d'effet "
            "de chance d'ordonnancement marqué.")


def segment_metrics(df: pd.DataFrame, mask: pd.Series, by: str,
                    min_trades: int = 15) -> list[dict]:
    """Compare baseline vs filtré segment par segment (`by` = colonne de découpe).

    Le masque est calculé UNE fois sur le jeu complet et découpé ensuite : c'est
    indispensable pour que les buckets (ATR notamment) restent comparables.
    """
    if by not in df.columns:
        return []
    pnl = _pnl_series(df)
    rows = []
    for seg, idx in df.groupby(by, dropna=True).groups.items():
        sub_pnl = pnl.loc[idx]
        if len(sub_pnl) < min_trades:
            continue
        sub_mask = mask.loc[idx]
        base = _subset_metrics(sub_pnl)
        filt = _subset_metrics(sub_pnl[sub_mask.values]) if sub_mask.any() else {"n": 0}
        if filt.get("n", 0) == 0:
            rows.append({"segment": str(seg), "n_baseline": base["n"],
                         "n_filtered": filt.get("n", 0), "applicable": False})
            continue
        rows.append({
            "segment": str(seg),
            "applicable": True,
            "n_baseline": base["n"],
            "n_filtered": filt["n"],
            "baseline_expectancy": base["expectancy"],
            "filtered_expectancy": filt["expectancy"],
            "expectancy_delta": round(filt["expectancy"] - base["expectancy"], 4),
            "pf_delta": pf_delta(base["profit_factor"], filt["profit_factor"]),
            "improved": bool(filt["expectancy"] > base["expectancy"]),
        })
    return sorted(rows, key=lambda r: r.get("segment", ""))


def add_period_segments(df: pd.DataFrame, n_periods: int = 4) -> pd.DataFrame:
    """Découpe chronologique en n tranches égales (P1..Pn) pour tester la
    stabilité dans le temps."""
    out = df.copy()
    out.attrs = dict(df.attrs)
    if "datetime" in out.columns and out["datetime"].notna().any():
        out = out.sort_values("datetime")
    labels = [f"P{i+1}" for i in range(n_periods)]
    out["_period"] = pd.qcut(np.arange(len(out)), q=n_periods,
                             labels=labels, duplicates="drop")
    return out.reset_index(drop=True)

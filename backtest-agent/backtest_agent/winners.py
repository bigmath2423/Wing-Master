"""Analyse des meilleurs trades : quelles configurations, horaires et régimes
de marché produisent le meilleur couple espérance / robustesse.

Point clé : on ne classe JAMAIS uniquement par win rate ou par gain moyen. On
utilise un score qui exige un échantillon suffisant (pénalité petit N) afin de
ne pas remonter des « pépites » qui ne sont que du bruit.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

from .features import (
    bucketize, condition_impact, all_condition_columns, is_boolean_like,
    as_bool, _pnl_series,
)

MIN_SAMPLE = 8


def _robust_score(expectancy: float, n: int, min_sample: int = MIN_SAMPLE) -> float:
    """Espérance ajustée du risque d'échantillon. sqrt(n) récompense la taille
    d'échantillon avec des rendements décroissants ; en dessous de min_sample on
    applique une forte décote."""
    if n <= 0:
        return float("-inf")
    penalty = min(1.0, n / min_sample)
    return round(expectancy * np.sqrt(n) * penalty, 4)


def _rank_single_conditions(df: pd.DataFrame) -> list[dict]:
    rows = []
    for col in all_condition_columns(df):
        if col not in df.columns:
            continue
        for r in condition_impact(df, col):
            if r["n_trades"] < MIN_SAMPLE:
                continue
            r = dict(r)
            r["robust_score"] = _robust_score(r["expectancy"], r["n_trades"])
            rows.append(r)
    return sorted(rows, key=lambda r: r["robust_score"], reverse=True)[:15]


def _rank_combos(df: pd.DataFrame, max_flags: int = 3) -> list[dict]:
    """Teste les combinaisons de conditions booléennes (OB & FVG & sweep...)."""
    bool_cols = [c for c in df.attrs.get("conditions", [])
                 if c in df.columns and is_boolean_like(df[c])]
    if not bool_cols:
        return []
    flags = {c: as_bool(df[c]) for c in bool_cols}
    pnl = _pnl_series(df)
    results = []
    for k in range(1, min(max_flags, len(bool_cols)) + 1):
        for combo in combinations(bool_cols, k):
            mask = np.logical_and.reduce([flags[c].values for c in combo])
            n = int(mask.sum())
            if n < MIN_SAMPLE:
                continue
            sub_pnl = pnl[mask]
            gp = sub_pnl[sub_pnl > 0].sum()
            gl = -sub_pnl[sub_pnl < 0].sum()
            pf = (gp / gl) if gl > 0 else float("inf")
            exp = float(sub_pnl.mean())
            results.append({
                "filters": " & ".join(combo),
                "n_trades": n,
                "win_rate": round(float((sub_pnl > 0).mean()), 4),
                "profit_factor": round(pf, 4) if np.isfinite(pf) else None,
                "expectancy": round(exp, 4),
                "robust_score": _robust_score(exp, n),
            })
    return sorted(results, key=lambda r: r["robust_score"], reverse=True)[:12]


def _best_rr(df: pd.DataFrame) -> dict:
    """Meilleur ratio risque/rendement réalisé (en R) parmi les setups."""
    if "pnl_r" not in df.columns or df["pnl_r"].notna().sum() == 0:
        return {"available": False}
    winners = df[df["result"] == "WIN"]
    return {
        "available": True,
        "avg_realized_r_all": round(float(df["pnl_r"].mean()), 4),
        "avg_realized_r_winners": round(float(winners["pnl_r"].mean()), 4) if len(winners) else None,
        "max_realized_r": round(float(df["pnl_r"].max()), 4),
    }


def analyze_winners(df: pd.DataFrame) -> dict:
    df = bucketize(df)
    winners = df[df["result"] == "WIN"]
    return {
        "n_wins": int(len(winners)),
        "best_single_conditions": _rank_single_conditions(df),
        "best_filter_combinations": _rank_combos(df),
        "best_sessions": [r for r in condition_impact(df, "_session")
                          if r["n_trades"] >= MIN_SAMPLE] if "_session" in df else [],
        "best_hours": [r for r in condition_impact(df, "_hour")
                       if r["n_trades"] >= MIN_SAMPLE] if "_hour" in df else [],
        "risk_reward": _best_rr(df),
        "note": (
            "Classement par 'robust_score' (espérance × √N pénalisée), jamais par "
            "win rate seul. Un score élevé sur peu de trades reste suspect."
        ),
    }

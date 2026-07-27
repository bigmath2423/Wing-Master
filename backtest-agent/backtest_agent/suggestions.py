"""Moteur de suggestions + tests A/B.

Philosophie (non négociable) : on ne propose JAMAIS une modification au seul
motif qu'elle augmente le win rate. Chaque suggestion est évaluée sur un panier
de critères de robustesse, et livrée avec un risque explicite de sur-optimisation.

Le « A/B » réalisé ici est un A/B IN-SAMPLE : on simule l'effet d'un filtre en
comparant les trades qui le respectent (variante B) à l'ensemble (variante A).
C'est une PRÉ-sélection d'hypothèses, pas une preuve. La vraie validation se fait
en re-backtestant hors échantillon (voir README, walk-forward).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .features import (
    bucketize, condition_impact, all_condition_columns, is_boolean_like,
    as_bool, _pnl_series,
)

MIN_SAMPLE_FILTER = 10          # taille min du sous-ensemble après filtre
MIN_RETAINED_RATIO = 0.25       # on refuse de jeter plus de 75% des trades


def _subset_metrics(pnl: pd.Series) -> dict:
    if len(pnl) == 0:
        return {"n": 0}
    gp = pnl[pnl > 0].sum()
    gl = -pnl[pnl < 0].sum()
    pf = (gp / gl) if gl > 0 else float("inf")
    eq = pnl.cumsum()
    dd = float((eq - eq.cummax()).min())
    return {
        "n": int(len(pnl)),
        "win_rate": round(float((pnl > 0).mean()), 4),
        "profit_factor": round(pf, 4) if np.isfinite(pf) else None,
        "expectancy": round(float(pnl.mean()), 4),
        "net_pnl": round(float(pnl.sum()), 4),
        "max_drawdown": round(dd, 4),
    }


def _overfit_risk(n_after: int, n_before: int, effect: float) -> str:
    """Estime le risque de sur-optimisation d'un filtre.
    Basé sur : taille d'échantillon restante, part de trades supprimés,
    amplitude de l'effet (des effets énormes sur peu de trades = suspects)."""
    retained = n_after / n_before if n_before else 0
    if n_after < MIN_SAMPLE_FILTER or retained < MIN_RETAINED_RATIO:
        return "ÉLEVÉ"
    if n_after < 30 or abs(effect) > 1.0:
        return "MOYEN"
    return "FAIBLE"


def _ab_test_filter(df: pd.DataFrame, column: str, keep_modality: str,
                    rationale: str, direction: str) -> dict | None:
    """Construit un test A/B : A = toute la stratégie, B = uniquement les trades
    où `column == keep_modality` (ou != si direction='exclude')."""
    pnl_all = _pnl_series(df)
    if direction == "keep":
        mask = df[column].astype(str) == str(keep_modality)
    else:
        mask = df[column].astype(str) != str(keep_modality)
    n_after = int(mask.sum())
    if n_after < MIN_SAMPLE_FILTER:
        return None

    a = _subset_metrics(pnl_all)
    b = _subset_metrics(pnl_all[mask.values])
    if a.get("profit_factor") is None or b.get("profit_factor") is None:
        return None

    pf_delta = (b["profit_factor"] or 0) - (a["profit_factor"] or 0)
    dd_delta = b["max_drawdown"] - a["max_drawdown"]  # >0 = drawdown amélioré
    exp_delta = b["expectancy"] - a["expectancy"]

    return {
        "problem_detected": rationale,
        "proposed_change": (
            f"{'Conserver uniquement' if direction == 'keep' else 'Exclure'} "
            f"les trades où {column} = {keep_modality}."
        ),
        # Spec réutilisable pour rejouer le filtre hors échantillon (walk-forward).
        "filter_spec": {"column": column, "modality": str(keep_modality),
                        "direction": direction},
        "variant_A_baseline": a,
        "variant_B_filtered": b,
        "expected_result": {
            "profit_factor_delta": round(pf_delta, 4),
            "expectancy_delta": round(exp_delta, 4),
            "drawdown_delta": round(dd_delta, 4),
            "trades_removed": a["n"] - b["n"],
            "trades_retained_ratio": round(n_after / a["n"], 3),
        },
        "overfitting_risk": _overfit_risk(n_after, a["n"], pf_delta),
        "decision_rule": (
            "À retenir seulement si le PF s'améliore ET que le drawdown ne se "
            "dégrade pas ET qu'il reste assez de trades ET que l'effet tient "
            "hors échantillon."
        ),
    }


def _candidate_filters(df: pd.DataFrame) -> list[tuple]:
    """Génère des candidats (colonne, modalité, justification, sens) à partir
    des données : conditions perdantes à exclure, conditions gagnantes à garder."""
    candidates = []
    for col in all_condition_columns(df):
        if col not in df.columns:
            continue
        impact = [r for r in condition_impact(df, col) if r["n_trades"] >= MIN_SAMPLE_FILTER]
        if len(impact) < 2:
            continue
        best = impact[0]
        worst = impact[-1]
        # Exclure la pire modalité si nettement négative.
        if worst["expectancy"] < 0:
            candidates.append((
                col, worst["modality"],
                f"La modalité {col}={worst['modality']} a une espérance négative "
                f"({worst['expectancy']}) sur {worst['n_trades']} trades.",
                "exclude"))
        # Garder la meilleure modalité si nettement positive et distincte.
        if best["expectancy"] > 0 and best["expectancy"] > 1.5 * max(1e-9, np.mean(
                [r["expectancy"] for r in impact])):
            candidates.append((
                col, best["modality"],
                f"La modalité {col}={best['modality']} concentre la performance "
                f"(espérance {best['expectancy']}, {best['n_trades']} trades).",
                "keep"))
    return candidates


def _parameter_suggestions(df: pd.DataFrame) -> list[dict]:
    """Suggestions de paramètres à balayer (grid), formulées prudemment."""
    suggestions = []
    if {"entry_price", "stop_loss"}.issubset(df.columns):
        suggestions.append({
            "parameter": "Multiplicateur d'ATR pour le stop",
            "why": "Hypothèse de stops trop serrés détectée / à tester.",
            "grid_to_test": "1.0, 1.5, 2.0, 2.5 × ATR",
            "watch": "Profit factor et drawdown, PAS le win rate.",
        })
    if "confidence" in df.columns and df["confidence"].notna().any():
        suggestions.append({
            "parameter": "Seuil minimal de score de confiance",
            "why": "Filtrer les signaux faibles peut stabiliser l'espérance.",
            "grid_to_test": "0.4, 0.5, 0.6, 0.7",
            "watch": "Nombre de trades restants (ne pas descendre trop bas).",
        })
    if "_atr_bucket" in bucketize(df).columns:
        suggestions.append({
            "parameter": "Plage de volatilité autorisée (ATR min/max)",
            "why": "Certains régimes de volatilité semblent défavorables.",
            "grid_to_test": "Exclure le quartile ATR le plus haut / le plus bas.",
            "watch": "Stabilité de l'espérance entre régimes.",
        })
    return suggestions


def build_suggestions(df: pd.DataFrame, max_ab: int = 6) -> dict:
    df = bucketize(df)
    ab_tests = []
    seen = set()
    for col, modality, rationale, direction in _candidate_filters(df):
        key = (col, modality, direction)
        if key in seen:
            continue
        seen.add(key)
        test = _ab_test_filter(df, col, modality, rationale, direction)
        if test:
            ab_tests.append(test)

    # Priorise les A/B robustes : on pondère le gain de PF par la part de trades
    # conservés (un gain obtenu en jetant 95% des trades ne vaut rien) et on
    # applique une décote selon le risque de sur-optimisation. Ainsi une pépite
    # sur 14 trades ne passe jamais devant un effet stable sur 150 trades.
    def score(t):
        risk_factor = {"FAIBLE": 1.0, "MOYEN": 0.5, "ÉLEVÉ": 0.15}[t["overfitting_risk"]]
        retained = t["expected_result"]["trades_retained_ratio"]
        pf_delta = t["expected_result"]["profit_factor_delta"]
        return pf_delta * retained * risk_factor
    ab_tests = sorted(ab_tests, key=score, reverse=True)[:max_ab]

    return {
        "filters_to_test": [
            {"filter": t["proposed_change"], "rationale": t["problem_detected"],
             "overfitting_risk": t["overfitting_risk"]}
            for t in ab_tests
        ],
        "parameters_to_test": _parameter_suggestions(df),
        "ab_tests": ab_tests,
        "guardrails": [
            "Ne jamais retenir une règle uniquement parce qu'elle monte le win rate.",
            "Exiger un minimum de trades après filtrage (>= 30 idéalement).",
            "Valider chaque règle sur une période HORS échantillon (walk-forward).",
            "Préférer des règles qui améliorent PF + drawdown de façon stable.",
            "Refuser les règles qui suppriment plus de ~50% des trades.",
        ],
    }

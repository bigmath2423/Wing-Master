"""Analyse des pertes : pourquoi la stratégie perd, et quelles conditions
reviennent avant les trades perdants.

Approche : on compare la population des trades perdants à la population globale.
Une condition « suspecte » est une condition sur-représentée chez les perdants
ET associée à une espérance négative, avec un échantillon suffisant.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .features import (
    bucketize, condition_impact, all_condition_columns, _pnl_series,
)

MIN_SAMPLE = 5  # on n'accuse jamais une condition sur trop peu de trades


def _lift_table(df: pd.DataFrame) -> list[dict]:
    """Pour chaque (colonne, modalité), calcule le 'lift' de perte :
    P(condition | perte) / P(condition | global). Un lift > 1 signifie que la
    condition est plus fréquente chez les perdants."""
    losers = df[df["result"] == "LOSS"]
    if losers.empty:
        return []
    base_n = len(df)
    lose_n = len(losers)
    rows = []
    for col in all_condition_columns(df):
        if col not in df.columns:
            continue
        global_freq = df[col].value_counts(normalize=True, dropna=True)
        lose_freq = losers[col].value_counts(normalize=True, dropna=True)
        for modality, lf in lose_freq.items():
            gf = float(global_freq.get(modality, 0.0))
            if gf == 0:
                continue
            support = int((losers[col] == modality).sum())
            if support < MIN_SAMPLE:
                continue
            lift = lf / gf
            # Espérance de cette modalité sur l'ensemble des trades.
            sub = df[df[col] == modality]
            exp = float(_pnl_series(sub).mean())
            rows.append({
                "column": col,
                "modality": str(modality),
                "loss_lift": round(float(lift), 3),
                "n_in_losers": support,
                "share_of_losers": round(float(lf), 3),
                "expectancy_when_present": round(exp, 4),
            })
    # On remonte les conditions les plus sur-représentées ET perdantes.
    rows = [r for r in rows if r["loss_lift"] > 1.05 and r["expectancy_when_present"] < 0]
    return sorted(rows, key=lambda r: (r["loss_lift"], -r["expectancy_when_present"]),
                  reverse=True)


def _structural_flags(df: pd.DataFrame) -> list[str]:
    """Signaux structurels calculables : mauvais placement de stop, entrée tardive,
    volatilité extrême. Heuristiques prudentes, formulées comme des hypothèses."""
    flags = []
    pnl = _pnl_series(df)
    losers = df[df["result"] == "LOSS"]

    # Stop trop serré : les perdants ont un risque (entry-stop) bien plus faible
    # que les gagnants -> stop probablement dans le bruit.
    if {"entry_price", "stop_loss"}.issubset(df.columns):
        risk = (df["entry_price"] - df["stop_loss"]).abs()
        if risk.notna().any():
            rl = risk[df["result"] == "LOSS"].mean()
            rw = risk[df["result"] == "WIN"].mean()
            if pd.notna(rl) and pd.notna(rw) and rw > 0 and rl < 0.6 * rw:
                flags.append(
                    "Le risque moyen (distance entrée→stop) des trades perdants "
                    f"est {rl/rw:.0%} de celui des gagnants : hypothèse de stops "
                    "trop serrés placés dans le bruit de marché.")

    # Entrée tardive : si une colonne de type 'distance au signal' existe on la
    # regarde ; sinon on approxime via la durée (perdants très courts = stop pris
    # immédiatement).
    if "duration_min" in df.columns and df["duration_min"].notna().any():
        dl = df.loc[df["result"] == "LOSS", "duration_min"].median()
        dw = df.loc[df["result"] == "WIN", "duration_min"].median()
        if pd.notna(dl) and pd.notna(dw) and dw > 0 and dl < 0.4 * dw:
            flags.append(
                "Les trades perdants sont stoppés très vite (durée médiane "
                f"{dl:.0f} min contre {dw:.0f} min pour les gagnants) : hypothèse "
                "d'entrées trop tardives / dans une zone déjà étendue.")

    # Volatilité extrême : buckets ATR les plus hauts avec espérance négative.
    if "_atr_bucket" in df.columns:
        atr_impact = condition_impact(df, "_atr_bucket")
        if atr_impact:
            worst = min(atr_impact, key=lambda r: r["expectancy"])
            if worst["expectancy"] < 0 and worst["n_trades"] >= MIN_SAMPLE:
                flags.append(
                    f"Le régime de volatilité '{worst['modality']}' (ATR) montre "
                    f"une espérance négative ({worst['expectancy']}) sur "
                    f"{worst['n_trades']} trades : hypothèse de volatilité "
                    "défavorable à ce setup.")

    if len(losers) and float((_pnl_series(losers)).min()) < 3 * float(pnl.std(ddof=1) or 1):
        pass  # placeholder volontairement neutre

    return flags


def analyze_losses(df: pd.DataFrame) -> dict:
    df = bucketize(df)
    losers = df[df["result"] == "LOSS"]
    return {
        "n_losses": int(len(losers)),
        "recurring_conditions_before_losses": _lift_table(df),
        "structural_hypotheses": _structural_flags(df),
        "loss_by_session": condition_impact(df, "_session") if "_session" in df else [],
        "loss_by_confidence": condition_impact(df, "_conf_bucket") if "_conf_bucket" in df else [],
        "note": (
            "Les 'conditions récurrentes' sont des corrélations, pas des causes. "
            "Chaque hypothèse doit être validée en A/B et hors échantillon avant "
            "toute modification de l'indicateur."
        ),
    }

"""Outils partagés pour transformer les conditions de marché en variables
analysables (buckets d'ATR, tranches horaires, buckets de confiance) et pour
mesurer l'impact d'une condition sur la performance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _pnl_series(df: pd.DataFrame) -> pd.Series:
    if "pnl_r" in df.columns and df["pnl_r"].notna().any():
        return df["pnl_r"].fillna(0.0)
    return df["pnl"].fillna(0.0)


def is_boolean_like(series: pd.Series) -> bool:
    vals = set(str(v).strip().lower() for v in series.dropna().unique())
    return vals.issubset({"true", "false", "1", "0", "yes", "no", "oui", "non",
                          "1.0", "0.0", ""})


def as_bool(series: pd.Series) -> pd.Series:
    truthy = {"true", "1", "yes", "oui", "1.0"}
    return series.map(lambda v: str(v).strip().lower() in truthy)


def bucketize(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute des colonnes dérivées utiles à la segmentation."""
    out = df.copy()
    if "datetime" in out.columns and out["datetime"].notna().any():
        out["_hour"] = out["datetime"].dt.hour
        out["_dow"] = out["datetime"].dt.day_name()
        out["_session"] = out["_hour"].map(_session_of_hour)
    if "confidence" in out.columns and out["confidence"].notna().any():
        out["_conf_bucket"] = pd.cut(
            out["confidence"], bins=[-0.01, 0.25, 0.5, 0.75, 1.01],
            labels=["0-25%", "25-50%", "50-75%", "75-100%"])
    # ATR / volatilité : cherche une colonne condition contenant 'atr' numérique.
    for col in df.attrs.get("conditions", []):
        if "atr" in col.lower():
            num = pd.to_numeric(out[col], errors="coerce")
            if num.notna().any():
                out["_atr_bucket"] = pd.qcut(num, q=min(4, num.nunique()),
                                             duplicates="drop")
            break
    return out


def _session_of_hour(h: int) -> str:
    # Sessions en UTC (approximation classique).
    if 0 <= h < 7:
        return "Asie"
    if 7 <= h < 12:
        return "Londres"
    if 12 <= h < 16:
        return "Londres/NY overlap"
    if 16 <= h < 21:
        return "New York"
    return "After-hours"


def condition_impact(df: pd.DataFrame, column: str) -> list[dict]:
    """Pour une colonne catégorielle/booléenne, retourne la performance par
    modalité : nb de trades, win rate, profit factor, expectancy.

    C'est LA brique qui permet de dire « quand OB=True, le PF passe de X à Y »."""
    pnl = _pnl_series(df)
    work = pd.DataFrame({"val": df[column], "pnl": pnl,
                         "win": df["result"].eq("WIN")})
    work = work.dropna(subset=["val"])
    rows = []
    for modality, grp in work.groupby("val", dropna=True):
        gp = grp["pnl"][grp["pnl"] > 0].sum()
        gl = -grp["pnl"][grp["pnl"] < 0].sum()
        pf = (gp / gl) if gl > 0 else float("inf")
        rows.append({
            "column": column,
            "modality": str(modality),
            "n_trades": int(len(grp)),
            "win_rate": round(float(grp["win"].mean()), 4),
            "profit_factor": round(pf, 4) if np.isfinite(pf) else None,
            "expectancy": round(float(grp["pnl"].mean()), 4),
            "net_pnl": round(float(grp["pnl"].sum()), 4),
        })
    return sorted(rows, key=lambda r: r["expectancy"], reverse=True)


def all_condition_columns(df: pd.DataFrame) -> list[str]:
    """Colonnes de conditions détectées + colonnes dérivées de segmentation."""
    base = list(df.attrs.get("conditions", []))
    derived = [c for c in ["_hour", "_session", "_dow", "_conf_bucket",
                           "_atr_bucket", "direction", "timeframe", "symbol"]
               if c in df.columns]
    # On retire les ATR numériques bruts (remplacés par _atr_bucket).
    return derived + base

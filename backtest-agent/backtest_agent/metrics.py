"""Analyse globale : les chiffres « santé » d'une stratégie.

Toutes les métriques sont calculées de façon déterministe. On privilégie des
définitions standards de l'industrie pour éviter toute ambiguïté.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

import numpy as np
import pandas as pd


def _pnl_series(df: pd.DataFrame) -> pd.Series:
    """Retourne la série de PnL utilisée pour les calculs. On préfère le PnL en R
    (comparable entre actifs) s'il existe, sinon le PnL en devise."""
    if "pnl_r" in df.columns and df["pnl_r"].notna().any():
        return df["pnl_r"].fillna(0.0)
    if "pnl" in df.columns and df["pnl"].notna().any():
        return df["pnl"].fillna(0.0)
    raise ValueError("Aucune colonne de PnL exploitable (ni pnl_r ni pnl).")


def _max_drawdown(equity: pd.Series) -> tuple[float, float]:
    """Retourne (drawdown_absolu_max, drawdown_relatif_max) sur la courbe d'équité."""
    running_max = equity.cummax()
    abs_dd = (equity - running_max)
    max_abs_dd = float(abs_dd.min()) if len(abs_dd) else 0.0
    # Drawdown relatif : évite la division par des pics <= 0.
    denom = running_max.replace(0, np.nan)
    rel_dd = (abs_dd / denom).replace([np.inf, -np.inf], np.nan)
    max_rel_dd = float(rel_dd.min()) if rel_dd.notna().any() else 0.0
    return max_abs_dd, max_rel_dd


def _consistency(df: pd.DataFrame, pnl: pd.Series) -> dict[str, Any]:
    """Mesure la régularité des résultats période par période (mensuel)."""
    if "datetime" not in df.columns or df["datetime"].notna().sum() < 2:
        return {"available": False}
    tmp = pd.DataFrame({"dt": df["datetime"], "pnl": pnl.values})
    tmp = tmp.dropna(subset=["dt"])
    monthly = tmp.groupby(tmp["dt"].dt.to_period("M"))["pnl"].sum()
    if monthly.empty:
        return {"available": False}
    profitable = (monthly > 0).mean()
    return {
        "available": True,
        "periods": int(len(monthly)),
        "profitable_period_ratio": round(float(profitable), 4),
        "period_pnl_mean": round(float(monthly.mean()), 4),
        "period_pnl_std": round(float(monthly.std(ddof=1)) if len(monthly) > 1 else 0.0, 4),
        "worst_period": round(float(monthly.min()), 4),
        "best_period": round(float(monthly.max()), 4),
        "monthly_breakdown": {str(k): round(float(v), 4) for k, v in monthly.items()},
    }


@dataclass
class GlobalMetrics:
    n_trades: int
    n_wins: int
    n_losses: int
    n_breakeven: int
    win_rate: float
    profit_factor: float
    expectancy: float           # PnL moyen par trade
    payoff_ratio: float         # gain moyen / perte moyenne (valeur absolue)
    avg_win: float
    avg_loss: float
    gross_profit: float
    gross_loss: float
    net_pnl: float
    max_drawdown_abs: float
    max_drawdown_rel: float
    sharpe_like: float          # PnL moyen / écart-type des PnL (par trade)
    largest_win: float
    largest_loss: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    pnl_unit: str
    consistency: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def _max_streak(results: pd.Series, target: str) -> int:
    best = cur = 0
    for r in results:
        if r == target:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def global_metrics(df: pd.DataFrame) -> GlobalMetrics:
    pnl = _pnl_series(df)
    unit = "R" if ("pnl_r" in df.columns and df["pnl_r"].notna().any()) else "devise"

    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    n = len(df)

    gross_profit = float(wins.sum())
    gross_loss = float(-losses.sum())  # positif
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    avg_win = float(wins.mean()) if len(wins) else 0.0
    avg_loss = float(losses.mean()) if len(losses) else 0.0  # négatif
    payoff = (avg_win / abs(avg_loss)) if avg_loss != 0 else float("inf")

    equity = pnl.cumsum()
    dd_abs, dd_rel = _max_drawdown(equity)

    std = float(pnl.std(ddof=1)) if n > 1 else 0.0
    sharpe_like = (float(pnl.mean()) / std) if std > 0 else 0.0

    results = df["result"] if "result" in df.columns else pd.Series(
        np.where(pnl > 0, "WIN", np.where(pnl < 0, "LOSS", "BE")))

    return GlobalMetrics(
        n_trades=n,
        n_wins=int((results == "WIN").sum()),
        n_losses=int((results == "LOSS").sum()),
        n_breakeven=int((results == "BE").sum()),
        win_rate=round(float((results == "WIN").mean()), 4),
        profit_factor=round(profit_factor, 4) if np.isfinite(profit_factor) else float("inf"),
        expectancy=round(float(pnl.mean()), 4),
        payoff_ratio=round(payoff, 4) if np.isfinite(payoff) else float("inf"),
        avg_win=round(avg_win, 4),
        avg_loss=round(avg_loss, 4),
        gross_profit=round(gross_profit, 4),
        gross_loss=round(gross_loss, 4),
        net_pnl=round(float(pnl.sum()), 4),
        max_drawdown_abs=round(dd_abs, 4),
        max_drawdown_rel=round(dd_rel, 4),
        sharpe_like=round(sharpe_like, 4),
        largest_win=round(float(pnl.max()), 4),
        largest_loss=round(float(pnl.min()), 4),
        max_consecutive_wins=_max_streak(results, "WIN"),
        max_consecutive_losses=_max_streak(results, "LOSS"),
        pnl_unit=unit,
        consistency=_consistency(df, pnl),
    )

"""Fixtures partagées.

On construit des jeux de données DÉTERMINISTES avec une structure connue, pour
pouvoir affirmer des choses vraies : « l'agent doit trouver que la condition X
est perdante », et pas seulement « le code ne plante pas ».
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from backtest_agent.ingest import normalize


def _rows(n: int = 120, start: datetime | None = None) -> list[dict]:
    """Jeu structuré : quand `bad_ctx` est vrai le trade perd, sinon il gagne.

    Un signal aussi net doit être retrouvé par l'analyse : c'est le but.
    """
    start = start or datetime(2025, 1, 1, 9, 0)
    rows = []
    for i in range(n):
        dt = start + timedelta(hours=6 * i)
        bad_ctx = (i % 3 == 0)          # 1 trade sur 3 en mauvais contexte
        win = not bad_ctx
        entry = 100.0
        stop = 98.0                      # risque = 2
        rows.append({
            "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": "BTCUSDT" if i % 2 == 0 else "ETHUSDT",
            "timeframe": "15m",
            "direction": "BUY",
            "entry_price": entry,
            "stop_loss": stop,
            "take_profit": 104.0,
            "exit_price": 104.0 if win else 98.0,
            "result": "WIN" if win else "LOSS",
            "duration_min": 120 if win else 20,
            "confidence": 80 if win else 30,
            "bad_ctx": bad_ctx,
            "good_setup": not bad_ctx,
        })
    return rows


@pytest.fixture
def structured_df() -> pd.DataFrame:
    """DataFrame normalisé avec une structure connue et exploitable."""
    return normalize(pd.DataFrame(_rows()))


@pytest.fixture
def structured_csv(tmp_path) -> str:
    path = tmp_path / "trades.csv"
    pd.DataFrame(_rows()).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def minimal_df() -> pd.DataFrame:
    """Le strict minimum : date, sens, PnL. Ni result, ni conditions."""
    rows = [{"time": f"2025-02-{d:02d} 10:00", "side": "buy",
             "profit": 1.0 if d % 2 else -0.5} for d in range(1, 25)]
    return normalize(pd.DataFrame(rows))

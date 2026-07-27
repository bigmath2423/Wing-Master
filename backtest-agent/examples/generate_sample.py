"""Génère un CSV de backtest réaliste pour tester l'agent sans données réelles.

Les conditions ne sont pas indépendantes du résultat : on injecte volontairement
des structures (ex : les trades en forte volatilité + sans confirmation VWAP
perdent plus) pour que l'analyse ait quelque chose à trouver.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
TF = "15m"


def _make_trade(dt: datetime) -> dict:
    direction = random.choice(["BUY", "SELL"])
    atr = round(random.uniform(50, 400), 1)
    ob = random.random() < 0.45
    fvg = random.random() < 0.40
    sweep = random.random() < 0.35
    vwap_up = random.random() < 0.55
    structure_up = random.random() < 0.6
    confidence = random.randint(20, 95)
    hour = dt.hour

    # Probabilité de gain : construite pour créer des signaux exploitables.
    p = 0.42
    if ob and sweep:
        p += 0.18                      # bon setup
    if fvg:
        p += 0.05
    if (direction == "BUY") == vwap_up:
        p += 0.08                      # aligné au VWAP
    if atr > 300:
        p -= 0.15                      # forte volatilité défavorable
    if confidence >= 70:
        p += 0.10
    if 12 <= hour < 16:
        p += 0.07                      # overlap Londres/NY favorable
    if 0 <= hour < 7:
        p -= 0.08                      # session asiatique moins bonne ici
    p = max(0.05, min(0.9, p))

    win = random.random() < p
    entry = round(random.uniform(20000, 60000), 1)
    risk = atr * 1.5
    reward = atr * 3.0
    if direction == "BUY":
        stop = round(entry - risk, 1)
        tp = round(entry + reward, 1)
        exit_price = tp if win else stop
    else:
        stop = round(entry + risk, 1)
        tp = round(entry - reward, 1)
        exit_price = tp if win else stop

    pnl_r = 2.0 if win else -1.0
    # bruit léger sur le PnL en R (sorties partielles / slippage).
    pnl_r = round(pnl_r + random.uniform(-0.15, 0.15), 3)

    return {
        "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": random.choice(SYMBOLS),
        "timeframe": TF,
        "direction": direction,
        "entry_price": entry,
        "stop_loss": stop,
        "take_profit": tp,
        "exit_price": exit_price,
        "result": "WIN" if win else "LOSS",
        "pnl_r": pnl_r,
        "duration_min": random.randint(15, 480) if win else random.randint(5, 90),
        "confidence": confidence,
        "ob": ob,
        "fvg": fvg,
        "sweep": sweep,
        "vwap_up": vwap_up,
        "structure_up": structure_up,
        "atr": atr,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=300)
    ap.add_argument("-o", "--out", default=str(Path(__file__).with_name("sample_trades.csv")))
    args = ap.parse_args()

    dt = datetime(2025, 1, 2, 8, 0, 0)
    rows = []
    for _ in range(args.n):
        dt += timedelta(hours=random.uniform(2, 20))
        rows.append(_make_trade(dt))

    out = Path(args.out)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[ok] {len(rows)} trades écrits dans {out}")


if __name__ == "__main__":
    main()

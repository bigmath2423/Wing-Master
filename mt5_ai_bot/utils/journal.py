"""
utils/journal.py
================
Journal des signaux : enregistre chaque analyse dans un CSV pour suivre la
performance dans le temps (logs/signals.csv).

Aucune dépendance externe : écriture CSV via le module standard `csv`.
"""

from __future__ import annotations

import csv
import os
from datetime import datetime

_FIELDS = [
    "datetime", "symbol", "decision", "confidence",
    "entry", "sl", "tp", "lot", "risk_amount", "rr",
    "top_reason",
]


def log_signal(signal, symbol: str, path: str = "logs/signals.csv") -> None:
    """Ajoute une ligne au journal. Crée le fichier + l'en-tête si besoin."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    file_exists = os.path.isfile(path)

    row = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "decision": signal.decision,
        "confidence": round(signal.confidence, 1),
        "entry": signal.entry if signal.entry is not None else "",
        "sl": signal.sl if signal.sl is not None else "",
        "tp": signal.tp if signal.tp is not None else "",
        "lot": signal.lot if signal.lot is not None else "",
        "risk_amount": signal.risk_amount if signal.risk_amount is not None else "",
        "rr": signal.rr if signal.rr is not None else "",
        "top_reason": signal.reasons[0] if signal.reasons else "",
    }

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

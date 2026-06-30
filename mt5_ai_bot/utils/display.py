"""
utils/display.py
================
Affichage propre du signal de trading dans la console.
"""

from __future__ import annotations

from datetime import datetime


_COLORS = {
    "BUY": "\033[92m",      # vert
    "SELL": "\033[91m",     # rouge
    "NO TRADE": "\033[93m", # jaune
}
_RESET = "\033[0m"


def _c(text: str, decision: str) -> str:
    return f"{_COLORS.get(decision, '')}{text}{_RESET}"


def print_signal(signal, symbol: str, max_reasons: int = 8) -> None:
    """Affiche le signal final de façon lisible."""
    d = signal.decision
    line = "=" * 56
    print("\n" + line)
    print(f"  SIGNAL {symbol}   {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(line)
    print(f"  DÉCISION       : {_c(d, d)}")
    print(f"  CONFIANCE      : {signal.confidence:.0f}%")

    if d in ("BUY", "SELL"):
        print(f"  ENTRÉE         : {signal.entry}")
        print(f"  STOP LOSS      : {signal.sl}")
        print(f"  TAKE PROFIT    : {signal.tp}")
        print(f"  LOT            : {signal.lot}")
        print(f"  RISQUE         : {signal.risk_amount}$  (RR {signal.rr:.1f})")

    print("  RAISON DU TRADE:")
    for r in signal.reasons[:max_reasons]:
        print(f"     - {r}")
    print(line + "\n")


def print_opinions(opinions) -> None:
    """Affiche le détail de chaque agent (debug / transparence)."""
    print("  Détail des agents :")
    for op in opinions:
        print(f"     • {op.name:10s} -> {op.bias:8s} (score {op.score:.0f})")

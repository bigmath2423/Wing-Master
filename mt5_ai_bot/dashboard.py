"""
dashboard.py
============
Tableau de bord en console : lit le journal des signaux (logs/signals.csv)
et affiche un résumé de l'activité du bot.

Lancement :
    python dashboard.py

Aucune dépendance externe (module csv standard).
"""

from __future__ import annotations

import csv
import os

import config


def _load_rows(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def show_dashboard(path: str | None = None) -> None:
    path = path or config.JOURNAL_PATH
    rows = _load_rows(path)

    line = "=" * 60
    print("\n" + line)
    print("  TABLEAU DE BORD — MT5 AI Trading Bot")
    print(line)

    if not rows:
        print(f"  Aucun signal enregistré ({path} introuvable ou vide).")
        print("  Lance d'abord le bot : python main.py")
        print(line + "\n")
        return

    total = len(rows)
    counts = {"BUY": 0, "SELL": 0, "NO TRADE": 0}
    confidences = []
    tradable_conf = []

    for r in rows:
        dec = r.get("decision", "NO TRADE")
        counts[dec] = counts.get(dec, 0) + 1
        c = _to_float(r.get("confidence"))
        if c is not None:
            confidences.append(c)
            if dec in ("BUY", "SELL"):
                tradable_conf.append(c)

    signals = counts.get("BUY", 0) + counts.get("SELL", 0)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    avg_trade_conf = sum(tradable_conf) / len(tradable_conf) if tradable_conf else 0

    print(f"  Fichier             : {path}")
    print(f"  Analyses totales    : {total}")
    print(f"  Signaux tradables   : {signals}  "
          f"({counts.get('BUY',0)} BUY / {counts.get('SELL',0)} SELL)")
    print(f"  NO TRADE            : {counts.get('NO TRADE',0)}")
    print(f"  Confiance moyenne   : {avg_conf:.1f}%  (tous)")
    print(f"  Confiance moyenne   : {avg_trade_conf:.1f}%  (signaux tradables)")

    # Barre visuelle BUY / SELL / NO TRADE
    print("\n  Répartition :")
    for dec in ("BUY", "SELL", "NO TRADE"):
        n = counts.get(dec, 0)
        pct = (n / total * 100) if total else 0
        bar = "█" * int(pct / 4)
        print(f"    {dec:9s} {n:4d}  {pct:5.1f}% {bar}")

    print("\n  Derniers signaux :")
    print("    " + "-" * 54)
    for r in rows[-8:]:
        dec = r.get("decision", "")
        conf = r.get("confidence", "")
        entry = r.get("entry", "") or "-"
        sl = r.get("sl", "") or "-"
        tp = r.get("tp", "") or "-"
        dt = r.get("datetime", "")
        print(f"    {dt}  {dec:8s} conf {conf:>5}%  E:{entry} SL:{sl} TP:{tp}")

    print(line + "\n")


if __name__ == "__main__":
    show_dashboard()

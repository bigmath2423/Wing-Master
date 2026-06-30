"""
agents/execution_agent.py
=========================
Agent d'exécution MT5.

Sécurités IMPORTANTES (par défaut, le bot N'EXÉCUTE RIEN) :
1. config.AUTO_TRADE doit valoir True.
2. config.DEMO_ONLY = True empêche tout ordre sur un compte réel.
3. Le compte doit être détecté comme DÉMO par MT5.

Tant que ces conditions ne sont pas réunies, l'agent se contente de logguer
qu'il aurait envoyé l'ordre, sans rien faire.
"""

from __future__ import annotations

from .decision_agent import TradeSignal


class ExecutionAgent:
    name = "Exécution"

    def __init__(self, config, client):
        self.config = config
        self.client = client

    def execute(self, signal: TradeSignal) -> dict:
        cfg = self.config

        if signal.decision not in ("BUY", "SELL"):
            return {"executed": False, "reason": "Pas de trade à exécuter."}

        if not cfg.AUTO_TRADE:
            return {
                "executed": False,
                "reason": "AUTO_TRADE=False : signal affiché uniquement (aucun ordre envoyé).",
            }

        # Garde-fou compte démo
        if cfg.DEMO_ONLY and not self.client.is_demo():
            return {
                "executed": False,
                "reason": "DEMO_ONLY=True mais le compte n'est pas un compte démo. Ordre bloqué.",
            }

        result = self.client.send_order(
            direction=signal.decision,
            lot=signal.lot,
            sl=signal.sl,
            tp=signal.tp,
        )
        return {
            "executed": bool(result.get("ok")),
            "reason": result.get("reason"),
            "ticket": result.get("ticket"),
        }

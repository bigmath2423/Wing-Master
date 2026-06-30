"""
agents/risk_agent.py
====================
Agent de gestion du risque.

À partir d'une direction (BUY/SELL) et des données de marché, il calcule :
- le stop loss (basé sur l'ATR + structure, pour éviter les mèches)
- le take profit (selon le ratio risque/récompense visé)
- la taille de lot pour ne risquer QUE `RISK_PER_TRADE` du capital (1% par défaut)

Le calcul du lot utilise la valeur du tick fournie par MT5, donc reste correct
pour XAUUSD quel que soit le broker.
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent
from core import indicators as ind


class RiskAgent(BaseAgent):
    name = "Risque"

    def compute(self, direction: str, market: dict, client) -> dict:
        """Retourne un dict { entry, sl, tp, lot, risk_amount, rr } ou None."""
        cfg = self.config
        if direction not in ("BUY", "SELL"):
            return None

        df = market.get(cfg.ENTRY_TIMEFRAME)
        if df is None or len(df) < cfg.ATR_PERIOD + 2:
            return None

        tick = client.get_tick()
        entry = tick["ask"] if direction == "BUY" else tick["bid"]

        atr = float(ind.atr(df, cfg.ATR_PERIOD).iloc[-1])
        sl_distance = atr * cfg.SL_ATR_MULTIPLIER
        if sl_distance <= 0:
            return None

        if direction == "BUY":
            sl = entry - sl_distance
            tp = entry + sl_distance * cfg.RISK_REWARD_RATIO
        else:
            sl = entry + sl_distance
            tp = entry - sl_distance * cfg.RISK_REWARD_RATIO

        # --- Taille de lot pour risquer 1% du capital ---
        balance = client.get_balance()
        risk_amount = balance * cfg.RISK_PER_TRADE

        si = client.get_symbol_info()
        tick_size = si["trade_tick_size"] or si["point"]
        tick_value = si["trade_tick_value"] or 1.0

        # Perte pour 1 lot si le SL est touché
        ticks_to_sl = sl_distance / tick_size
        loss_per_lot = ticks_to_sl * tick_value
        if loss_per_lot <= 0:
            return None

        raw_lot = risk_amount / loss_per_lot
        lot = self._normalize_lot(raw_lot, si)

        digits = si["digits"]
        return {
            "entry": round(entry, digits),
            "sl": round(sl, digits),
            "tp": round(tp, digits),
            "lot": lot,
            "risk_amount": round(risk_amount, 2),
            "rr": cfg.RISK_REWARD_RATIO,
            "atr": round(atr, digits),
        }

    def _normalize_lot(self, lot: float, si: dict) -> float:
        """Arrondit le lot au pas du broker et applique les bornes config."""
        cfg = self.config
        step = si["volume_step"] or 0.01
        lot = round(round(lot / step) * step, 2)
        lot = max(lot, cfg.MIN_LOT, si["volume_min"])
        lot = min(lot, cfg.MAX_LOT, si["volume_max"])
        return round(lot, 2)

    # Conformité à l'interface BaseAgent (non utilisée : le risk agent est
    # appelé via compute() une fois la direction connue).
    def analyze(self, market: dict) -> AgentOpinion:  # pragma: no cover
        return AgentOpinion(name=self.name, bias="NEUTRAL")

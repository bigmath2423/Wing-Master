"""
agents/technical_agent.py
=========================
Agent d'analyse technique classique.

Analyse :
- la tendance via EMA 50 / EMA 200 (croisement + position du prix)
- le momentum via RSI (surachat / survente)
- les niveaux de support / résistance

Combine plusieurs timeframes : H1 donne la tendance de fond (poids fort),
M15 la structure, M5 le timing. Le biais final est pondéré.
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent
from core import indicators as ind


class TechnicalAgent(BaseAgent):
    name = "Technique"

    # Poids de chaque timeframe dans le score global
    TF_WEIGHTS = {"H1": 0.5, "M15": 0.3, "M5": 0.2}

    def analyze(self, market: dict) -> AgentOpinion:
        op = AgentOpinion(name=self.name)
        cfg = self.config

        weighted_bias = 0.0   # >0 haussier, <0 baissier
        total_weight = 0.0

        for tf, df in market.items():
            if df is None or len(df) < cfg.EMA_SLOW + 5:
                continue
            weight = self.TF_WEIGHTS.get(tf, 0.2)
            total_weight += weight

            ema_fast = ind.ema(df["close"], cfg.EMA_FAST)
            ema_slow = ind.ema(df["close"], cfg.EMA_SLOW)
            rsi = ind.rsi(df["close"], cfg.RSI_PERIOD)

            price = float(df["close"].iloc[-1])
            ef = float(ema_fast.iloc[-1])
            es = float(ema_slow.iloc[-1])
            r = float(rsi.iloc[-1])

            tf_bias = 0.0

            # --- Tendance via EMA ---
            if ef > es and price > ef:
                tf_bias += 1.0
                op.add(f"{tf}: tendance haussière (EMA{cfg.EMA_FAST}>EMA{cfg.EMA_SLOW}, prix au-dessus)")
            elif ef < es and price < ef:
                tf_bias -= 1.0
                op.add(f"{tf}: tendance baissière (EMA{cfg.EMA_FAST}<EMA{cfg.EMA_SLOW}, prix en-dessous)")
            else:
                op.add(f"{tf}: tendance indécise (prix proche des EMA)")

            # --- Momentum via RSI ---
            if r >= cfg.RSI_OVERBOUGHT:
                tf_bias -= 0.5
                op.add(f"{tf}: RSI {r:.0f} en surachat")
            elif r <= cfg.RSI_OVERSOLD:
                tf_bias += 0.5
                op.add(f"{tf}: RSI {r:.0f} en survente")
            elif r > 50:
                tf_bias += 0.25
            else:
                tf_bias -= 0.25

            weighted_bias += tf_bias * weight

        # --- Support / résistance sur le timeframe d'entrée ---
        entry_df = market.get(cfg.ENTRY_TIMEFRAME)
        if entry_df is not None and len(entry_df) > cfg.SWING_LOOKBACK:
            support, resistance = ind.support_resistance(entry_df, cfg.SWING_LOOKBACK)
            op.data["support"] = support
            op.data["resistance"] = resistance
            op.add(f"Support ~{support:.2f} / Résistance ~{resistance:.2f}")

        if total_weight == 0:
            return op  # pas assez de données

        # Normalise le biais (-1.5..1.5 environ) vers un score 0..100
        norm = max(-1.0, min(1.0, weighted_bias / total_weight / 1.5))
        op.score = abs(norm) * 100
        if norm > 0.15:
            op.bias = "BUY"
        elif norm < -0.15:
            op.bias = "SELL"
        else:
            op.bias = "NEUTRAL"

        return op

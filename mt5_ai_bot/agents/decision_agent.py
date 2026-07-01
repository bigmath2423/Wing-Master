"""
agents/decision_agent.py
========================
Agent de décision : c'est le "chef d'orchestre".

Il agrège les opinions des agents d'analyse (technique + ICT/SMC), calcule un
biais consensuel et un niveau de confiance, puis demande à l'agent de risque
les niveaux d'entrée/SL/TP.

Règles :
- Les deux agents doivent globalement pointer dans la même direction.
- La confiance combine la force des signaux et l'accord entre agents.
- Si la confiance < MIN_CONFIDENCE -> NO TRADE.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import AgentOpinion


@dataclass
class TradeSignal:
    decision: str = "NO TRADE"      # BUY / SELL / NO TRADE
    confidence: float = 0.0         # 0..100
    entry: float | None = None
    sl: float | None = None
    tp: float | None = None
    lot: float | None = None
    risk_amount: float | None = None
    rr: float | None = None
    reasons: list[str] = field(default_factory=list)
    opinions: list[AgentOpinion] = field(default_factory=list)


class DecisionAgent:
    name = "Décision"

    # Poids de chaque agent dans le consensus
    AGENT_WEIGHTS = {
        "Technique": 0.30,
        "ICT/SMC": 0.25,
        "Macro": 0.20,
        "Quant": 0.25,
    }

    def __init__(self, config, risk_agent):
        self.config = config
        self.risk_agent = risk_agent

    def decide(self, opinions: list[AgentOpinion], market: dict, client) -> TradeSignal:
        cfg = self.config
        signal = TradeSignal(opinions=opinions)

        # Score signé : +score pour BUY, -score pour SELL, pondéré par agent
        net = 0.0
        agreement_dir = {"BUY": 0.0, "SELL": 0.0}
        for op in opinions:
            w = self.AGENT_WEIGHTS.get(op.name, 0.3)
            if op.bias == "BUY":
                net += op.score * w
                agreement_dir["BUY"] += w
            elif op.bias == "SELL":
                net -= op.score * w
                agreement_dir["SELL"] += w
            signal.reasons.extend(f"[{op.name}] {r}" for r in op.reasons)

        direction = "BUY" if net > 0 else "SELL" if net < 0 else "NO TRADE"

        # Confiance = moyenne pondérée des scores allant dans la direction nette
        if direction == "NO TRADE":
            signal.decision = "NO TRADE"
            signal.confidence = 0.0
            signal.reasons.insert(0, "Pas de consensus directionnel entre les agents.")
            return signal

        same = [op for op in opinions if op.bias == direction]
        opposite = [op for op in opinions if op.bias not in (direction, "NEUTRAL")]

        base_conf = sum(op.score * self.AGENT_WEIGHTS.get(op.name, 0.3) for op in same)
        base_conf /= max(sum(self.AGENT_WEIGHTS.get(op.name, 0.3) for op in same), 0.01)

        # Bonus si les deux agents sont d'accord, malus si l'un s'oppose
        if len(same) >= 2:
            base_conf = min(100, base_conf + 10)
        if opposite:
            base_conf *= 0.6
            signal.reasons.insert(0, "Attention : un agent est en désaccord.")

        confidence = round(base_conf, 1)

        if confidence < cfg.MIN_CONFIDENCE:
            signal.decision = "NO TRADE"
            signal.confidence = confidence
            signal.reasons.insert(
                0,
                f"Confiance {confidence:.0f}% < seuil {cfg.MIN_CONFIDENCE}% -> on attend.",
            )
            return signal

        # --- Calcul du risque / niveaux ---
        levels = self.risk_agent.compute(direction, market, client)
        if not levels:
            signal.decision = "NO TRADE"
            signal.confidence = confidence
            signal.reasons.insert(0, "Impossible de calculer SL/TP/lot (données insuffisantes).")
            return signal

        signal.decision = direction
        signal.confidence = confidence
        signal.entry = levels["entry"]
        signal.sl = levels["sl"]
        signal.tp = levels["tp"]
        signal.lot = levels["lot"]
        signal.risk_amount = levels["risk_amount"]
        signal.rr = levels["rr"]
        signal.reasons.insert(
            0,
            f"Consensus {direction} (confiance {confidence:.0f}%), "
            f"RR {levels['rr']:.1f}, risque {levels['risk_amount']}$.",
        )
        return signal

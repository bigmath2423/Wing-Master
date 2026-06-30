"""
agents/base.py
==============
Structures communes aux agents.

Chaque agent d'analyse renvoie un `AgentOpinion` :
- bias   : "BUY", "SELL" ou "NEUTRAL"
- score  : force du signal de 0 à 100
- reasons: liste de raisons lisibles (pour expliquer le trade)
- data   : valeurs brutes utiles (EMA, RSI, niveaux...) pour les autres agents

Cette uniformité (inspirée de l'approche multi-agents de TradingAgents) permet
à l'agent de décision d'agréger facilement toutes les opinions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentOpinion:
    name: str
    bias: str = "NEUTRAL"           # BUY / SELL / NEUTRAL
    score: float = 0.0              # 0..100
    reasons: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def add(self, reason: str) -> None:
        self.reasons.append(reason)


class BaseAgent:
    """Classe de base : tous les agents implémentent analyze()."""

    name = "base"

    def __init__(self, config):
        self.config = config

    def analyze(self, market: dict) -> AgentOpinion:  # pragma: no cover
        """`market` est un dict { timeframe: DataFrame }.
        Doit être surchargée par les agents concrets."""
        raise NotImplementedError

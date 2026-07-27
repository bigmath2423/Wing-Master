"""Agent d'analyse quantitative de backtests de trading.

Ce package sépare volontairement deux responsabilités :

1. Le CALCUL (déterministe, testable, reproductible) : toutes les statistiques
   sont produites par du code Python, jamais par un modèle de langage.
2. L'INTERPRÉTATION (rôle d'analyste quant) : un LLM commente les chiffres déjà
   calculés et propose des pistes, sous une discipline stricte (robustesse avant
   win rate).

Cette séparation garantit que l'agent se comporte comme un chercheur qui lit des
données, et non comme une IA qui invente des chiffres pour « améliorer » un score.
"""

from .ingest import load_trades, normalize
from .metrics import global_metrics
from .losses import analyze_losses
from .winners import analyze_winners
from .suggestions import build_suggestions
from .report import build_report

__all__ = [
    "load_trades",
    "normalize",
    "global_metrics",
    "analyze_losses",
    "analyze_winners",
    "build_suggestions",
    "build_report",
]

__version__ = "0.1.0"

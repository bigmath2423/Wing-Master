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
from .walkforward import walk_forward
from .proposals import build_proposals, generate_candidate_pine
from .validate import validate_candidate, compare_backtests
from .robustness import monte_carlo_drawdown
from .rolling import rolling_walk_forward, optimize_threshold
from .htmlview import render_report

__all__ = [
    "load_trades",
    "normalize",
    "global_metrics",
    "analyze_losses",
    "analyze_winners",
    "build_suggestions",
    "build_report",
    "walk_forward",
    "build_proposals",
    "generate_candidate_pine",
    "validate_candidate",
    "compare_backtests",
    "monte_carlo_drawdown",
    "rolling_walk_forward",
    "optimize_threshold",
    "render_report",
]

# Source unique de vérité : la version vit dans pyproject.toml et se lit ici via
# les métadonnées du paquet. La dupliquer en dur les ferait diverger — ce qui
# était déjà arrivé (0.1.0 ici contre 0.3.0 dans pyproject).
try:  # paquet installé
    from importlib.metadata import PackageNotFoundError, version as _version
    __version__ = _version("backtest-agent")
except (ImportError, PackageNotFoundError):  # exécution depuis les sources
    __version__ = "0.0.0+source"

"""Génération du biais marché : direction + confiance + niveau de risque.

    XAUUSD
      MACRO BIAS : HAUSSIER
      CONFIANCE  : 82%

Confiance = f(amplitude du score, cohérence des facteurs).
Un score fort ET des facteurs alignés (même signe) => haute confiance.
Un score moyen avec facteurs contradictoires => faible confiance.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engine.scoring import AssetScore

BULLISH, BEARISH, NEUTRAL = "bullish", "bearish", "neutral"
_NEUTRAL_BAND = 15.0  # |score| < 15 => neutre


@dataclass(slots=True)
class BiasResult:
    asset: str
    score: float
    bias: str
    confidence: float
    risk_level: str


def _direction(score: float) -> str:
    if score >= _NEUTRAL_BAND:
        return BULLISH
    if score <= -_NEUTRAL_BAND:
        return BEARISH
    return NEUTRAL


def _coherence(factors: dict[str, float]) -> float:
    """Part des facteurs alignés avec le signe dominant (0..1)."""
    values = [v for v in factors.values() if abs(v) > 1e-6]
    if not values:
        return 0.0
    net = sum(values)
    if net == 0:
        return 0.0
    aligned = sum(abs(v) for v in values if (v > 0) == (net > 0))
    total = sum(abs(v) for v in values)
    return aligned / total if total else 0.0


def compute_confidence(score: float, factors: dict[str, float]) -> float:
    magnitude = min(abs(score) / 100.0, 1.0)     # 0..1
    coherence = _coherence(factors)              # 0..1
    # Pondération : l'amplitude compte plus, la cohérence affine.
    raw = 100.0 * (0.65 * magnitude + 0.35 * coherence)
    # Plancher réaliste pour éviter des "0%" trompeurs sur signal faible.
    return round(max(min(raw, 99.0), 0.0), 0)


def compute_risk_level(geo_risk_index: float, upcoming_high_impact: int, dxy_change_pct: float) -> str:
    """Risque de contexte (volatilité événementielle), indépendant de la direction."""
    risk = 0.0
    risk += geo_risk_index * 0.5                       # tension géopolitique
    risk += min(upcoming_high_impact, 3) / 3.0 * 0.3   # événements macro imminents
    risk += min(abs(dxy_change_pct) / 1.0, 1.0) * 0.2  # nervosité du dollar
    if risk >= 0.6:
        return "high"
    if risk >= 0.3:
        return "medium"
    return "low"


def compute_bias(
    asset_score: AssetScore,
    *,
    geo_risk_index: float = 0.0,
    upcoming_high_impact: int = 0,
    dxy_change_pct: float = 0.0,
) -> BiasResult:
    return BiasResult(
        asset=asset_score.asset,
        score=asset_score.score,
        bias=_direction(asset_score.score),
        confidence=compute_confidence(asset_score.score, asset_score.factors),
        risk_level=compute_risk_level(geo_risk_index, upcoming_high_impact, dxy_change_pct),
    )

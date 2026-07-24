"""Tests du moteur de biais : direction, confiance, niveau de risque."""

from app.engine import bias as B
from app.engine.scoring import AssetScore


def _score(score, factors):
    return AssetScore(asset="gold", score=score, factors=factors)


def test_direction_thresholds():
    assert B.compute_bias(_score(50, {"a": 50})).bias == B.BULLISH
    assert B.compute_bias(_score(-50, {"a": -50})).bias == B.BEARISH
    assert B.compute_bias(_score(5, {"a": 5})).bias == B.NEUTRAL


def test_confidence_grows_with_magnitude():
    low = B.compute_confidence(20, {"a": 20})
    high = B.compute_confidence(90, {"a": 90})
    assert high > low


def test_coherent_factors_more_confident_than_conflicting():
    coherent = B.compute_confidence(40, {"a": 20, "b": 20})
    conflicting = B.compute_confidence(40, {"a": 70, "b": -30})
    assert coherent > conflicting


def test_risk_level_levels():
    assert B.compute_risk_level(0.0, 0, 0.0) == "low"
    assert B.compute_risk_level(0.9, 3, 1.0) == "high"


def test_confidence_capped():
    assert B.compute_confidence(100, {"a": 100}) <= 99

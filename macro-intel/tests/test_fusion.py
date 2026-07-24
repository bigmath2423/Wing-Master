"""Tests de la fusion technique + macro (règle : macro ne trade jamais seul)."""

from app.engine.bias import BiasResult
from app.engine.fusion import fuse


def _macro(score, bias, conf=80):
    return BiasResult(asset="gold", score=score, bias=bias, confidence=conf, risk_level="medium")


def test_aligned_strong_macro_reinforces():
    r = fuse(symbol="XAUUSD", side="buy", technical_score=88, macro=_macro(70, "bullish"))
    assert r["verdict"] == "reinforced"
    assert r["alignment"] == "aligned"
    assert r["final_confidence"] >= 88


def test_conflicting_strong_macro_warns():
    r = fuse(symbol="XAUUSD", side="buy", technical_score=90, macro=_macro(-80, "bearish"))
    assert r["verdict"] == "warning"
    assert r["alignment"] == "conflict"
    assert r["final_confidence"] < 90
    assert "défavorable" in r["message"]


def test_neutral_macro_keeps_standard():
    r = fuse(symbol="XAUUSD", side="buy", technical_score=75, macro=_macro(5, "neutral"))
    assert r["verdict"] == "standard"
    assert r["alignment"] == "neutral"


def test_sell_side_alignment():
    # Vente + macro baissier => aligné.
    r = fuse(symbol="XAUUSD", side="sell", technical_score=80, macro=_macro(-60, "bearish"))
    assert r["alignment"] == "aligned"
    assert r["verdict"] == "reinforced"


def test_confidence_never_out_of_bounds():
    r = fuse(symbol="XAUUSD", side="buy", technical_score=99, macro=_macro(100, "bullish"))
    assert 0 <= r["final_confidence"] <= 100

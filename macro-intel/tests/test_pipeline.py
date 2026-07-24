"""Tests du mapping symbole -> actif et de la robustesse des providers."""

from app.domain import GeoRiskReading, MarketReadings
from app.engine import scoring
from app.pipeline import symbol_to_asset
from app.providers.market_data import fetch_market_readings


def test_symbol_mapping():
    assert symbol_to_asset("XAUUSD") == "gold"
    assert symbol_to_asset("GOLD") == "gold"
    assert symbol_to_asset("BTCUSDT") == "btc"
    assert symbol_to_asset("BTCUSD.P") == "btc"
    assert symbol_to_asset("WTIUSD") == "commodities"  # défaut


def test_market_readings_never_none():
    # Même hors-ligne, le provider renvoie des valeurs exploitables (repli).
    r = fetch_market_readings()
    assert r.dxy is not None
    assert r.us10y is not None
    assert r.real_rate_10y is not None
    assert r.breakeven_inflation is not None


def test_score_all_returns_three_assets():
    market = MarketReadings(
        dxy=100, dxy_change_pct=0.0, us10y=4.2, real_rate_10y=1.5, breakeven_inflation=2.0
    )
    out = scoring.score_all(market, GeoRiskReading(risk_index=0.4), [])
    assert set(out) == {"gold", "btc", "commodities"}
    for asc in out.values():
        assert -100 <= asc.score <= 100

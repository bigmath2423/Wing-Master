"""Tests du moteur d'analyse : régimes, courbe des taux, corrélations."""

from app.analysis.correlations import correlate, correlation_matrix, pearson
from app.analysis.regime import detect_regime
from app.analysis.yield_curve import analyse_curve
from app.domain import GeoRiskReading, MarketReadings


# ── Courbe des taux ─────────────────────────────────────────────
def test_curve_inverted():
    reading = analyse_curve(us2y=4.8, us10y=4.2, us30y=4.3)
    assert reading.shape == "inverted"
    assert reading.spread_10y2y < 0
    assert "ralentissement" in reading.interpretation


def test_curve_normal():
    reading = analyse_curve(us2y=3.5, us10y=4.2, us30y=4.4)
    assert reading.shape == "normal"
    assert reading.spread_10y2y > 0


def test_curve_steep():
    assert analyse_curve(us2y=2.0, us10y=4.0, us30y=4.5).shape == "steep"


def test_curve_unknown_without_data():
    reading = analyse_curve(us2y=None, us10y=None)
    assert reading.shape == "unknown"
    assert reading.spread_10y2y is None


# ── Régimes ─────────────────────────────────────────────────────
def _market(**kw):
    base = {"dxy": 100.0, "dxy_change_pct": 0.0, "us10y": 4.2, "real_rate_10y": 1.5}
    base.update(kw)
    return MarketReadings(**base)


def test_regime_risk_off_on_high_vix_and_geo():
    reading = detect_regime(_market(vix=32.0), GeoRiskReading(risk_index=0.8, tone=-5))
    assert reading.regime == "risk_off"
    assert reading.confidence > 0
    assert reading.drivers


def test_regime_tightening_on_rising_real_rates():
    reading = detect_regime(
        _market(real_rate_change_bps=15, real_rate_10y=2.4, vix=15.0), GeoRiskReading(risk_index=0.2)
    )
    assert reading.regime == "tightening"


def test_regime_easing_on_falling_real_rates():
    reading = detect_regime(
        _market(real_rate_change_bps=-15, real_rate_10y=0.3, vix=16.0), GeoRiskReading(risk_index=0.2)
    )
    assert reading.regime == "easing"


def test_regime_stagflation_watch():
    reading = detect_regime(
        _market(breakeven_inflation=2.8, vix=20.0),
        GeoRiskReading(risk_index=0.3),
        growth_momentum=-0.5,
    )
    assert reading.regime == "stagflation_watch"


def test_regime_neutral_when_no_dominant_factor():
    reading = detect_regime(_market(), GeoRiskReading(risk_index=0.35))
    assert reading.regime == "neutral"
    assert reading.confidence <= 45


def test_regime_confidence_bounded():
    reading = detect_regime(
        _market(vix=45.0, real_rate_change_bps=30, dxy_change_pct=2.0),
        GeoRiskReading(risk_index=1.0, tone=-8),
    )
    assert 0 <= reading.confidence <= 92


# ── Corrélations ────────────────────────────────────────────────
def test_pearson_perfect_positive():
    assert pearson([1, 2, 3, 4, 5, 6], [2, 4, 6, 8, 10, 12]) == 1.0


def test_pearson_perfect_negative():
    assert pearson([1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1]) == -1.0


def test_pearson_needs_enough_points():
    assert pearson([1, 2], [2, 4]) is None


def test_correlate_on_returns():
    rising = [100 + i for i in range(40)]
    falling = [100 - i for i in range(40)]
    reading = correlate(rising, falling, 30, "a~b")
    assert reading.value is not None
    assert reading.direction in {"positive", "négative", "neutre"}


def test_correlation_matrix_skips_missing_series():
    series = {"market.dxy": [100 + i for i in range(40)]}  # paire incomplète
    assert correlation_matrix(series) == []

"""Tests du moteur de scoring : cohérence des relations économiques de l'or."""
from app.domain import GeoRiskReading, MarketReadings, NewsImpact
from app.engine import scoring


def _base_market(**kw):
    m = MarketReadings(
        dxy=100, dxy_change_pct=0.0, us10y=4.2, us10y_change_bps=0.0,
        real_rate_10y=1.5, real_rate_change_bps=0.0, breakeven_inflation=2.0,
    )
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def test_score_bounded():
    s = scoring.score_gold(_base_market(), GeoRiskReading(risk_index=1.0, tone=-6), [])
    assert -100 <= s.score <= 100


def test_strong_dollar_is_bearish_gold():
    weak = scoring.score_gold(_base_market(dxy_change_pct=-1.0), GeoRiskReading(), [])
    strong = scoring.score_gold(_base_market(dxy_change_pct=+1.0), GeoRiskReading(), [])
    assert strong.factors["dollar"] < weak.factors["dollar"]
    assert strong.factors["dollar"] < 0 < weak.factors["dollar"]


def test_rising_real_rates_bearish_gold():
    up = scoring.score_gold(_base_market(real_rate_change_bps=+25), GeoRiskReading(), [])
    down = scoring.score_gold(_base_market(real_rate_change_bps=-25), GeoRiskReading(), [])
    assert up.factors["us_rates"] < down.factors["us_rates"]


def test_geopolitical_risk_supports_gold():
    calm = scoring.score_gold(_base_market(), GeoRiskReading(risk_index=0.0, tone=0), [])
    crisis = scoring.score_gold(_base_market(), GeoRiskReading(risk_index=0.9, tone=-5), [])
    assert crisis.factors["geopolitics"] > calm.factors["geopolitics"]
    assert crisis.score > calm.score


def test_higher_inflation_supports_gold():
    low = scoring.score_gold(_base_market(breakeven_inflation=1.5), GeoRiskReading(), [])
    high = scoring.score_gold(_base_market(breakeven_inflation=3.0), GeoRiskReading(), [])
    assert high.factors["inflation"] > low.factors["inflation"]


def test_news_impact_flows_through():
    war = NewsImpact(title="War escalates", category="geopolitics",
                     severity=0.9, impact_gold=35)
    s = scoring.score_gold(_base_market(), GeoRiskReading(risk_index=0.5), [war])
    assert s.factors["geopolitics"] > 0

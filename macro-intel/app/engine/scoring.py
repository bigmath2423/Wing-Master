"""Moteur de scoring macro.

Transforme les lectures de marché + news + risque géopolitique en un score
signé par actif, avec le détail des facteurs.

    GOLD MACRO SCORE : +75/100
      - Géopolitique   : +30
      - Dollar         : +15
      - Taux US        : -10
      - Inflation      : +20
      - Sentiment risque: +20

Chaque facteur est borné (cap) puis la somme est ramenée dans [-100, +100].
Les logiques sont documentées inline (relation économique avec l'or).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domain import GeoRiskReading, MarketReadings, NewsImpact


# Bornes par facteur (pour éviter qu'un seul facteur domine tout le score).
_CAPS = {
    "geopolitics": (-10.0, 35.0),
    "dollar": (-25.0, 25.0),
    "us_rates": (-30.0, 30.0),
    "inflation": (-20.0, 25.0),
    "risk_sentiment": (-25.0, 25.0),
}


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass(slots=True)
class AssetScore:
    asset: str
    score: float
    factors: dict[str, float] = field(default_factory=dict)
    drivers: dict[str, float] = field(default_factory=dict)  # valeurs brutes (debug/dashboard)


def _avg_news_gold(news: list[NewsImpact]) -> float:
    """Sentiment or moyen pondéré par la sévérité (news récentes)."""
    if not news:
        return 0.0
    num = sum(n.impact_gold * (0.5 + n.severity) for n in news)
    den = sum(0.5 + n.severity for n in news)
    return num / den if den else 0.0


def score_gold(
    market: MarketReadings,
    geo: GeoRiskReading,
    news: list[NewsImpact],
) -> AssetScore:
    f: dict[str, float] = {}

    # 1) Géopolitique : risque élevé -> valeur refuge -> or haussier.
    geo_component = geo.risk_index * 35.0                       # 0..35
    geo_news = sum(n.impact_gold for n in news if n.category == "geopolitics")
    f["geopolitics"] = _clamp(geo_component + 0.3 * geo_news, *_CAPS["geopolitics"])

    # 2) Dollar : DXY en hausse -> or baissier (relation inverse).
    dxy_chg = market.dxy_change_pct or 0.0
    f["dollar"] = _clamp(-dxy_chg * 25.0, *_CAPS["dollar"])     # +1% DXY -> -25 (borné)

    # 3) Taux US : ce sont les TAUX RÉELS qui pilotent l'or.
    #    Taux réel en hausse -> coût d'opportunité de l'or -> baissier.
    real_chg = market.real_rate_change_bps or 0.0              # en points de base
    nominal_chg = market.us10y_change_bps or 0.0
    rate_component = -(0.8 * real_chg + 0.2 * nominal_chg) * 1.2
    # Niveau absolu du taux réel : très bas/négatif = soutien structurel.
    if market.real_rate_10y is not None:
        rate_component += _clamp((1.5 - market.real_rate_10y) * 6.0, -12.0, 12.0)
    f["us_rates"] = _clamp(rate_component, *_CAPS["us_rates"])

    # 4) Inflation : anticipations d'inflation élevées -> or couverture.
    be = market.breakeven_inflation
    infl_component = 0.0
    if be is not None:
        infl_component = _clamp((be - 2.0) * 18.0, -20.0, 25.0)  # >2% = soutien
    infl_news = sum(n.impact_gold for n in news if "inflation" in n.title.lower())
    f["inflation"] = _clamp(infl_component + 0.2 * infl_news, *_CAPS["inflation"])

    # 5) Sentiment risque : agrégat des news + ton géopolitique.
    sentiment = _avg_news_gold(news) * 0.6 + (-geo.tone) * 3.0
    f["risk_sentiment"] = _clamp(sentiment, *_CAPS["risk_sentiment"])

    total = _clamp(sum(f.values()), -100.0, 100.0)
    return AssetScore(
        asset="gold",
        score=round(total, 1),
        factors={k: round(v, 1) for k, v in f.items()},
        drivers={
            "dxy": market.dxy or 0.0,
            "dxy_change_pct": dxy_chg,
            "us10y": market.us10y or 0.0,
            "real_rate_10y": market.real_rate_10y or 0.0,
            "breakeven_inflation": be or 0.0,
            "geo_risk_index": geo.risk_index,
        },
    )


def score_btc(market: MarketReadings, geo: GeoRiskReading, news: list[NewsImpact]) -> AssetScore:
    f: dict[str, float] = {}
    dxy_chg = market.dxy_change_pct or 0.0
    real_chg = market.real_rate_change_bps or 0.0
    # BTC : actif de risque + sensible à la liquidité (dollar/taux).
    f["dollar"] = _clamp(-dxy_chg * 18.0, -22.0, 22.0)
    f["us_rates"] = _clamp(-real_chg * 1.0, -25.0, 25.0)
    f["risk_sentiment"] = _clamp(
        sum(n.impact_btc for n in news) / max(len(news), 1), -30.0, 30.0
    )
    # Un choc géopolitique majeur peut peser (risk-off) mais BTC = refuge partiel.
    f["geopolitics"] = _clamp((geo.risk_index - 0.5) * -20.0, -15.0, 15.0)
    total = _clamp(sum(f.values()), -100.0, 100.0)
    return AssetScore("btc", round(total, 1), {k: round(v, 1) for k, v in f.items()})


def score_commodities(
    market: MarketReadings, geo: GeoRiskReading, news: list[NewsImpact]
) -> AssetScore:
    f: dict[str, float] = {}
    dxy_chg = market.dxy_change_pct or 0.0
    # Matières premières cotées en dollars -> relation inverse au DXY.
    f["dollar"] = _clamp(-dxy_chg * 22.0, -25.0, 25.0)
    # Tensions géopolitiques -> primes de risque sur l'offre (énergie/métaux).
    f["geopolitics"] = _clamp(geo.risk_index * 30.0, -10.0, 30.0)
    f["inflation"] = _clamp(
        ((market.breakeven_inflation or 2.0) - 2.0) * 12.0, -15.0, 20.0
    )
    f["risk_sentiment"] = _clamp(
        sum(n.impact_commodities for n in news) / max(len(news), 1), -20.0, 20.0
    )
    total = _clamp(sum(f.values()), -100.0, 100.0)
    return AssetScore("commodities", round(total, 1), {k: round(v, 1) for k, v in f.items()})


def score_all(
    market: MarketReadings, geo: GeoRiskReading, news: list[NewsImpact]
) -> dict[str, AssetScore]:
    return {
        "gold": score_gold(market, geo, news),
        "btc": score_btc(market, geo, news),
        "commodities": score_commodities(market, geo, news),
    }

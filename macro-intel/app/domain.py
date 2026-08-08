"""Types internes légers partagés entre providers et moteur d'analyse."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


@dataclass(slots=True)
class MarketReadings:
    """Instantané des drivers de marché de l'or."""

    dxy: float | None = None  # niveau indice dollar
    dxy_change_pct: float | None = None  # variation % sur la fenêtre
    us10y: float | None = None  # rendement nominal 10 ans (%)
    us10y_change_bps: float | None = None
    real_rate_10y: float | None = None  # taux réel 10 ans (TIPS, %)
    real_rate_change_bps: float | None = None
    breakeven_inflation: float | None = None  # inflation anticipée 10Y (%)
    # ── Extensions (Tome 2) : courbe des taux et volatilité ──────
    us2y: float | None = None  # rendement nominal 2 ans (%)
    us30y: float | None = None  # rendement nominal 30 ans (%)
    curve_10y2y: float | None = None  # pente 10a-2a (points de %)
    vix: float | None = None  # indice de volatilité
    vix_change_pct: float | None = None
    source: str = "unknown"
    ts: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.UTC))


@dataclass(slots=True)
class NewsImpact:
    """News classifiée avec impact chiffré par actif."""

    title: str
    category: str  # geopolitics | central_bank | macro | markets
    source: str = ""
    url: str = ""
    severity: float = 0.0  # 0..1
    impact_gold: float = 0.0  # contribution -100..+100
    impact_btc: float = 0.0
    impact_commodities: float = 0.0
    ts: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.UTC))


@dataclass(slots=True)
class GeoRiskReading:
    """Indice de risque géopolitique agrégé (ex: via GDELT)."""

    risk_index: float = 0.0  # 0..1 (0 = calme, 1 = crise majeure)
    tone: float = 0.0  # ton médiatique moyen (négatif = tension)
    top_events: list[str] = field(default_factory=list)
    source: str = "unknown"
    ts: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.UTC))

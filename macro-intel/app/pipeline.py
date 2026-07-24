"""Orchestration : collecte -> classification -> scoring -> biais -> état.

Expose :
  - run_pipeline()  : rafraîchit tout et met à jour l'état + la base.
  - STATE           : dernier snapshot en mémoire (servi par l'API).
  - symbol_to_asset : mappe un symbole TradingView vers un actif macro.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import logging
import threading

from sqlalchemy import select

from app.db import SessionLocal
from app.domain import GeoRiskReading, MarketReadings, NewsImpact
from app.engine import bias as bias_engine
from app.engine import scoring
from app.engine.ai_classifier import classify_batch
from app.engine.bias import BiasResult
from app.models import MacroSnapshot, MarketDatum, NewsEvent
from app.providers.central_banks import fetch_central_bank_events
from app.providers.economic_calendar import fetch_calendar
from app.providers.geopolitics import fetch_geo_risk
from app.providers.market_data import fetch_market_readings
from app.providers.news import fetch_news

logger = logging.getLogger("macro.pipeline")


class MacroState:
    """État thread-safe partagé entre le scheduler et l'API."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.generated_at: dt.datetime | None = None
        self.market: MarketReadings = MarketReadings(source="init")
        self.geo: GeoRiskReading = GeoRiskReading()
        self.bias: dict[str, BiasResult] = {}
        self.scores: dict[str, scoring.AssetScore] = {}
        self.news: list[NewsImpact] = []
        self.upcoming_high_impact: int = 0

    def update(self, **kwargs) -> None:
        with self._lock:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "generated_at": self.generated_at,
                "market": self.market,
                "geo": self.geo,
                "bias": dict(self.bias),
                "scores": dict(self.scores),
                "news": list(self.news),
            }


STATE = MacroState()

# Mapping symbole TradingView -> actif macro.
_SYMBOL_MAP = {
    "XAUUSD": "gold",
    "GOLD": "gold",
    "GC": "gold",
    "BTCUSD": "btc",
    "BTCUSDT": "btc",
    "XBTUSD": "btc",
}


def symbol_to_asset(symbol: str) -> str:
    s = symbol.upper().replace("/", "").replace("PERP", "")
    for key, asset in _SYMBOL_MAP.items():
        if s.startswith(key):
            return asset
    return "commodities"


def _count_upcoming_high_impact() -> int:
    now = dt.datetime.now(dt.UTC)
    horizon = now + dt.timedelta(hours=48)
    count = 0
    for ev in fetch_calendar():
        if ev.get("importance", 1) < 3:
            continue
        raw = ev.get("event_time", "")
        try:
            when = dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=dt.UTC)
        except (ValueError, TypeError):
            continue
        if now <= when <= horizon:
            count += 1
    return count


def _persist(
    scores: dict[str, scoring.AssetScore],
    biases: dict[str, BiasResult],
    market: MarketReadings,
    news: list[NewsImpact],
) -> None:
    session = SessionLocal()
    try:
        for key, val in {
            "dxy": market.dxy,
            "us10y": market.us10y,
            "real_rate_10y": market.real_rate_10y,
            "breakeven_inflation": market.breakeven_inflation,
        }.items():
            if val is not None:
                session.add(MarketDatum(key=key, value=float(val), source=market.source))

        for asset, b in biases.items():
            session.add(
                MacroSnapshot(
                    asset=asset,
                    score=b.score,
                    bias=b.bias,
                    confidence=b.confidence,
                    risk_level=b.risk_level,
                    factors=scores[asset].factors,
                )
            )

        # News : clé de dédup stable (sha1 du titre) pour ne pas ré-insérer
        # les mêmes titres à chaque cycle. hash() n'est PAS stable entre process.
        candidates = {}
        for n in news[:30]:
            key = hashlib.sha1(n.title.encode("utf-8")).hexdigest()[:32]
            candidates[key] = n  # dédoublonne aussi au sein du même lot
        if candidates:
            existing = set(
                session.scalars(
                    select(NewsEvent.dedup_key).where(NewsEvent.dedup_key.in_(candidates.keys()))
                ).all()
            )
            for key, n in candidates.items():
                if key in existing:
                    continue
                session.add(
                    NewsEvent(
                        source=n.source,
                        category=n.category,
                        title=n.title[:500],
                        url=n.url,
                        impact={
                            "gold": n.impact_gold,
                            "btc": n.impact_btc,
                            "commodities": n.impact_commodities,
                        },
                        severity=n.severity,
                        dedup_key=key,
                    )
                )
        session.commit()
    except Exception as exc:
        logger.warning("Persistance partielle : %s", exc)
        session.rollback()
    finally:
        session.close()


def run_pipeline() -> dict[str, BiasResult]:
    """Cycle complet. Renvoie le biais par actif et met à jour STATE."""
    logger.info("Cycle macro : collecte des données...")

    market = fetch_market_readings()
    geo = fetch_geo_risk()

    raw_news = fetch_news() + fetch_central_bank_events()
    news = classify_batch(raw_news)

    scores = scoring.score_all(market, geo, news)
    upcoming = _count_upcoming_high_impact()

    biases: dict[str, BiasResult] = {}
    for asset, asc in scores.items():
        biases[asset] = bias_engine.compute_bias(
            asc,
            geo_risk_index=geo.risk_index,
            upcoming_high_impact=upcoming,
            dxy_change_pct=market.dxy_change_pct or 0.0,
        )

    STATE.update(
        generated_at=dt.datetime.now(dt.UTC),
        market=market,
        geo=geo,
        bias=biases,
        scores=scores,
        news=news,
        upcoming_high_impact=upcoming,
    )
    _persist(scores, biases, market, news)

    logger.info(
        "Cycle terminé — GOLD %s (%s, conf %s%%, risque %s)",
        biases["gold"].score,
        biases["gold"].bias,
        biases["gold"].confidence,
        biases["gold"].risk_level,
    )
    return biases

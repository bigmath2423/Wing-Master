"""Modèles ORM : historisation des données brutes et des snapshots macro."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class MarketDatum(Base):
    """Point de donnée d'un driver de marché (DXY, US10Y, taux réel...)."""

    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[dt.datetime] = mapped_column(default=_utcnow, index=True)
    key: Mapped[str] = mapped_column(String(32), index=True)   # dxy, us10y, real_rate...
    value: Mapped[float] = mapped_column(Float)
    change: Mapped[float] = mapped_column(Float, default=0.0)  # variation vs point précédent
    source: Mapped[str] = mapped_column(String(32), default="unknown")


class NewsEvent(Base):
    """News économique / géopolitique + impact classifié."""

    __tablename__ = "news_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[dt.datetime] = mapped_column(default=_utcnow, index=True)
    source: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(32), index=True)  # geopolitics, cb, macro...
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, default="")
    # Impact classifié (par asset) : {"gold": +30, "btc": -10, "commodities": +5}
    impact: Mapped[dict] = mapped_column(JSON, default=dict)
    severity: Mapped[float] = mapped_column(Float, default=0.0)   # 0..1
    dedup_key: Mapped[str] = mapped_column(String(64), index=True, default="")


class CalendarEvent(Base):
    """Événement du calendrier économique (CPI, NFP, FOMC...)."""

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_time: Mapped[dt.datetime] = mapped_column(index=True)
    country: Mapped[str] = mapped_column(String(8), default="US")
    event: Mapped[str] = mapped_column(Text)
    importance: Mapped[int] = mapped_column(Integer, default=1)  # 1..3
    actual: Mapped[str] = mapped_column(String(32), default="")
    forecast: Mapped[str] = mapped_column(String(32), default="")
    previous: Mapped[str] = mapped_column(String(32), default="")
    dedup_key: Mapped[str] = mapped_column(String(64), index=True, default="")


class MacroSnapshot(Base):
    """Snapshot calculé : scores + biais par asset à un instant T."""

    __tablename__ = "macro_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[dt.datetime] = mapped_column(default=_utcnow, index=True)
    asset: Mapped[str] = mapped_column(String(16), index=True)  # gold, btc, commodities
    score: Mapped[float] = mapped_column(Float)                 # -100..+100
    bias: Mapped[str] = mapped_column(String(16))               # bullish/bearish/neutral
    confidence: Mapped[float] = mapped_column(Float)            # 0..100
    risk_level: Mapped[str] = mapped_column(String(16))         # low/medium/high
    factors: Mapped[dict] = mapped_column(JSON, default=dict)   # détail par facteur

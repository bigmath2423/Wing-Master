"""Schémas Pydantic : contrats d'entrée/sortie de l'API."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ── Sorties macro ───────────────────────────────────────────────
class FactorBreakdown(BaseModel):
    geopolitics: float = 0.0
    dollar: float = 0.0
    us_rates: float = 0.0
    inflation: float = 0.0
    risk_sentiment: float = 0.0


class MacroBias(BaseModel):
    asset: str
    score: float = Field(..., description="Score macro de -100 à +100")
    bias: str = Field(..., description="bullish | bearish | neutral")
    confidence: float = Field(..., description="Confiance 0..100")
    risk_level: str = Field(..., description="low | medium | high")
    factors: FactorBreakdown
    updated_at: dt.datetime


class Headline(BaseModel):
    ts: dt.datetime
    category: str
    title: str
    impact_gold: float = 0.0
    severity: float = 0.0
    url: str = ""


class MacroLatest(BaseModel):
    """Ce que le dashboard / TradingView consomme."""

    generated_at: dt.datetime
    assets: dict[str, MacroBias]
    headlines: list[Headline] = []
    # Valeurs brutes des drivers de l'or (pour synchroniser les curseurs live).
    gold_drivers: dict[str, float] = {}
    sources: dict[str, str] = {}


# ── Entrée : webhook depuis l'indicateur TradingView ────────────
class TradingViewSignal(BaseModel):
    """Payload envoyé par l'alerte Pine Script de votre indicateur."""

    secret: str = Field(..., description="Doit correspondre à API_SHARED_SECRET")
    symbol: str = Field(..., min_length=1, examples=["XAUUSD"])
    side: Literal["buy", "sell"] = Field(..., description="buy | sell")
    technical_score: float = Field(..., ge=0, le=100, description="Score technique 0..100")
    price: float | None = None
    timeframe: str | None = None
    strategy: str | None = "SMC+VWAP+Structure"
    note: str | None = None

    @field_validator("side", mode="before")
    @classmethod
    def _normalize_side(cls, v: str) -> str:
        """Tolère long/short/BUY/SELL depuis les alertes TradingView."""
        s = str(v).strip().lower()
        return {"long": "buy", "short": "sell"}.get(s, s)


class FusionResult(BaseModel):
    """Décision fusionnée technique + macro (jamais un trade seul)."""

    symbol: str
    side: str
    technical_score: float
    macro_score: float
    macro_bias: str
    macro_confidence: float
    alignment: str = Field(..., description="aligned | conflict | neutral")
    verdict: str = Field(..., description="reinforced | warning | standard")
    final_confidence: float
    message: str

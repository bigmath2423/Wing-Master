"""Drivers de marché de l'or : DXY, rendements US, taux réels, inflation.

Priorité des sources :
  1. FRED (gratuit, clé) — séries officielles quotidiennes.
  2. yfinance — DXY / US10Y intraday si installé.
  3. Fallback neutre — le système reste fonctionnel hors-ligne.

Séries FRED utilisées :
  DGS10   -> rendement nominal 10 ans
  DFII10  -> rendement réel 10 ans (TIPS)  == taux réel
  T10YIE  -> point mort d'inflation 10 ans (inflation anticipée)
"""
from __future__ import annotations

import logging

from app.config import settings
from app.domain import MarketReadings
from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.market")

_FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def _fred_last_two(series_id: str) -> tuple[float, float] | None:
    if not settings.fred_api_key:
        return None
    data = http_get_json(
        _FRED_URL,
        params={
            "series_id": series_id,
            "api_key": settings.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 8,
        },
    )
    if not data or "observations" not in data:
        return None
    vals: list[float] = []
    for obs in data["observations"]:
        try:
            vals.append(float(obs["value"]))
        except (ValueError, KeyError):
            continue
        if len(vals) == 2:
            break
    if len(vals) < 2:
        return None
    return vals[0], vals[1]  # (dernier, précédent)


def _from_fred() -> MarketReadings | None:
    dgs10 = _fred_last_two("DGS10")
    dfii10 = _fred_last_two("DFII10")
    t10yie = _fred_last_two("T10YIE")
    if not any([dgs10, dfii10, t10yie]):
        return None

    r = MarketReadings(source="fred")
    if dgs10:
        r.us10y = dgs10[0]
        r.us10y_change_bps = round((dgs10[0] - dgs10[1]) * 100, 1)
    if dfii10:
        r.real_rate_10y = dfii10[0]
        r.real_rate_change_bps = round((dfii10[0] - dfii10[1]) * 100, 1)
    if t10yie:
        r.breakeven_inflation = t10yie[0]
    return r


def _dxy_from_yfinance() -> tuple[float, float] | None:
    try:
        import yfinance as yf  # import paresseux : dépendance optionnelle
    except ImportError:
        return None
    try:
        hist = yf.Ticker("DX-Y.NYB").history(period="5d", interval="1d")
        if len(hist) < 2:
            return None
        last = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        return last, round((last - prev) / prev * 100, 2)
    except Exception as exc:
        logger.warning("yfinance DXY indisponible : %s", exc)
        return None


def fetch_market_readings() -> MarketReadings:
    """Point d'entrée unique : renvoie toujours un MarketReadings."""
    readings = _from_fred() or MarketReadings(source="fallback")

    dxy = _dxy_from_yfinance()
    if dxy:
        readings.dxy, readings.dxy_change_pct = dxy
        if readings.source == "fallback":
            readings.source = "yfinance"

    # Valeurs de secours neutres si tout a échoué (garde le pipeline vivant).
    if readings.dxy is None:
        readings.dxy, readings.dxy_change_pct = 100.0, 0.0
    if readings.us10y is None:
        readings.us10y, readings.us10y_change_bps = 4.2, 0.0
    if readings.real_rate_10y is None:
        readings.real_rate_10y, readings.real_rate_change_bps = 1.8, 0.0
    if readings.breakeven_inflation is None:
        readings.breakeven_inflation = 2.3

    return readings

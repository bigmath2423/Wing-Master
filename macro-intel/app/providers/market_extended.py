"""Extensions de marché : courbe des taux, VIX, prix multi-actifs.

Complète `market_data.py` (DXY, 10 ans, taux réel, inflation anticipée) avec :
  - rendements 2 et 30 ans + pente 10a-2a (FRED : DGS2, DGS30, T10Y2Y) ;
  - VIX (FRED VIXCLS, repli yfinance ^VIX) ;
  - prix multi-actifs (or, pétrole, indices, forex, crypto) via yfinance.

Comme tous les providers : ne lève jamais, repli gracieux (Tome 2 §6).
"""

from __future__ import annotations

import logging

from app.config import settings
from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.market_ext")

_FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

# Univers de prix suivi (identifiant interne -> symbole yfinance).
PRICE_UNIVERSE: dict[str, str] = {
    "commodity.gold": "GC=F",
    "commodity.silver": "SI=F",
    "commodity.oil": "CL=F",
    "commodity.natgas": "NG=F",
    "commodity.copper": "HG=F",
    "index.spx": "^GSPC",
    "index.ndx": "^NDX",
    "index.dax": "^GDAXI",
    "fx.eurusd": "EURUSD=X",
    "fx.usdjpy": "USDJPY=X",
    "fx.gbpusd": "GBPUSD=X",
    "crypto.btc": "BTC-USD",
    "crypto.eth": "ETH-USD",
}

LABELS: dict[str, str] = {
    "commodity.gold": "Or (XAU)",
    "commodity.silver": "Argent",
    "commodity.oil": "Pétrole WTI",
    "commodity.natgas": "Gaz naturel",
    "commodity.copper": "Cuivre",
    "index.spx": "S&P 500",
    "index.ndx": "Nasdaq 100",
    "index.dax": "DAX",
    "fx.eurusd": "EUR/USD",
    "fx.usdjpy": "USD/JPY",
    "fx.gbpusd": "GBP/USD",
    "crypto.btc": "Bitcoin",
    "crypto.eth": "Ethereum",
}


def _fred_last_two(series_id: str) -> tuple[float, float] | None:
    """Deux dernières valeurs valides d'une série FRED (dernier, précédent)."""
    if not settings.fred_api_key:
        return None
    data = http_get_json(
        _FRED_URL,
        params={
            "series_id": series_id,
            "api_key": settings.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10,
        },
    )
    if not data or "observations" not in data:
        return None
    values: list[float] = []
    for obs in data["observations"]:
        try:
            values.append(float(obs["value"]))
        except (ValueError, KeyError, TypeError):
            continue
        if len(values) == 2:
            break
    return (values[0], values[1]) if len(values) == 2 else None


def fetch_curve_and_vol() -> dict[str, float | bool | None]:
    """Rendements 2/30 ans, pente 10a-2a et VIX. Valeurs None si indisponibles.

    La clé `degraded` (booléenne) indique que des valeurs de repli sont utilisées.
    """
    out: dict[str, float | bool | None] = {
        "us2y": None,
        "us30y": None,
        "curve_10y2y": None,
        "vix": None,
        "vix_change_pct": None,
    }

    if (pair := _fred_last_two("DGS2")) is not None:
        out["us2y"] = pair[0]
    if (pair := _fred_last_two("DGS30")) is not None:
        out["us30y"] = pair[0]
    if (pair := _fred_last_two("T10Y2Y")) is not None:
        out["curve_10y2y"] = pair[0]
    if (pair := _fred_last_two("VIXCLS")) is not None:
        last, prev = pair
        out["vix"] = last
        if prev:
            out["vix_change_pct"] = round((last - prev) / prev * 100, 2)

    if out["vix"] is None:
        quote = _yf_last_change("^VIX")
        if quote:
            out["vix"], out["vix_change_pct"] = quote

    # Repli neutre : garde la lecture de contexte possible hors-ligne. Le drapeau
    # `degraded` remonte jusqu'à l'UI, qui affiche explicitement « données de repli »
    # — on ne fait jamais passer une valeur de secours pour une donnée réelle.
    degraded = out["us2y"] is None and out["vix"] is None
    if degraded:
        out.update(
            {
                "us2y": 4.30,
                "us30y": 4.45,
                "curve_10y2y": None,  # recalculé depuis 10a - 2a par l'analyse
                "vix": 16.0,
                "vix_change_pct": 0.0,
            }
        )
    out["degraded"] = degraded
    return out


def _yf_last_change(symbol: str) -> tuple[float, float] | None:
    """Dernier cours et variation % via yfinance. None si indisponible."""
    try:
        import yfinance as yf
    except ImportError:
        return None
    try:
        hist = yf.Ticker(symbol).history(period="5d", interval="1d")
        if len(hist) < 2:
            return None
        last = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        if prev == 0:
            return None
        return last, round((last - prev) / prev * 100, 2)
    except Exception as exc:
        logger.warning("yfinance indisponible pour %s : %s", symbol, exc)
        return None


def fetch_prices() -> dict[str, dict[str, float]]:
    """Cours et variations de l'univers suivi. Dictionnaire éventuellement vide."""
    out: dict[str, dict[str, float]] = {}
    for key, symbol in PRICE_UNIVERSE.items():
        quote = _yf_last_change(symbol)
        if quote is None:
            continue
        last, change = quote
        out[key] = {"price": last, "change_pct": change}
    if not out:
        logger.info("Aucun prix récupéré (hors-ligne) — l'UI affichera l'état 'indisponible'.")
    return out


def fetch_history(keys: list[str], period: str = "6mo") -> dict[str, list[float]]:
    """Historiques de clôture pour le calcul des corrélations."""
    try:
        import yfinance as yf
    except ImportError:
        return {}
    out: dict[str, list[float]] = {}
    for key in keys:
        symbol = PRICE_UNIVERSE.get(key)
        if not symbol:
            continue
        try:
            hist = yf.Ticker(symbol).history(period=period, interval="1d")
            closes = [float(v) for v in hist["Close"].tolist() if v == v]  # filtre NaN
            if len(closes) >= 10:
                out[key] = closes
        except Exception as exc:
            logger.warning("Historique indisponible pour %s : %s", symbol, exc)
    return out


def fetch_fred_history(series_id: str, key: str, limit: int = 200) -> dict[str, list[float]]:
    """Historique d'une série FRED (pour corréler taux réels / DXY / VIX)."""
    if not settings.fred_api_key:
        return {}
    data = http_get_json(
        _FRED_URL,
        params={
            "series_id": series_id,
            "api_key": settings.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        },
    )
    if not data or "observations" not in data:
        return {}
    values: list[float] = []
    for obs in data["observations"]:
        try:
            values.append(float(obs["value"]))
        except (ValueError, KeyError, TypeError):
            continue
    values.reverse()  # ordre chronologique
    return {key: values} if len(values) >= 10 else {}

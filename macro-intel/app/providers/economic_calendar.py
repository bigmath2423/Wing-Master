"""Calendrier économique (CPI, NFP, FOMC, BCE, taux directeurs).

FMP (Financial Modeling Prep) si clé, sinon liste de secours des rendez-vous
récurrents à forte importance pour cadrer le risque événementiel.
"""
from __future__ import annotations

import datetime as dt

from app.config import settings
from app.providers.base import http_get_json

_HIGH_IMPACT = {"CPI", "Nonfarm", "NFP", "FOMC", "Fed", "ECB", "Interest Rate", "PCE", "Unemployment"}


def _importance(event_name: str) -> int:
    name = event_name.lower()
    if any(k.lower() in name for k in ("fomc", "nonfarm", "cpi", "interest rate")):
        return 3
    if any(k.lower() in name for k in _HIGH_IMPACT):
        return 2
    return 1


def _from_fmp() -> list[dict]:
    if not settings.fmp_api_key:
        return []
    today = dt.date.today()
    data = http_get_json(
        "https://financialmodelingprep.com/api/v3/economic_calendar",
        params={
            "from": today.isoformat(),
            "to": (today + dt.timedelta(days=7)).isoformat(),
            "apikey": settings.fmp_api_key,
        },
    )
    if not isinstance(data, list):
        return []
    out = []
    for item in data:
        name = item.get("event", "")
        out.append(
            {
                "event_time": item.get("date", ""),
                "country": item.get("country", ""),
                "event": name,
                "importance": _importance(name),
                "actual": str(item.get("actual", "") or ""),
                "forecast": str(item.get("estimate", "") or ""),
                "previous": str(item.get("previous", "") or ""),
            }
        )
    return out


def _fallback() -> list[dict]:
    """Rendez-vous macro récurrents (approximatifs) si aucune source."""
    now = dt.datetime.now(dt.timezone.utc)
    return [
        {
            "event_time": (now + dt.timedelta(days=3)).isoformat(),
            "country": "US",
            "event": "US CPI (Inflation) — repère récurrent",
            "importance": 3,
            "actual": "",
            "forecast": "",
            "previous": "",
        },
        {
            "event_time": (now + dt.timedelta(days=6)).isoformat(),
            "country": "US",
            "event": "FOMC / Taux directeur Fed — repère récurrent",
            "importance": 3,
            "actual": "",
            "forecast": "",
            "previous": "",
        },
    ]


def fetch_calendar() -> list[dict]:
    return _from_fmp() or _fallback()

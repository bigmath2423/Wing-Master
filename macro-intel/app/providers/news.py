"""News économiques. Finnhub si clé, sinon flux RSS gratuits (Reuters/IMF...).

Renvoie une liste de dicts bruts {title, url, source, ts, category}.
La classification d'impact est faite en aval par engine.ai_classifier.
"""

from __future__ import annotations

import datetime as dt
import logging

from app.config import settings
from app.providers.base import http_get_json, http_get_text

logger = logging.getLogger("macro.providers.news")

# Flux RSS gratuits (aucune clé requise).
_RSS_FEEDS = [
    ("https://www.investing.com/rss/news_285.rss", "macro"),  # Économie
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "markets"),
]


def _from_finnhub() -> list[dict]:
    if not settings.finnhub_api_key:
        return []
    data = http_get_json(
        "https://finnhub.io/api/v1/news",
        params={"category": "general", "token": settings.finnhub_api_key},
    )
    if not isinstance(data, list):
        return []
    out = []
    for item in data[:40]:
        out.append(
            {
                "title": item.get("headline", ""),
                "url": item.get("url", ""),
                "source": item.get("source", "finnhub"),
                "ts": dt.datetime.fromtimestamp(item.get("datetime", 0), dt.UTC),
                "category": "macro",
            }
        )
    return out


def _from_rss() -> list[dict]:
    try:
        import feedparser
    except ImportError:
        return []
    out: list[dict] = []
    for url, category in _RSS_FEEDS:
        raw = http_get_text(url)
        if not raw:
            continue
        parsed = feedparser.parse(raw)
        for entry in parsed.entries[:20]:
            out.append(
                {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": parsed.feed.get("title", "rss"),
                    "ts": dt.datetime.now(dt.UTC),
                    "category": category,
                }
            )
    return out


def fetch_news() -> list[dict]:
    news = _from_finnhub() or _from_rss()
    if not news:
        logger.info("Aucune news récupérée (hors-ligne ou sans clé).")
    return news

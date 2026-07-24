"""Discours & communiqués des banques centrales (Fed, BCE) via RSS officiels."""
from __future__ import annotations

import datetime as dt

from app.providers.base import http_get_text

# Flux RSS publics et gratuits.
_CB_FEEDS = [
    ("https://www.federalreserve.gov/feeds/press_all.xml", "FED"),
    ("https://www.ecb.europa.eu/rss/press.html", "ECB"),
]


def fetch_central_bank_events() -> list[dict]:
    try:
        import feedparser
    except ImportError:
        return []
    out: list[dict] = []
    for url, bank in _CB_FEEDS:
        raw = http_get_text(url)
        if not raw:
            continue
        parsed = feedparser.parse(raw)
        for entry in parsed.entries[:15]:
            out.append(
                {
                    "title": f"[{bank}] {entry.get('title', '')}",
                    "url": entry.get("link", ""),
                    "source": bank,
                    "ts": dt.datetime.now(dt.timezone.utc),
                    "category": "central_bank",
                }
            )
    return out

"""
core/news_feed.py
=================
Récupère des titres d'actualité depuis des flux RSS gratuits, pour alimenter
automatiquement l'agent de sentiment (au lieu de coller les titres à la main).

Volontairement SANS dépendance externe : utilise urllib (standard) + un parsing
XML léger des balises <title>. Si le réseau échoue (hors-ligne, proxy...), la
fonction renvoie une liste vide et le bot continue normalement.
"""

from __future__ import annotations

import re
import urllib.request
from html import unescape

# Flux RSS gratuits orientés marchés / or / macro (modifiable).
DEFAULT_FEEDS = [
    "https://www.investing.com/rss/commodities_Gold.rss",
    "https://www.investing.com/rss/news_285.rss",   # actualité économique
]

_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)


def _clean(title: str) -> str:
    m = _CDATA_RE.search(title)
    if m:
        title = m.group(1)
    return unescape(title).strip()


def fetch_headlines(feeds: list[str] | None = None,
                    limit: int = 15,
                    timeout: int = 6) -> list[str]:
    """Retourne jusqu'à `limit` titres agrégés depuis les flux RSS.

    Ne lève jamais : en cas d'erreur réseau, retourne ce qui a pu être lu
    (souvent une liste vide)."""
    feeds = feeds or DEFAULT_FEEDS
    headlines: list[str] = []

    for url in feeds:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                xml = resp.read().decode("utf-8", errors="ignore")
        except Exception as exc:  # réseau/proxy/format : on ignore ce flux
            print(f"[news_feed] Flux ignoré ({url}) : {exc}")
            continue

        titles = _TITLE_RE.findall(xml)
        # Le 1er <title> d'un flux RSS est le nom du flux -> on le saute.
        for raw in titles[1:]:
            t = _clean(raw)
            if t and t not in headlines:
                headlines.append(t)

    return headlines[:limit]

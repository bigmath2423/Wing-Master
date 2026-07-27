"""Fil d'actualité économique en direct.

Agrège plusieurs sources **gratuites** (aucune clé requise) et les complète avec
Finnhub si une clé est configurée. Contrairement à la version initiale, les
sources ne sont plus exclusives : elles sont **fusionnées** puis dédupliquées,
ce qui élargit la couverture et réduit le risque de fil vide.

Points de rigueur :
  - horodatage **réel** issu du flux (`published_parsed`), jamais l'heure de
    collecte — un fil d'actualité sans vraie chronologie est trompeur ;
  - déduplication par titre normalisé (les mêmes dépêches circulent sur
    plusieurs fils) ;
  - tri antéchronologique et fenêtre de fraîcheur configurable.
"""

from __future__ import annotations

import datetime as dt
import logging
import re
import unicodedata
from dataclasses import asdict, dataclass

from app.config import settings
from app.providers.base import http_get_json, http_get_text

logger = logging.getLogger("macro.providers.news")

# Flux RSS gratuits. `category` alimente le filtrage dans l'application.
_RSS_FEEDS: tuple[tuple[str, str, str], ...] = (
    ("https://www.investing.com/rss/news_285.rss", "macro", "Investing — Économie"),
    ("https://www.investing.com/rss/news_1.rss", "markets", "Investing — Marchés"),
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "markets", "MarketWatch"),
    ("https://feeds.marketwatch.com/marketwatch/marketpulse/", "markets", "MarketWatch — Pulse"),
    ("https://www.cnbc.com/id/20910258/device/rss/rss.html", "macro", "CNBC — Économie"),
    ("https://finance.yahoo.com/news/rssindex", "markets", "Yahoo Finance"),
    # Google Actualités : requêtes ciblées, utiles pour la couverture francophone.
    (
        "https://news.google.com/rss/search?q=inflation+OR+banque+centrale+OR+taux+directeur"
        "&hl=fr&gl=FR&ceid=FR:fr",
        "macro",
        "Google Actualités — Macro",
    ),
    (
        "https://news.google.com/rss/search?q=g%C3%A9opolitique+OR+sanctions+OR+conflit"
        "&hl=fr&gl=FR&ceid=FR:fr",
        "geopolitics",
        "Google Actualités — Géopolitique",
    ),
)

MAX_ITEMS = 60
FRESHNESS_HOURS = 72


@dataclass(slots=True)
class NewsItem:
    """Dépêche normalisée, prête à être classifiée puis affichée."""

    title: str
    url: str
    source: str
    ts: dt.datetime
    category: str  # macro | markets | geopolitics | central_bank

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ts"] = self.ts.isoformat()
        return data


# ── Déduplication ───────────────────────────────────────────────
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")


def _normalise(title: str) -> str:
    """Clé de dédup : minuscules, sans accents ni ponctuation."""
    text = unicodedata.normalize("NFKD", title.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return _SPACES.sub(" ", _PUNCT.sub(" ", text)).strip()


# ── Sources ─────────────────────────────────────────────────────
def _from_finnhub() -> list[NewsItem]:
    if not settings.finnhub_api_key:
        return []
    data = http_get_json(
        "https://finnhub.io/api/v1/news",
        params={"category": "general", "token": settings.finnhub_api_key},
    )
    if not isinstance(data, list):
        return []
    out: list[NewsItem] = []
    for item in data[:50]:
        title = str(item.get("headline", "")).strip()
        if not title:
            continue
        try:
            ts = dt.datetime.fromtimestamp(int(item.get("datetime", 0)), dt.UTC)
        except (ValueError, TypeError, OSError):
            ts = dt.datetime.now(dt.UTC)
        out.append(
            NewsItem(
                title=title,
                url=str(item.get("url", "")),
                source=str(item.get("source", "Finnhub")),
                ts=ts,
                category="macro",
            )
        )
    return out


def _entry_timestamp(entry) -> dt.datetime:
    """Horodatage réel de la dépêche, avec repli sur l'heure de collecte."""
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if not parsed:
            continue
        try:
            year, month, day, hour, minute, second = (int(v) for v in parsed[:6])
            return dt.datetime(year, month, day, hour, minute, second, tzinfo=dt.UTC)
        except (TypeError, ValueError):
            continue
    return dt.datetime.now(dt.UTC)


def _from_rss() -> list[NewsItem]:
    try:
        import feedparser
    except ImportError:
        logger.info("feedparser absent : flux RSS désactivés.")
        return []

    out: list[NewsItem] = []
    for url, category, label in _RSS_FEEDS:
        raw = http_get_text(url)
        if not raw:
            continue
        try:
            parsed = feedparser.parse(raw)
        except Exception as exc:
            logger.warning("Flux illisible (%s) : %s", label, exc)
            continue
        for entry in parsed.entries[:20]:
            title = str(entry.get("title", "")).strip()
            if not title:
                continue
            out.append(
                NewsItem(
                    title=title,
                    url=str(entry.get("link", "")),
                    source=label,
                    ts=_entry_timestamp(entry),
                    category=category,
                )
            )
    return out


# ── Agrégation ──────────────────────────────────────────────────
def fetch_news_items(max_items: int = MAX_ITEMS, freshness_hours: int = FRESHNESS_HOURS) -> list[NewsItem]:
    """Fil fusionné, dédupliqué, trié du plus récent au plus ancien."""
    collected = _from_finnhub() + _from_rss()
    if not collected:
        logger.info("Fil d'actualité vide (hors-ligne ou sources injoignables).")
        return []

    cutoff = dt.datetime.now(dt.UTC) - dt.timedelta(hours=freshness_hours)
    seen: set[str] = set()
    fresh: list[NewsItem] = []
    for item in collected:
        if item.ts < cutoff:
            continue
        key = _normalise(item.title)
        if not key or key in seen:
            continue
        seen.add(key)
        fresh.append(item)

    fresh.sort(key=lambda n: n.ts, reverse=True)
    logger.info("Fil d'actualité : %d dépêches retenues sur %d collectées.", len(fresh), len(collected))
    return fresh[:max_items]


def fetch_news() -> list[dict]:
    """Compatibilité : format dictionnaire consommé par le pipeline existant."""
    return [
        {"title": n.title, "url": n.url, "source": n.source, "ts": n.ts, "category": n.category}
        for n in fetch_news_items()
    ]

"""Ordonnanceur temps réel : rafraîchit le pipeline à intervalles réguliers.

Utilise APScheduler (BackgroundScheduler) démarré au boot de l'API.
Un seul job pilote le cycle complet ; sa cadence suit le plus court des
intervalles configurés (marché) tout en évitant de marteler les sources
lourdes (news/calendrier ont leur propre logique de fraîcheur en amont).
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.pipeline import refresh_news, run_pipeline
from app.platform_state import refresh_platform

logger = logging.getLogger("macro.scheduler")

_scheduler: BackgroundScheduler | None = None


def _full_cycle() -> None:
    """Cycle complet : scores macro puis consolidation plateforme."""
    run_pipeline()
    refresh_platform()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(daemon=True, timezone="UTC")

    # Cycle complet : données de marché, scores, régime, corrélations, calendrier.
    market_interval = max(60, settings.refresh_market_seconds)
    _scheduler.add_job(
        _full_cycle,
        "interval",
        seconds=market_interval,
        id="macro_cycle",
        max_instances=1,
        coalesce=True,
    )

    # Fil d'actualité : cadence propre, plus rapide, pour rester « en direct ».
    news_interval = max(60, settings.refresh_news_seconds)
    _scheduler.add_job(
        refresh_news,
        "interval",
        seconds=news_interval,
        id="news_feed",
        max_instances=1,
        coalesce=True,
    )

    _scheduler.start()
    logger.info(
        "Scheduler démarré (cycle complet %ss, fil d'actualité %ss).",
        market_interval,
        news_interval,
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler arrêté.")

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
from app.pipeline import run_pipeline

logger = logging.getLogger("macro.scheduler")

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(daemon=True, timezone="UTC")
    interval = max(60, settings.refresh_market_seconds)
    _scheduler.add_job(
        run_pipeline,
        "interval",
        seconds=interval,
        id="macro_cycle",
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("Scheduler démarré (cycle toutes les %ss).", interval)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler arrêté.")

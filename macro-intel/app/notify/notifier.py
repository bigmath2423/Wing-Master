"""Envoi des verdicts de fusion vers Telegram / Discord (ou log si non configuré)."""
from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger("macro.notify")


def _send_telegram(text: str) -> None:
    if not (settings.telegram_bot_token and settings.telegram_chat_id):
        return
    try:
        httpx.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as exc:
        logger.warning("Telegram indisponible : %s", exc)


def _send_discord(text: str) -> None:
    if not settings.discord_webhook_url:
        return
    try:
        httpx.post(settings.discord_webhook_url, json={"content": text}, timeout=10)
    except Exception as exc:
        logger.warning("Discord indisponible : %s", exc)


def notify(text: str) -> None:
    """Diffuse un message sur tous les canaux configurés."""
    logger.info("NOTIFY: %s", text)
    _send_telegram(text)
    _send_discord(text)

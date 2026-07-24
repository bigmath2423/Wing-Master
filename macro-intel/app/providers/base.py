"""Utilitaires communs aux providers."""
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("macro.providers")

DEFAULT_TIMEOUT = 12.0
_HEADERS = {"User-Agent": "MacroIntel/1.0 (+https://github.com/)"}


def http_get_json(url: str, params: dict | None = None, timeout: float = DEFAULT_TIMEOUT):
    """GET JSON défensif : renvoie None au lieu de lever en cas d'échec."""
    try:
        resp = httpx.get(url, params=params, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # réseau, TLS, quota, JSON invalide...
        logger.warning("http_get_json a échoué pour %s : %s", url, exc)
        return None


def http_get_text(url: str, timeout: float = DEFAULT_TIMEOUT) -> str | None:
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        logger.warning("http_get_text a échoué pour %s : %s", url, exc)
        return None

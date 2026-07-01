"""
utils/sessions.py
=================
Filtre de sessions de trading.

L'or (XAUUSD) a la meilleure liquidité/volatilité pendant les sessions de
Londres et New York. Ce module dit si l'heure courante (UTC) tombe dans une
session active, pour éviter de trader pendant les heures creuses (Asie tardive).
"""

from __future__ import annotations

from datetime import datetime, timezone


def active_sessions(sessions: dict, now: datetime | None = None) -> list[str]:
    """Retourne la liste des sessions actives à l'instant `now` (UTC).

    Chaque session est une plage (heure_début, heure_fin) en UTC.
    Gère les plages qui passent minuit (ex: (22, 6))."""
    now = now or datetime.now(timezone.utc)
    hour = now.hour
    active = []
    for name, (start, end) in sessions.items():
        if start <= end:
            in_session = start <= hour < end
        else:  # plage à cheval sur minuit
            in_session = hour >= start or hour < end
        if in_session:
            active.append(name)
    return active


def is_trading_time(config, now: datetime | None = None):
    """Retourne (autorisé: bool, sessions_actives: list[str]).

    Si le filtre est désactivé, tout est autorisé."""
    if not getattr(config, "SESSION_FILTER_ENABLED", False):
        return True, []
    active = active_sessions(config.TRADING_SESSIONS, now)
    return (len(active) > 0), active

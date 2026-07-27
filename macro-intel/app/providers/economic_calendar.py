"""Calendrier économique (CPI, NFP, FOMC, BCE, PIB, PMI, chômage...).

Trois niveaux de source, du plus précis au plus robuste :
  1. **FMP** (Financial Modeling Prep) si `FMP_API_KEY` — dates et consensus réels.
  2. **Trading Economics** si `TRADING_ECONOMICS_KEY` — alternative.
  3. **Calendrier récurrent généré** — reconstruit les rendez-vous à partir des
     règles de publication officielles (NFP le 1er vendredi, inscriptions au
     chômage chaque jeudi, CPI mi-mois...). Explicitement étiqueté comme
     *estimation* : l'application ne présente jamais une date reconstruite comme
     une date confirmée.

Chaque entrée est rattachée à un **thème macro** (`app/ai/knowledge.py`), ce qui
permet d'expliquer ce qui se joue et quels marchés sont concernés — la valeur
ajoutée par rapport à un calendrier brut.
"""

from __future__ import annotations

import datetime as dt
import logging
from dataclasses import asdict, dataclass, field

from app.config import settings
from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.calendar")

_HIGH_IMPACT = {"CPI", "Nonfarm", "NFP", "FOMC", "Fed", "ECB", "Interest Rate", "PCE", "Unemployment"}


@dataclass(slots=True)
class CalendarEntry:
    """Rendez-vous économique, enrichi de son contexte d'interprétation."""

    event_time: str  # ISO 8601 UTC
    country: str
    event: str
    importance: int  # 1 (faible) .. 3 (majeure)
    actual: str = ""
    forecast: str = ""
    previous: str = ""
    topic: str = ""  # clé de thème macro (inflation, rates, employment...)
    watch: str = ""  # ce qu'il faut regarder dans la publication
    estimated_date: bool = False  # True si la date est reconstruite, pas confirmée
    source: str = "fallback"

    def to_dict(self) -> dict:
        return asdict(self)


# ── Rattachement thème + « ce qu'il faut regarder » ──────────────
_TOPIC_RULES: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (
        ("cpi", "inflation", "pce", "ppi", "prix"),
        "inflation",
        "La composante sous-jacente (cœur) et les services comptent souvent plus que le chiffre global.",
    ),
    (
        ("fomc", "interest rate", "taux directeur", "rate decision", "bce", "ecb", "minutes"),
        "rates",
        "Le communiqué, les projections et la conférence de presse pèsent souvent plus que la décision elle-même.",
    ),
    (
        ("nonfarm", "nfp", "payroll", "unemployment", "chômage", "jobless", "emploi"),
        "employment",
        "Le salaire horaire moyen et le taux de participation nuancent le chiffre principal.",
    ),
    (
        ("gdp", "pib", "pmi", "ism", "retail", "production"),
        "growth",
        "La tendance sur plusieurs mois est plus informative qu'une publication isolée.",
    ),
    (
        ("crude", "petroleum", "inventories", "brut", "pétrole", "opec", "opep", "gaz"),
        "energy",
        "L'écart aux attentes et la dynamique des stocks sur plusieurs semaines guident la lecture.",
    ),
)


def _classify(event_name: str) -> tuple[str, str]:
    """Renvoie (clé de thème, conseil de lecture) pour un intitulé d'événement."""
    lowered = event_name.lower()
    for keywords, topic, watch in _TOPIC_RULES:
        if any(k in lowered for k in keywords):
            return topic, watch
    return "", "Comparer la publication au consensus et à la valeur précédente."


def _importance(event_name: str) -> int:
    name = event_name.lower()
    if any(k in name for k in ("fomc", "nonfarm", "cpi", "interest rate", "taux directeur")):
        return 3
    if any(k.lower() in name for k in _HIGH_IMPACT):
        return 2
    return 1


# ── Source 1 : FMP ───────────────────────────────────────────────
def _from_fmp(days: int) -> list[CalendarEntry]:
    if not settings.fmp_api_key:
        return []
    today = dt.datetime.now(dt.UTC).date()
    data = http_get_json(
        "https://financialmodelingprep.com/api/v3/economic_calendar",
        params={
            "from": today.isoformat(),
            "to": (today + dt.timedelta(days=days)).isoformat(),
            "apikey": settings.fmp_api_key,
        },
    )
    if not isinstance(data, list):
        return []
    out: list[CalendarEntry] = []
    for item in data:
        name = str(item.get("event", "")).strip()
        if not name:
            continue
        topic, watch = _classify(name)
        out.append(
            CalendarEntry(
                event_time=str(item.get("date", "")),
                country=str(item.get("country", "")),
                event=name,
                importance=_importance(name),
                actual=str(item.get("actual", "") or ""),
                forecast=str(item.get("estimate", "") or ""),
                previous=str(item.get("previous", "") or ""),
                topic=topic,
                watch=watch,
                estimated_date=False,
                source="fmp",
            )
        )
    return out


# ── Source 2 : Trading Economics ─────────────────────────────────
def _from_trading_economics(days: int) -> list[CalendarEntry]:
    if not settings.trading_economics_key:
        return []
    today = dt.datetime.now(dt.UTC).date()
    data = http_get_json(
        f"https://api.tradingeconomics.com/calendar/country/all/"
        f"{today.isoformat()}/{(today + dt.timedelta(days=days)).isoformat()}",
        params={"c": settings.trading_economics_key, "f": "json"},
    )
    if not isinstance(data, list):
        return []
    out: list[CalendarEntry] = []
    for item in data:
        name = str(item.get("Event", "")).strip()
        if not name:
            continue
        topic, watch = _classify(name)
        out.append(
            CalendarEntry(
                event_time=str(item.get("Date", "")),
                country=str(item.get("Country", "")),
                event=name,
                importance=int(item.get("Importance", 1) or 1),
                actual=str(item.get("Actual", "") or ""),
                forecast=str(item.get("Forecast", "") or ""),
                previous=str(item.get("Previous", "") or ""),
                topic=topic,
                watch=watch,
                estimated_date=False,
                source="trading_economics",
            )
        )
    return out


# ── Source 3 : calendrier récurrent reconstruit ──────────────────
# Règles de publication réelles des principales statistiques américaines.
def _first_weekday(year: int, month: int, weekday: int) -> dt.date:
    """Premier `weekday` (0=lundi) du mois donné."""
    d = dt.date(year, month, 1)
    return d + dt.timedelta(days=(weekday - d.weekday()) % 7)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> dt.date:
    """N-ième `weekday` du mois (n commence à 1)."""
    return _first_weekday(year, month, weekday) + dt.timedelta(weeks=n - 1)


def _at(day: dt.date, hour: int, minute: int = 0) -> str:
    return dt.datetime(day.year, day.month, day.day, hour, minute, tzinfo=dt.UTC).isoformat()


def _recurring(days: int) -> list[CalendarEntry]:
    """Reconstruit les rendez-vous macro majeurs sur la fenêtre demandée.

    Horaires en UTC, d'après les heures de publication habituelles :
      - NFP / CPI / PPI / ventes au détail : 12h30 UTC (8h30 ET)
      - PMI ISM : 14h00 UTC (10h00 ET)
      - Stocks de brut EIA : 14h30 UTC, le mercredi
      - Décision FOMC : 18h00 UTC (14h00 ET)
    """
    now = dt.datetime.now(dt.UTC)
    today = now.date()
    horizon = today + dt.timedelta(days=days)
    out: list[CalendarEntry] = []

    def add(day: dt.date, hour: int, minute: int, country: str, event: str, importance: int) -> None:
        if not (today <= day <= horizon):
            return
        topic, watch = _classify(event)
        out.append(
            CalendarEntry(
                event_time=_at(day, hour, minute),
                country=country,
                event=event,
                importance=importance,
                topic=topic,
                watch=watch,
                estimated_date=True,
                source="recurring",
            )
        )

    # Parcourt les mois couverts par la fenêtre.
    months: list[tuple[int, int]] = []
    cursor = dt.date(today.year, today.month, 1)
    while cursor <= horizon:
        months.append((cursor.year, cursor.month))
        cursor = dt.date(cursor.year + (cursor.month == 12), (cursor.month % 12) + 1, 1)

    for year, month in months:
        # Emploi : NFP le 1er vendredi du mois.
        add(
            _first_weekday(year, month, 4),
            12,
            30,
            "US",
            "NFP — créations d'emplois non agricoles (États-Unis)",
            3,
        )
        # ISM manufacturier : 1er jour ouvré ; ISM services : ~3e jour ouvré.
        add(_first_weekday(year, month, 0), 14, 0, "US", "ISM manufacturier (PMI)", 2)
        add(_first_weekday(year, month, 2), 14, 0, "US", "ISM services (PMI)", 2)
        # CPI : ~2e mardi/mercredi du mois ; PPI le lendemain.
        cpi_day = _nth_weekday(year, month, 1, 2)
        add(cpi_day, 12, 30, "US", "CPI — inflation des prix à la consommation (États-Unis)", 3)
        add(cpi_day + dt.timedelta(days=1), 12, 30, "US", "PPI — prix à la production (États-Unis)", 2)
        # Ventes au détail : ~mi-mois.
        add(_nth_weekday(year, month, 3, 3), 12, 30, "US", "Ventes au détail (États-Unis)", 2)
        # PCE : dernier vendredi du mois (mesure d'inflation préférée de la Fed).
        last_friday = _nth_weekday(year, month, 4, 4)
        if (last_friday + dt.timedelta(weeks=1)).month == month:
            last_friday += dt.timedelta(weeks=1)
        add(last_friday, 12, 30, "US", "PCE — inflation (indicateur privilégié de la Fed)", 3)
        # PIB : ~4e jeudi.
        add(_nth_weekday(year, month, 3, 4), 12, 30, "US", "PIB — croissance trimestrielle (estimation)", 2)
        # BCE : réunion de politique monétaire ~toutes les 6 semaines (mois pairs).
        if month % 2 == 0:
            add(_nth_weekday(year, month, 3, 2), 12, 15, "EU", "BCE — décision de politique monétaire", 3)
        # FOMC : 8 réunions par an (mois hors mars/août/octobre/décembre décalés).
        if month in (1, 3, 5, 6, 7, 9, 11, 12):
            add(
                _nth_weekday(year, month, 2, 3),
                18,
                0,
                "US",
                "FOMC — décision de taux directeur et projections",
                3,
            )

    # Hebdomadaires : inscriptions au chômage (jeudi), stocks de brut (mercredi).
    day = today
    while day <= horizon:
        if day.weekday() == 3:
            add(day, 12, 30, "US", "Inscriptions hebdomadaires au chômage", 1)
        if day.weekday() == 2:
            add(day, 14, 30, "US", "Stocks de pétrole brut (EIA)", 2)
        day += dt.timedelta(days=1)

    out.sort(key=lambda e: e.event_time)
    return out


# ── Points d'entrée ──────────────────────────────────────────────
def fetch_calendar_entries(days: int = 21) -> list[CalendarEntry]:
    """Calendrier sur `days` jours. Renvoie toujours une liste exploitable."""
    entries = _from_fmp(days) or _from_trading_economics(days)
    if entries:
        entries.sort(key=lambda e: e.event_time)
        return entries
    logger.info("Calendrier : aucune source externe, reconstruction des rendez-vous récurrents.")
    return _recurring(days)


def fetch_calendar() -> list[dict]:
    """Compatibilité : format dictionnaire utilisé par le pipeline existant."""
    return [
        {
            "event_time": e.event_time,
            "country": e.country,
            "event": e.event,
            "importance": e.importance,
            "actual": e.actual,
            "forecast": e.forecast,
            "previous": e.previous,
        }
        for e in fetch_calendar_entries()
    ]


@dataclass(slots=True)
class CalendarSummary:
    """Vue d'ensemble du risque événementiel à venir."""

    entries: list[CalendarEntry] = field(default_factory=list)
    next_major: CalendarEntry | None = None
    high_impact_48h: int = 0
    estimated: bool = False
    source: str = "fallback"


def summarise_calendar(days: int = 21) -> CalendarSummary:
    """Calendrier + prochain rendez-vous majeur + densité d'événements à 48 h."""
    entries = fetch_calendar_entries(days)
    now = dt.datetime.now(dt.UTC)
    horizon = now + dt.timedelta(hours=48)

    upcoming: list[CalendarEntry] = []
    high_impact = 0
    next_major: CalendarEntry | None = None

    for entry in entries:
        try:
            when = dt.datetime.fromisoformat(entry.event_time.replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=dt.UTC)
        except (ValueError, TypeError):
            continue
        if when < now - dt.timedelta(hours=12):
            continue  # publication déjà passée
        upcoming.append(entry)
        if entry.importance >= 3:
            if next_major is None:
                next_major = entry
            if now <= when <= horizon:
                high_impact += 1

    source = entries[0].source if entries else "fallback"
    return CalendarSummary(
        entries=upcoming[:40],
        next_major=next_major,
        high_impact_48h=high_impact,
        estimated=source == "recurring",
        source=source,
    )

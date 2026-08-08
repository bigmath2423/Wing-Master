"""État consolidé de la plateforme : ce que l'application affiche.

Assemble, en une structure unique et sérialisable :
  - le régime de marché dominant + ses moteurs ;
  - les indicateurs clés (taux, courbe, dollar, volatilité, inflation, risque géo) ;
  - le contexte par actif (score/biais/confiance, hérité du moteur existant) ;
  - les prix multi-actifs ;
  - les événements analysés par l'IA (résumé, mécanismes, scénarios, priorité) ;
  - les corrélations inter-marchés ;
  - le positionnement (COT) et l'énergie (stocks de brut) ;
  - un briefing de synthèse.

Ce module **compose** : il ne recalcule pas ce que `pipeline` produit déjà. Il est
rafraîchi par le scheduler, en parallèle du cycle de scoring existant.
"""

from __future__ import annotations

import datetime as dt
import logging
import threading

from app.ai import guardrails
from app.ai.analyst import EventAnalysis, analyse_batch
from app.analysis.correlations import CorrelationReading, correlation_matrix, describe
from app.analysis.regime import RegimeReading, detect_regime
from app.analysis.yield_curve import CurveReading, analyse_curve
from app.pipeline import STATE
from app.providers import market_extended
from app.providers.cot import CotReading, fetch_cot
from app.providers.economic_calendar import CalendarSummary, summarise_calendar
from app.providers.energy import EnergyReading, fetch_energy

logger = logging.getLogger("macro.platform")

# Séries utilisées pour les corrélations (prix + séries FRED).
_CORR_PRICE_KEYS = [
    "commodity.gold",
    "commodity.oil",
    "index.spx",
    "crypto.btc",
]


class PlatformState:
    """État thread-safe de la plateforme, servi par l'API."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.generated_at: dt.datetime | None = None
        self.regime: RegimeReading | None = None
        self.curve: CurveReading | None = None
        self.prices: dict[str, dict[str, float]] = {}
        self.analyses: list[EventAnalysis] = []
        self.correlations: list[CorrelationReading] = []
        self.cot: list[CotReading] = []
        self.energy: EnergyReading | None = None
        self.calendar: CalendarSummary | None = None
        self.extras: dict[str, float | None] = {}
        self.briefing: str = ""

    def update(self, **kwargs) -> None:
        with self._lock:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def read(self) -> dict:
        with self._lock:
            return {
                "generated_at": self.generated_at,
                "regime": self.regime,
                "curve": self.curve,
                "prices": dict(self.prices),
                "analyses": list(self.analyses),
                "correlations": list(self.correlations),
                "cot": list(self.cot),
                "energy": self.energy,
                "calendar": self.calendar,
                "extras": dict(self.extras),
                "briefing": self.briefing,
            }


PLATFORM = PlatformState()


def _growth_momentum(prices: dict[str, dict[str, float]]) -> float:
    """Proxy d'élan de croissance à partir du comportement des actifs cycliques.

    Les indices actions et le cuivre réagissent avant les statistiques
    officielles ; on s'en sert comme indicateur avancé grossier, borné [-1, 1].
    """
    signals: list[float] = []
    for key in ("index.spx", "commodity.copper", "commodity.oil"):
        entry = prices.get(key)
        if entry and "change_pct" in entry:
            signals.append(max(-1.0, min(1.0, entry["change_pct"] / 2.0)))
    if not signals:
        return 0.0
    return round(sum(signals) / len(signals), 3)


def _format_delay(target: dt.datetime, now: dt.datetime) -> str:
    """Délai lisible avant un rendez-vous (« dans 3 h », « dans 2 jours »)."""
    delta = target - now
    hours = delta.total_seconds() / 3600
    if hours < 0:
        return "imminent"
    if hours < 1:
        return f"dans {int(delta.total_seconds() // 60)} min"
    if hours < 36:
        return f"dans {int(hours)} h"
    return f"dans {int(hours // 24)} jours"


def build_briefing(
    regime: RegimeReading,
    curve: CurveReading,
    analyses: list[EventAnalysis],
    extras: dict[str, float | None],
    calendar: CalendarSummary | None = None,
) -> str:
    """Rédige la synthèse d'ouverture — descriptive, sans aucune recommandation."""
    parts: list[str] = []

    parts.append(
        f"Régime macro dominant : {regime.label.lower()} "
        f"(confiance {regime.confidence:.0f} %). {regime.description}"
    )
    if regime.drivers:
        parts.append("Facteurs déterminants : " + ", ".join(regime.drivers) + ".")

    if curve.spread_10y2y is not None:
        parts.append(f"{curve.label} (pente 10a-2a : {curve.spread_10y2y:+.2f} pt). {curve.interpretation}")

    vix = extras.get("vix")
    if vix is not None:
        tone = "élevée" if vix >= 22 else "contenue" if vix <= 15 else "modérée"
        parts.append(f"La volatilité implicite est {tone} (VIX {vix:.1f}).")

    # Risque événementiel : ce qui arrive pèse autant que ce qui vient de se passer.
    if calendar is not None:
        now = dt.datetime.now(dt.UTC)
        if calendar.next_major is not None:
            try:
                when = dt.datetime.fromisoformat(calendar.next_major.event_time.replace("Z", "+00:00"))
                if when.tzinfo is None:
                    when = when.replace(tzinfo=dt.UTC)
                delay = _format_delay(when, now)
            except (ValueError, TypeError):
                delay = "à venir"
            estimate_note = " (date reconstruite, à confirmer)" if calendar.estimated else ""
            parts.append(f"Prochain rendez-vous majeur : {calendar.next_major.event} {delay}{estimate_note}.")
        if calendar.high_impact_48h:
            parts.append(
                f"{calendar.high_impact_48h} publication(s) à fort impact dans les 48 heures : "
                "la volatilité événementielle est un facteur à intégrer."
            )

    priorities = [a for a in analyses if a.priority in ("critical", "high")]
    if priorities:
        titles = "; ".join(a.title[:80] for a in priorities[:3])
        parts.append(f"Sujets prioritaires du moment : {titles}.")
    else:
        parts.append("Aucun événement de priorité haute n'est identifié dans le flux récent.")

    parts.append(
        "Cette synthèse décrit le contexte. Elle ne comporte aucune orientation "
        "d'exécution : l'interprétation et la décision restent au lecteur."
    )
    return guardrails.enforce(" ".join(parts)).text


def refresh_platform() -> dict:
    """Cycle de rafraîchissement de la couche plateforme. Ne lève jamais."""
    logger.info("Rafraîchissement plateforme : marchés étendus, IA, corrélations...")

    macro = STATE.snapshot()
    market = macro["market"]
    geo = macro["geo"]

    # 1) Courbe des taux et volatilité
    try:
        extras = market_extended.fetch_curve_and_vol()
    except Exception as exc:
        logger.warning("Extensions de marché indisponibles : %s", exc)
        extras = {}

    # Enrichit l'objet MarketReadings partagé (champs optionnels).
    for field_name in ("us2y", "us30y", "curve_10y2y", "vix", "vix_change_pct"):
        value = extras.get(field_name)
        if value is not None:
            setattr(market, field_name, value)

    # 2) Prix multi-actifs
    try:
        prices = market_extended.fetch_prices()
    except Exception as exc:
        logger.warning("Prix indisponibles : %s", exc)
        prices = {}

    # 3) Régime et courbe
    curve = analyse_curve(market.us2y, market.us10y, market.us30y)
    if curve.spread_10y2y is not None and market.curve_10y2y is None:
        market.curve_10y2y = curve.spread_10y2y
    regime = detect_regime(market, geo, growth_momentum=_growth_momentum(prices))

    # 4) Analyses IA des événements récents (news classifiées + géopolitique)
    events: list[dict] = [
        {"title": n.title, "category": n.category, "severity": n.severity} for n in macro["news"]
    ]
    for headline in geo.top_events[:4]:
        events.append({"title": headline, "category": "geopolitics", "severity": geo.risk_index})
    try:
        analyses = analyse_batch(events, limit=10)
    except Exception as exc:
        logger.warning("Analyses IA indisponibles : %s", exc)
        analyses = []

    # 5) Corrélations (historiques de prix + séries FRED)
    try:
        series = market_extended.fetch_history(_CORR_PRICE_KEYS)
        series.update(market_extended.fetch_fred_history("DFII10", "rates.real10y"))
        series.update(market_extended.fetch_fred_history("DTWEXBGS", "market.dxy"))
        series.update(market_extended.fetch_fred_history("VIXCLS", "market.vix"))
        series.update(market_extended.fetch_fred_history("DGS10", "rates.us10y"))
        correlations = correlation_matrix(series)
    except Exception as exc:
        logger.warning("Corrélations indisponibles : %s", exc)
        correlations = []

    # 6) Positionnement et énergie
    try:
        cot = fetch_cot()
    except Exception as exc:
        logger.warning("COT indisponible : %s", exc)
        cot = []
    try:
        energy = fetch_energy()
    except Exception as exc:
        logger.warning("Énergie indisponible : %s", exc)
        energy = None

    # 7) Calendrier économique (risque événementiel à venir)
    try:
        calendar = summarise_calendar()
    except Exception as exc:
        logger.warning("Calendrier indisponible : %s", exc)
        calendar = None

    briefing = build_briefing(regime, curve, analyses, extras, calendar)

    PLATFORM.update(
        generated_at=dt.datetime.now(dt.UTC),
        regime=regime,
        curve=curve,
        prices=prices,
        analyses=analyses,
        correlations=correlations,
        cot=cot,
        energy=energy,
        calendar=calendar,
        extras=extras,
        briefing=briefing,
    )
    logger.info(
        "Plateforme à jour — régime=%s (%.0f%%), %d analyses, %d corrélations, %d prix",
        regime.regime,
        regime.confidence,
        len(analyses),
        len(correlations),
        len(prices),
    )
    return PLATFORM.read()


def correlation_descriptions(readings: list[CorrelationReading]) -> list[str]:
    """Phrases descriptives des corrélations (fenêtre 30 jours en priorité)."""
    return [describe(r) for r in readings if r.window_days == 30 and r.value is not None]

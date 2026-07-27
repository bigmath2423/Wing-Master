"""Analyste IA : transforme un événement en explication structurée.

Sortie produite pour chaque événement notable :
  - résumé court                     (« ce qui s'est passé »)
  - pourquoi c'est important         (« so what »)
  - marchés concernés                (avec sens d'impact historique)
  - mécanisme économique             (chaîne causale)
  - scénarios possibles              (2 à 3 issues descriptives)
  - niveau de confiance              (0..100)
  - priorité                         (critical | high | normal | low)

Deux moteurs :
  * **déterministe** (par défaut) : s'appuie sur la base de mécanismes
    (`knowledge.py`) — fonctionne hors-ligne, sans clé, de façon reproductible ;
  * **LLM** (optionnel) : enrichit le résumé et les scénarios si une clé est
    configurée. Sa sortie traverse toujours les garde-fous.

Aucun texte n'est exposé sans passer par `guardrails.enforce()`.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field

from app.ai import guardrails
from app.ai.knowledge import Topic, detect_topics, topic_for_category
from app.config import settings

logger = logging.getLogger("macro.ai.analyst")

PRIORITIES = ("low", "normal", "high", "critical")


@dataclass(slots=True)
class EventAnalysis:
    """Analyse structurée d'un événement — descriptive, jamais prescriptive."""

    title: str
    category: str
    summary: str
    why_it_matters: str
    mechanism: str
    markets: dict[str, str] = field(default_factory=dict)
    scenarios: list[str] = field(default_factory=list)
    confidence: float = 0.0
    priority: str = "normal"
    topics: list[str] = field(default_factory=list)
    engine: str = "rules"  # "rules" | "llm"
    disclaimer: str = guardrails.DISCLAIMER

    def to_dict(self) -> dict:
        return asdict(self)


# ── Priorisation ────────────────────────────────────────────────
_CRITICAL_MARKERS = (
    "fomc", "guerre", "war", "invasion", "krach", "défaut souverain", "sovereign default",
)
_HIGH_MARKERS = (
    "cpi", "nfp", "nonfarm", "inflation", "taux directeur", "relève ses taux",
    "baisse ses taux", "rate decision", "rate hike", "rate cut", "sanction",
    "opep", "opec", "récession", "recession", "banque centrale", "fed ", "bce ",
)


def compute_priority(title: str, category: str, severity: float) -> str:
    """Priorité d'affichage : ce que le trader doit regarder en premier."""
    lowered = title.lower()
    if any(m in lowered for m in _CRITICAL_MARKERS) or severity >= 0.85:
        return "critical"
    if any(m in lowered for m in _HIGH_MARKERS) or severity >= 0.6:
        return "high"
    if severity >= 0.3 or category in ("central_bank", "geopolitics"):
        return "normal"
    return "low"


def compute_confidence(topics: list[Topic], severity: float, engine: str) -> float:
    """Confiance de l'analyse : couverture thématique + netteté du signal source.

    Volontairement plafonnée : une analyse macro reste incertaine par nature.
    """
    coverage = min(len(topics) / 2.0, 1.0)  # 2 thèmes identifiés = couverture pleine
    clarity = min(max(severity, 0.0), 1.0)
    base = 100.0 * (0.55 * coverage + 0.45 * clarity)
    if engine == "llm":
        base += 5.0  # nuance sémantique supérieure
    return round(min(base, 90.0), 0)  # jamais de fausse certitude


# ── Moteur déterministe ─────────────────────────────────────────
def _analyse_rules(title: str, category: str, severity: float) -> EventAnalysis:
    topics = detect_topics(title) or [topic_for_category(category)]
    primary = topics[0]

    markets: dict[str, str] = {}
    scenarios: list[str] = []
    for topic in topics:
        markets.update(topic.markets)
        for scenario in topic.scenarios:
            if scenario not in scenarios:
                scenarios.append(scenario)

    mechanism = " ".join(t.mechanism for t in topics[:2])
    why = primary.why
    if len(topics) > 1:
        why += f" Ce sujet croise également : {topics[1].label.lower()}."

    summary = (
        f"{title.strip()} — sujet rattaché à « {primary.label} ». "
        f"Cet élément agit d'abord sur : {', '.join(list(markets)[:4])}."
    )

    return EventAnalysis(
        title=title,
        category=category,
        summary=summary,
        why_it_matters=why,
        mechanism=mechanism,
        markets=markets,
        scenarios=scenarios[:3],
        confidence=compute_confidence(topics, severity, "rules"),
        priority=compute_priority(title, category, severity),
        topics=[t.key for t in topics],
        engine="rules",
    )


# ── Moteur LLM (optionnel, enrichit le déterministe) ────────────
_LLM_PROMPT = """Analyse cet événement macroéconomique pour un trader.

Événement : {title}
Catégorie : {category}
Thèmes identifiés : {topics}

Réponds UNIQUEMENT en JSON avec ces clés :
{{
  "summary": "2 phrases factuelles décrivant l'événement et sa portée",
  "why_it_matters": "1 à 2 phrases sur son importance macroéconomique",
  "mechanism": "la chaîne causale économique, 2 phrases maximum",
  "scenarios": ["scénario 1", "scénario 2", "scénario 3"],
  "confidence": 0-100
}}

Reste strictement descriptif. N'emploie aucun verbe d'action de marché."""


def _analyse_llm(title: str, category: str, severity: float) -> EventAnalysis | None:
    """Enrichissement LLM. Renvoie None en cas d'indisponibilité (repli assuré)."""
    try:
        import anthropic

        topics = detect_topics(title) or [topic_for_category(category)]
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=settings.ai_model,
            max_tokens=900,
            system=guardrails.SYSTEM_RULES,
            messages=[
                {
                    "role": "user",
                    "content": _LLM_PROMPT.format(
                        title=title,
                        category=category,
                        topics=", ".join(t.label for t in topics),
                    ),
                }
            ],
        )
        raw = message.content[0].text.strip()
        raw = raw[raw.find("{") : raw.rfind("}") + 1]
        data = json.loads(raw)

        markets: dict[str, str] = {}
        for topic in topics:
            markets.update(topic.markets)

        return EventAnalysis(
            title=title,
            category=category,
            summary=str(data.get("summary", "")),
            why_it_matters=str(data.get("why_it_matters", "")),
            mechanism=str(data.get("mechanism", "")),
            markets=markets,
            scenarios=[str(s) for s in data.get("scenarios", [])][:3],
            confidence=min(float(data.get("confidence", 60)), 90.0),
            priority=compute_priority(title, category, severity),
            topics=[t.key for t in topics],
            engine="llm",
        )
    except Exception as exc:  # quota, réseau, JSON invalide...
        logger.warning("Analyse LLM indisponible, repli déterministe : %s", exc)
        return None


# ── Point d'entrée ──────────────────────────────────────────────
def analyse_event(title: str, category: str = "news", severity: float = 0.4) -> EventAnalysis:
    """Analyse un événement. LLM si configuré, sinon moteur déterministe.

    Tout texte renvoyé a traversé les garde-fous anti-signal.
    """
    analysis: EventAnalysis | None = None
    if settings.ai_enabled:
        analysis = _analyse_llm(title, category, severity)
    if analysis is None:
        analysis = _analyse_rules(title, category, severity)

    # Garde-fous : on assainit chaque champ textuel exposé.
    analysis.summary = guardrails.enforce(analysis.summary).text
    analysis.why_it_matters = guardrails.enforce(analysis.why_it_matters).text
    analysis.mechanism = guardrails.enforce(analysis.mechanism).text
    analysis.scenarios, violations = guardrails.enforce_many(analysis.scenarios)
    if violations:
        logger.info("Garde-fous appliqués (%d motif(s)) sur : %s", len(violations), title[:70])
    return analysis


def analyse_batch(events: list[dict], limit: int = 12) -> list[EventAnalysis]:
    """Analyse un lot d'événements, triés par priorité décroissante."""
    out: list[EventAnalysis] = []
    for ev in events[:limit]:
        title = str(ev.get("title", "")).strip()
        if not title:
            continue
        out.append(
            analyse_event(
                title,
                category=str(ev.get("category", "news")),
                severity=float(ev.get("severity", 0.4) or 0.4),
            )
        )
    out.sort(key=lambda a: (PRIORITIES.index(a.priority), a.confidence), reverse=True)
    return out

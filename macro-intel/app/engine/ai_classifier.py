"""Classification de l'impact des news sur GOLD / BTC / matières premières.

Deux modes :
  1. IA (Claude) si ANTHROPIC_API_KEY est défini — nuance sémantique.
  2. Moteur de règles (lexique pondéré) sinon — déterministe, hors-ligne.

Convention d'impact : contribution signée -100..+100 par actif.
Pour l'or, un contexte de peur / tension / dollar faible => positif.
"""
from __future__ import annotations

import json
import logging

from app.config import settings
from app.domain import NewsImpact

logger = logging.getLogger("macro.engine.ai")

# ── Lexique de règles (fallback déterministe) ───────────────────
# Chaque terme -> (impact_gold, impact_btc, impact_commodities, sévérité)
_LEXICON: dict[str, tuple[float, float, float, float]] = {
    # Risque / valeur refuge -> or +, btc parfois +, risk-off
    "war": (35, 10, 15, 0.9),
    "guerre": (35, 10, 15, 0.9),
    "invasion": (35, 5, 15, 0.9),
    "sanction": (25, 5, 20, 0.7),
    "conflict": (25, 5, 10, 0.7),
    "attack": (28, 5, 12, 0.8),
    "crisis": (22, 0, 8, 0.7),
    "recession": (18, -10, -15, 0.7),
    "default": (20, -5, -5, 0.7),
    # Inflation -> or + (couverture), dépend des taux réels
    "inflation surges": (25, 10, 15, 0.7),
    "hot cpi": (20, 5, 10, 0.6),
    "rate cut": (30, 20, 10, 0.8),      # baisse de taux -> or +
    "dovish": (25, 15, 8, 0.6),
    "rate hike": (-30, -20, -10, 0.8),  # hausse de taux -> or -
    "hawkish": (-25, -12, -8, 0.6),
    "strong dollar": (-25, -10, -12, 0.6),
    "dollar rallies": (-22, -8, -10, 0.6),
    "weak dollar": (22, 10, 12, 0.6),
    "risk-on": (-12, 15, 8, 0.4),
    "rally": (-8, 10, 6, 0.3),
    "selloff": (12, -12, -8, 0.5),
}


def _rule_based(title: str, category: str) -> NewsImpact:
    text = title.lower()
    g = b = c = sev = 0.0
    hits = 0
    for term, (ig, ib, ic, s) in _LEXICON.items():
        if term in text:
            g += ig
            b += ib
            c += ic
            sev = max(sev, s)
            hits += 1
    if hits == 0:
        # Neutre mais légèrement pondéré par la catégorie.
        base = {"central_bank": 0.3, "geopolitics": 0.4}.get(category, 0.1)
        return NewsImpact(title=title, category=category, severity=base)

    # Amortit l'accumulation quand plusieurs termes matchent.
    damp = 1.0 / (1.0 + 0.35 * (hits - 1))
    return NewsImpact(
        title=title,
        category=category,
        severity=round(sev, 2),
        impact_gold=round(max(-100, min(100, g * damp)), 1),
        impact_btc=round(max(-100, min(100, b * damp)), 1),
        impact_commodities=round(max(-100, min(100, c * damp)), 1),
    )


_AI_PROMPT = (
    "Tu es un analyste macro. Pour ce titre de news, estime l'impact sur "
    "l'or (XAUUSD), le BTC et les matières premières. Réponds UNIQUEMENT en "
    "JSON: {{\"gold\": int, \"btc\": int, \"commodities\": int, \"severity\": float}} "
    "où gold/btc/commodities sont dans [-100,100] (positif = haussier) et "
    "severity dans [0,1]. Titre: {title}"
)


def _ai_based(title: str, category: str) -> NewsImpact | None:
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.ai_model,
            max_tokens=200,
            messages=[{"role": "user", "content": _AI_PROMPT.format(title=title)}],
        )
        raw = msg.content[0].text.strip()
        raw = raw[raw.find("{") : raw.rfind("}") + 1]
        data = json.loads(raw)
        return NewsImpact(
            title=title,
            category=category,
            severity=float(data.get("severity", 0.3)),
            impact_gold=float(data.get("gold", 0)),
            impact_btc=float(data.get("btc", 0)),
            impact_commodities=float(data.get("commodities", 0)),
        )
    except Exception as exc:  # quota, réseau, parsing...
        logger.warning("Classification IA indisponible, repli sur règles : %s", exc)
        return None


def classify(title: str, category: str = "macro") -> NewsImpact:
    """Classifie un titre. IA si dispo, sinon règles."""
    if settings.ai_enabled:
        result = _ai_based(title, category)
        if result is not None:
            return result
    return _rule_based(title, category)


def classify_batch(news: list[dict]) -> list[NewsImpact]:
    return [classify(n.get("title", ""), n.get("category", "macro")) for n in news if n.get("title")]

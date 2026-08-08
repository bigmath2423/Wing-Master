"""Garde-fous anti-signal : la plateforme explique, elle n'ordonne jamais.

Deux niveaux de défense :
  1. **Consigne système** injectée dans chaque appel LLM (`SYSTEM_RULES`).
  2. **Filtre de sortie** déterministe (`enforce`) qui inspecte le texte produit,
     qu'il vienne du LLM ou d'un gabarit interne, et neutralise toute formulation
     prescriptive (« achetez », « vendez », « entrée », « SL/TP »...).

Le filtre est volontairement conservateur : il préfère reformuler au conditionnel
descriptif plutôt que laisser passer un impératif de trading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Consigne système, injectée dans tous les prompts (Tome 5).
SYSTEM_RULES = (
    "Tu es un analyste macroéconomique. Ton rôle est d'EXPLIQUER le contexte "
    "économique et géopolitique, jamais de recommander une action de marché.\n"
    "INTERDICTIONS ABSOLUES :\n"
    "- ne jamais recommander d'acheter, vendre, entrer, sortir ou se positionner ;\n"
    "- ne jamais donner de niveau d'entrée, de stop-loss, de take-profit ou d'objectif ;\n"
    "- ne jamais employer l'impératif d'action de marché.\n"
    "OBLIGATIONS : rester descriptif et factuel, expliquer les mécanismes "
    "économiques, présenter plusieurs scénarios possibles, indiquer ton niveau de "
    "confiance et rappeler les incertitudes. Le lecteur décide seul."
)

# Termes prescriptifs interdits -> reformulation descriptive neutre.
# L'ordre compte : les expressions longues d'abord.
_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\b(achetez|acheter|achète|achat recommandé)\b", "[contexte favorable historiquement]"),
    (r"\b(vendez|vendre|vends|vente recommandée)\b", "[contexte défavorable historiquement]"),
    (r"\b(shortez|shorter|short(?:ez)?\s+le)\b", "[contexte défavorable historiquement]"),
    (r"\b(prenez|prendre)\s+(?:une\s+)?position\b", "[à mettre en perspective]"),
    (r"\b(entrez|entrer)\s+(?:en\s+)?(?:position|achat|vente)\b", "[à mettre en perspective]"),
    (r"\b(buy|sell|go\s+long|go\s+short)\b", "[contexte à interpréter]"),
    (r"\bstop[-\s]?loss\b", "[gestion du risque à définir par le lecteur]"),
    (r"\btake[-\s]?profit\b", "[gestion du risque à définir par le lecteur]"),
    (r"\bobjectif\s+de\s+(?:prix|cours)\b", "[niveau de référence]"),
    (r"\b(?:je\s+)?recommande\b", "on observe"),
    (r"\bil\s+faut\s+(?:acheter|vendre|se\s+positionner)\b", "on observe que"),
    (r"\bopportunité\s+d[e']achat\b", "configuration à analyser"),
    (r"\bsignal\s+d[e'](?:achat|entrée)\b", "élément de contexte"),
    (r"\bsignal\s+de\s+vente\b", "élément de contexte"),
]

_COMPILED = [(re.compile(pat, re.IGNORECASE), repl) for pat, repl in _REPLACEMENTS]

# Motifs de niveaux de trading (ex. "SL 1920", "TP: 2050", "entrée @ 1980").
_LEVEL_PATTERNS = [
    re.compile(r"\b(?:sl|tp)\s*[:=@]?\s*\d+[.,]?\d*", re.IGNORECASE),
    re.compile(r"\bentrée\s*[:=@]\s*\d+[.,]?\d*", re.IGNORECASE),
]

DISCLAIMER = (
    "Analyse de contexte macroéconomique — ne constitue pas un conseil "
    "en investissement. La décision appartient au lecteur."
)


@dataclass(slots=True)
class GuardrailReport:
    """Résultat du filtrage : texte assaini + traces pour l'audit."""

    text: str
    violations: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.violations


def enforce(text: str) -> GuardrailReport:
    """Neutralise toute formulation prescriptive. Ne lève jamais.

    Renvoie le texte assaini et la liste des motifs détectés (audit / tests).
    """
    if not text:
        return GuardrailReport(text="", violations=[])

    violations: list[str] = []
    out = text

    for pattern, replacement in _COMPILED:
        found = pattern.search(out)
        if found:
            violations.append(found.group(0).strip().lower())
            out = pattern.sub(replacement, out)

    for pattern in _LEVEL_PATTERNS:
        found = pattern.search(out)
        if found:
            violations.append(found.group(0).strip().lower())
            out = pattern.sub("[niveau retiré]", out)

    return GuardrailReport(text=out, violations=violations)


def enforce_many(texts: list[str]) -> tuple[list[str], list[str]]:
    """Applique `enforce` à une liste. Renvoie (textes assainis, violations)."""
    cleaned: list[str] = []
    all_violations: list[str] = []
    for t in texts:
        report = enforce(t)
        cleaned.append(report.text)
        all_violations.extend(report.violations)
    return cleaned, all_violations

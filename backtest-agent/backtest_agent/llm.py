"""Client LLM optionnel (Anthropic / Claude).

L'agent fonctionne SANS clé API : il produit alors un rapport 100% déterministe
(chiffres + hypothèses règles). Si une clé est présente, on ajoute la couche
d'interprétation « analyste quant » par-dessus les mêmes chiffres.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .prompts import SYSTEM_PROMPT, USER_TEMPLATE

# Modèle par défaut : configurable via la variable d'environnement.
DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")


def _dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def is_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def generate_narrative(payload: dict, model: str | None = None,
                       max_tokens: int = 4000) -> str | None:
    """Appelle Claude pour produire le rapport narratif. Retourne None si le SDK
    ou la clé sont absents (le mode déterministe prend alors le relais)."""
    if not is_available():
        return None
    try:
        import anthropic
    except ImportError:
        return None

    client = anthropic.Anthropic()
    user_msg = USER_TEMPLATE.format(
        meta=_dumps(payload.get("meta", {})),
        global_metrics=_dumps(payload.get("global_metrics", {})),
        losses=_dumps(payload.get("losses", {})),
        winners=_dumps(payload.get("winners", {})),
        suggestions=_dumps(payload.get("suggestions", {})),
    )
    resp = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")

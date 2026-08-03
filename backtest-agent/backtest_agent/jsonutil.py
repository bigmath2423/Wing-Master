"""Sérialisation JSON stricte.

Python accepte d'écrire `NaN`, `Infinity` et `-Infinity` dans du JSON. Ce n'est
PAS du JSON valide (RFC 8259) : `JSON.parse` en JavaScript lève une erreur, et
`jq` convertit silencieusement `Infinity` en 1.79e308 — une valeur fausse qui
passe inaperçue.

Comme les fichiers produits ici sont faits pour être relus par d'autres outils,
on assainit d'abord (NaN/inf -> null), puis on écrit avec `allow_nan=False` pour
que toute valeur non conforme qui aurait échappé au nettoyage lève une erreur
bruyante au lieu de corrompre le fichier en silence.
"""

from __future__ import annotations

import json
import math
from typing import Any


def sanitize(obj: Any) -> Any:
    """Remplace récursivement NaN/inf par None. Convertit les clés non-str."""
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    return obj


def dumps(obj: Any, **kwargs: Any) -> str:
    """json.dumps strict : échoue plutôt que d'émettre du JSON invalide."""
    kwargs.setdefault("indent", 2)
    kwargs.setdefault("ensure_ascii", False)
    kwargs.setdefault("default", str)
    return json.dumps(sanitize(obj), allow_nan=False, **kwargs)

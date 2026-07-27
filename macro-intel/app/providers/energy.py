"""Énergie : stocks de pétrole US (EIA) et contexte OPEP.

Les stocks hebdomadaires de brut sont un déterminant direct du prix du pétrole,
donc de l'inflation importée. Clé EIA gratuite ; repli gracieux sans clé.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import settings
from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.energy")

_EIA_URL = "https://api.eia.gov/v2/petroleum/stoc/wstk/data/"


@dataclass(slots=True)
class EnergyReading:
    crude_inventories_kb: float | None = None  # milliers de barils
    change_kb: float | None = None
    period: str = ""
    interpretation: str = ""
    source: str = "fallback"


def _interpret(change: float | None) -> str:
    if change is None:
        return "Variation des stocks indisponible."
    if change < -1000:
        return (
            f"Les stocks de brut reculent nettement ({change:+,.0f} kb) : signe d'une "
            "demande supérieure à l'offre, historiquement associé à une tension sur "
            "les prix de l'énergie et à une pression inflationniste."
        )
    if change > 1000:
        return (
            f"Les stocks de brut progressent nettement ({change:+,.0f} kb) : signe "
            "d'une offre abondante, historiquement associé à une détente des prix et "
            "à un effet désinflationniste."
        )
    return (
        f"Les stocks de brut varient peu ({change:+,.0f} kb) : marché énergétique "
        "globalement équilibré, faible impact macro à court terme."
    )


def fetch_energy() -> EnergyReading:
    """Stocks de brut US les plus récents. Toujours un objet exploitable."""
    if not settings.eia_api_key:
        return EnergyReading(interpretation="Clé EIA non configurée : stocks de pétrole non suivis.")

    data = http_get_json(
        _EIA_URL,
        params={
            "api_key": settings.eia_api_key,
            "frequency": "weekly",
            "data[0]": "value",
            "facets[product][]": "EPC0",  # brut
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 2,
        },
    )
    try:
        rows = data["response"]["data"]
        last = float(rows[0]["value"])
        prev = float(rows[1]["value"])
        change = last - prev
        return EnergyReading(
            crude_inventories_kb=last,
            change_kb=change,
            period=str(rows[0].get("period", ""))[:10],
            interpretation=_interpret(change),
            source="eia",
        )
    except (TypeError, KeyError, IndexError, ValueError) as exc:
        logger.warning("EIA indisponible : %s", exc)
        return EnergyReading(interpretation="Stocks de pétrole momentanément indisponibles.")

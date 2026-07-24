"""Risque géopolitique via GDELT (gratuit, sans clé).

GDELT Doc 2.0 : on interroge le volume et le ton médiatique sur des thèmes
de crise (guerre, sanctions, conflit). Un ton très négatif + un volume élevé
=> risque géopolitique élevé => haussier pour l'or (valeur refuge).
"""
from __future__ import annotations

import logging

from app.domain import GeoRiskReading
from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.geo")

_GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
_QUERY = "(war OR sanctions OR conflict OR military OR crisis OR geopolitical)"


def fetch_geo_risk() -> GeoRiskReading:
    data = http_get_json(
        _GDELT_URL,
        params={
            "query": _QUERY,
            "mode": "artlist",
            "format": "json",
            "maxrecords": 50,
            "timespan": "24h",
            "sort": "hybridrel",
        },
    )
    if not data or "articles" not in data:
        # Fallback neutre : risque modéré par défaut.
        return GeoRiskReading(risk_index=0.35, tone=-1.5, source="fallback")

    articles = data["articles"]
    if not articles:
        return GeoRiskReading(risk_index=0.2, tone=0.0, source="gdelt")

    tones = [float(a.get("tone", 0) or 0) for a in articles if a.get("tone") not in (None, "")]
    avg_tone = sum(tones) / len(tones) if tones else -1.0

    # Normalisation heuristique :
    #  - volume : plus il y a d'articles, plus la tension médiatique est forte.
    #  - tone   : plus il est négatif, plus la tension est élevée.
    volume_factor = min(len(articles) / 50.0, 1.0)          # 0..1
    tone_factor = min(max(-avg_tone / 6.0, 0.0), 1.0)        # ton -6 => 1.0
    risk_index = round(0.5 * volume_factor + 0.5 * tone_factor, 3)

    top = [a.get("title", "")[:120] for a in articles[:5] if a.get("title")]
    return GeoRiskReading(
        risk_index=risk_index,
        tone=round(avg_tone, 2),
        top_events=top,
        source="gdelt",
    )

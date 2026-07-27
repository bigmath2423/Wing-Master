"""COT Report (CFTC) : positionnement des intervenants.

Source publique CFTC via Socrata (aucune clé requise). On extrait le
positionnement net des non-commerciaux (spéculateurs) sur les contrats suivis,
qui sert de **proxy de positionnement** — jamais de signal d'entrée.

Le positionnement est une mesure de **fragilité technique** : un extrême rend le
marché sensible aux nouvelles contraires.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.providers.base import http_get_json

logger = logging.getLogger("macro.providers.cot")

# Jeu de données CFTC « Commitments of Traders » (futures only, legacy).
_SOCRATA_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# Marchés suivis : identifiant interne -> fragment du nom CFTC.
TRACKED = {
    "cot.gold": "GOLD",
    "cot.silver": "SILVER",
    "cot.crude": "CRUDE OIL",
    "cot.usd_index": "USD INDEX",
}


@dataclass(slots=True)
class CotReading:
    market: str
    net_noncommercial: int | None
    long_positions: int | None
    short_positions: int | None
    report_date: str = ""
    interpretation: str = ""


def _interpret(net: int | None) -> str:
    if net is None:
        return "Positionnement indisponible."
    if net > 0:
        stance = "net acheteur"
        note = (
            "Un positionnement net acheteur étiré rend historiquement le marché "
            "vulnérable à un débouclage en cas de nouvelle contraire."
        )
    elif net < 0:
        stance = "net vendeur"
        note = (
            "Un positionnement net vendeur étiré rend historiquement le marché "
            "sensible à un rachat rapide en cas de nouvelle favorable."
        )
    else:
        stance = "neutre"
        note = "Positionnement équilibré : faible fragilité technique."
    return f"Les spéculateurs sont {stance} ({net:+,} contrats nets). {note}"


def fetch_cot() -> list[CotReading]:
    """Dernier rapport COT pour les marchés suivis. Liste vide si indisponible."""
    readings: list[CotReading] = []
    for key, name_fragment in TRACKED.items():
        data = http_get_json(
            _SOCRATA_URL,
            params={
                "$where": f"upper(market_and_exchange_names) like '%{name_fragment}%'",
                "$order": "report_date_as_yyyy_mm_dd DESC",
                "$limit": 1,
            },
        )
        if not isinstance(data, list) or not data:
            continue
        row = data[0]
        longs: int | None
        shorts: int | None
        net: int | None
        try:
            longs = int(float(row.get("noncomm_positions_long_all", 0)))
            shorts = int(float(row.get("noncomm_positions_short_all", 0)))
            net = longs - shorts
        except (ValueError, TypeError):
            longs = shorts = net = None
        readings.append(
            CotReading(
                market=key,
                net_noncommercial=net,
                long_positions=longs,
                short_positions=shorts,
                report_date=str(row.get("report_date_as_yyyy_mm_dd", ""))[:10],
                interpretation=_interpret(net),
            )
        )
    if not readings:
        logger.info("COT indisponible (réseau ou format) — section masquée dans l'UI.")
    return readings

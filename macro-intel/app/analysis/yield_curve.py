"""Analyse de la courbe des taux US.

La courbe résume les anticipations de croissance, d'inflation et de politique
monétaire. On en extrait une **forme**, une **pente** et une lecture
**descriptive** du cycle — jamais une recommandation.
"""

from __future__ import annotations

from dataclasses import dataclass

# Seuils (en points de pourcentage) sur la pente 10 ans - 2 ans.
_INVERTED = -0.05
_FLAT = 0.25
_STEEP = 1.20


@dataclass(slots=True)
class CurveReading:
    spread_10y2y: float | None
    shape: str  # inverted | flat | normal | steep | unknown
    label: str
    interpretation: str


def analyse_curve(us2y: float | None, us10y: float | None, us30y: float | None = None) -> CurveReading:
    """Qualifie la courbe à partir des rendements 2/10 (30 ans optionnel)."""
    if us2y is None or us10y is None:
        return CurveReading(
            spread_10y2y=None,
            shape="unknown",
            label="Courbe indisponible",
            interpretation="Données de rendements incomplètes : lecture de la courbe non disponible.",
        )

    spread = round(us10y - us2y, 3)

    if spread <= _INVERTED:
        shape, label = "inverted", "Courbe inversée"
        interpretation = (
            "Le 2 ans rémunère plus que le 10 ans. Historiquement, cette configuration "
            "traduit des anticipations de ralentissement économique et de baisses de "
            "taux futures. Elle a souvent précédé les phases de récession, avec des "
            "délais très variables."
        )
    elif spread <= _FLAT:
        shape, label = "flat", "Courbe plate"
        interpretation = (
            "L'écart entre le 2 ans et le 10 ans est faible : le marché voit peu de "
            "prime à prêter à long terme. Configuration typique des fins de cycle de "
            "resserrement monétaire."
        )
    elif spread >= _STEEP:
        shape, label = "steep", "Courbe très pentue"
        interpretation = (
            "L'écart est large : le marché intègre de la croissance et/ou une prime "
            "d'inflation à long terme. Configuration fréquente en début de cycle "
            "d'expansion ou de reflation."
        )
    else:
        shape, label = "normal", "Courbe normale"
        interpretation = (
            "La pente est positive et modérée : régime de taux lisible, sans stress "
            "particulier sur les anticipations de cycle."
        )

    if us30y is not None and us10y is not None and (us30y - us10y) < 0:
        interpretation += (
            " Le segment long (30 ans vs 10 ans) est également inversé, signe d'une "
            "demande marquée pour la duration longue."
        )

    return CurveReading(spread_10y2y=spread, shape=shape, label=label, interpretation=interpretation)

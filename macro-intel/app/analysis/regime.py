"""Détection du régime de marché dominant.

Un « régime » est une lecture agrégée du contexte macro qui explique pourquoi les
actifs se comportent d'une certaine façon. Il est **descriptif** : il aide à
interpréter, il ne dit jamais quoi faire.

Régimes reconnus :
  risk_off        — aversion au risque, recherche de refuge
  risk_on         — appétit pour le risque
  tightening      — resserrement monétaire (taux réels en hausse)
  easing          — assouplissement (taux réels en baisse)
  reflation       — croissance + inflation qui accélèrent
  stagflation_watch — inflation élevée avec croissance/emploi qui faiblissent
  neutral         — aucun facteur dominant
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain import GeoRiskReading, MarketReadings

_LABELS = {
    "risk_off": "Aversion au risque",
    "risk_on": "Appétit pour le risque",
    "tightening": "Resserrement monétaire",
    "easing": "Assouplissement monétaire",
    "reflation": "Reflation",
    "stagflation_watch": "Vigilance stagflation",
    "neutral": "Régime neutre",
}

_DESCRIPTIONS = {
    "risk_off": (
        "La volatilité est élevée et/ou les tensions géopolitiques dominent. Dans ce "
        "type de régime, les actifs refuges (or, obligations d'État, dollar) sont "
        "historiquement recherchés et les corrélations entre actifs risqués tendent à "
        "converger."
    ),
    "risk_on": (
        "La volatilité est contenue et le contexte de liquidité est favorable. Les "
        "actifs cycliques et à bêta élevé sont historiquement soutenus dans ce régime."
    ),
    "tightening": (
        "Les taux réels progressent : le coût d'opportunité de détenir des actifs sans "
        "rendement augmente. Ce régime pèse historiquement sur l'or et les actifs de "
        "longue duration, et soutient le dollar."
    ),
    "easing": (
        "Les taux réels se détendent : la contrainte monétaire se relâche. Ce régime "
        "est historiquement porteur pour l'or, les actifs de duration et la crypto."
    ),
    "reflation": (
        "Les anticipations d'inflation sont élevées alors que l'activité tient. Les "
        "matières premières et les actifs réels sont historiquement favorisés."
    ),
    "stagflation_watch": (
        "L'inflation anticipée reste élevée alors que les signaux de croissance "
        "s'affaiblissent. Régime historiquement difficile pour les actions, plus "
        "ambivalent pour l'or."
    ),
    "neutral": (
        "Aucun facteur macro ne domine clairement : les facteurs propres à chaque "
        "marché et l'analyse technique reprennent une place relative plus importante."
    ),
}


@dataclass(slots=True)
class RegimeReading:
    regime: str
    label: str
    description: str
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)
    drivers: list[str] = field(default_factory=list)


def detect_regime(
    market: MarketReadings,
    geo: GeoRiskReading,
    *,
    growth_momentum: float = 0.0,  # -1 (contraction) .. +1 (accélération)
) -> RegimeReading:
    """Pondère les faisceaux d'indices et renvoie le régime dominant."""
    scores: dict[str, float] = dict.fromkeys(_LABELS, 0.0)
    drivers: list[str] = []

    vix = market.vix
    real_chg = market.real_rate_change_bps or 0.0
    real_level = market.real_rate_10y
    dxy_chg = market.dxy_change_pct or 0.0
    breakeven = market.breakeven_inflation

    # 1) Volatilité et tension géopolitique -> risk-off / risk-on
    if vix is not None:
        if vix >= 25:
            scores["risk_off"] += 2.0
            drivers.append(f"VIX élevé ({vix:.1f})")
        elif vix >= 18:
            scores["risk_off"] += 0.8
        elif vix <= 14:
            scores["risk_on"] += 1.2
            drivers.append(f"VIX bas ({vix:.1f})")
    if geo.risk_index >= 0.65:
        scores["risk_off"] += 1.5
        drivers.append(f"risque géopolitique élevé ({geo.risk_index:.2f})")
    elif geo.risk_index <= 0.25:
        scores["risk_on"] += 0.5

    # 2) Taux réels -> resserrement / assouplissement
    if real_chg >= 8:
        scores["tightening"] += 1.8
        drivers.append(f"taux réels en hausse (+{real_chg:.0f} bps)")
    elif real_chg <= -8:
        scores["easing"] += 1.8
        drivers.append(f"taux réels en baisse ({real_chg:.0f} bps)")
    if real_level is not None:
        if real_level >= 2.2:
            scores["tightening"] += 1.0
            drivers.append(f"taux réel restrictif ({real_level:.2f} %)")
        elif real_level <= 0.5:
            scores["easing"] += 1.0
            drivers.append(f"taux réel accommodant ({real_level:.2f} %)")

    # 3) Dollar : un dollar qui s'apprécie fortement accompagne souvent le risk-off
    if dxy_chg >= 0.5:
        scores["risk_off"] += 0.6
        scores["tightening"] += 0.4
        drivers.append(f"dollar en hausse (+{dxy_chg:.2f} %)")
    elif dxy_chg <= -0.5:
        scores["risk_on"] += 0.5
        drivers.append(f"dollar en baisse ({dxy_chg:.2f} %)")

    # 4) Inflation anticipée x croissance -> reflation / stagflation
    if breakeven is not None and breakeven >= 2.4:
        if growth_momentum >= 0.1:
            scores["reflation"] += 1.8
            drivers.append(f"inflation anticipée élevée ({breakeven:.2f} %) avec activité résiliente")
        elif growth_momentum <= -0.1:
            scores["stagflation_watch"] += 1.8
            drivers.append(f"inflation anticipée élevée ({breakeven:.2f} %) avec activité qui faiblit")
        else:
            scores["reflation"] += 0.7

    # 5) Courbe inversée -> renforce la vigilance sur le cycle
    if market.curve_10y2y is not None and market.curve_10y2y <= -0.05:
        scores["stagflation_watch"] += 0.4
        scores["risk_off"] += 0.4
        drivers.append(f"courbe inversée ({market.curve_10y2y:+.2f} pt)")

    best = max(scores.items(), key=lambda kv: kv[1])
    regime, top_score = best

    total = sum(scores.values())
    if top_score < 1.0 or total == 0:
        regime, top_score = "neutral", max(top_score, 0.0)

    # Confiance : force du régime dominant + marge sur le second.
    ordered = sorted(scores.values(), reverse=True)
    margin = (ordered[0] - ordered[1]) if len(ordered) > 1 else ordered[0]
    strength = min(top_score / 4.0, 1.0)
    separation = min(margin / 2.0, 1.0)
    confidence = round(min(100.0 * (0.6 * strength + 0.4 * separation), 92.0), 0)
    if regime == "neutral":
        confidence = min(confidence, 45.0)

    return RegimeReading(
        regime=regime,
        label=_LABELS[regime],
        description=_DESCRIPTIONS[regime],
        confidence=confidence,
        scores={k: round(v, 2) for k, v in scores.items() if v > 0},
        drivers=drivers[:5],
    )

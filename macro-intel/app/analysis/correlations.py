"""Corrélations glissantes inter-marchés.

On calcule des corrélations de Pearson sur les **variations** (rendements) plutôt
que sur les niveaux : deux séries tendancielles paraissent toujours corrélées en
niveau, ce qui est trompeur.

Implémentation volontairement sans dépendance externe (pas de numpy requis) pour
rester utilisable dans tous les environnements.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Paires suivies par défaut : les relations macro structurantes.
DEFAULT_PAIRS: tuple[tuple[str, str], ...] = (
    ("market.dxy", "commodity.gold"),
    ("rates.real10y", "commodity.gold"),
    ("market.vix", "index.spx"),
    ("commodity.oil", "index.spx"),
    ("market.dxy", "crypto.btc"),
    ("index.spx", "crypto.btc"),
    ("rates.us10y", "index.spx"),
)

WINDOWS = (30, 90)


@dataclass(slots=True)
class CorrelationReading:
    pair: str
    window_days: int
    value: float | None
    strength: str  # forte | modérée | faible | indisponible
    direction: str  # positive | négative | neutre


def _returns(series: list[float]) -> list[float]:
    """Variations relatives successives (ignore les points nuls ou invalides)."""
    out: list[float] = []
    for prev, cur in zip(series, series[1:], strict=False):
        if prev in (None, 0) or cur is None:
            continue
        try:
            out.append((cur - prev) / abs(prev))
        except ZeroDivisionError:
            continue
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Coefficient de Pearson. Renvoie None si le calcul n'est pas fiable."""
    n = min(len(xs), len(ys))
    if n < 5:
        return None
    xs, ys = xs[-n:], ys[-n:]
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=False))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    value = cov / math.sqrt(vx * vy)
    return max(-1.0, min(1.0, value))


def _qualify(value: float | None) -> tuple[str, str]:
    if value is None:
        return "indisponible", "neutre"
    magnitude = abs(value)
    strength = "forte" if magnitude >= 0.6 else "modérée" if magnitude >= 0.3 else "faible"
    direction = "positive" if value > 0.05 else "négative" if value < -0.05 else "neutre"
    return strength, direction


def correlate(
    series_a: list[float], series_b: list[float], window_days: int, pair_name: str
) -> CorrelationReading:
    """Corrélation d'une paire sur une fenêtre donnée (sur les variations)."""
    ra = _returns(series_a[-(window_days + 1) :])
    rb = _returns(series_b[-(window_days + 1) :])
    value = pearson(ra, rb)
    strength, direction = _qualify(value)
    return CorrelationReading(
        pair=pair_name,
        window_days=window_days,
        value=round(value, 3) if value is not None else None,
        strength=strength,
        direction=direction,
    )


def correlation_matrix(
    series: dict[str, list[float]],
    pairs: tuple[tuple[str, str], ...] = DEFAULT_PAIRS,
    windows: tuple[int, ...] = WINDOWS,
) -> list[CorrelationReading]:
    """Calcule toutes les paires disponibles. Les séries absentes sont ignorées."""
    out: list[CorrelationReading] = []
    for left, right in pairs:
        sa, sb = series.get(left), series.get(right)
        if not sa or not sb:
            continue
        for window in windows:
            out.append(correlate(sa, sb, window, f"{left}~{right}"))
    return out


def describe(reading: CorrelationReading) -> str:
    """Phrase descriptive d'une corrélation (pour l'UI et l'IA)."""
    if reading.value is None:
        return f"{reading.pair} : historique insuffisant sur {reading.window_days} jours."
    left, right = reading.pair.split("~", 1)
    sense = (
        "évoluent dans le même sens"
        if reading.direction == "positive"
        else "évoluent en sens opposé"
        if reading.direction == "négative"
        else "n'affichent pas de relation nette"
    )
    return (
        f"Sur {reading.window_days} jours, {left} et {right} {sense} "
        f"(corrélation {reading.value:+.2f}, intensité {reading.strength})."
    )

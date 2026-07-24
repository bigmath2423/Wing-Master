"""Conversion de l'état interne vers les schémas d'API publics."""

from __future__ import annotations

import datetime as dt

from app.pipeline import STATE
from app.schemas import FactorBreakdown, Headline, MacroBias, MacroLatest


def _asset_bias(asset: str) -> MacroBias | None:
    snap = STATE.snapshot()
    b = snap["bias"].get(asset)
    sc = snap["scores"].get(asset)
    if not b or not sc:
        return None
    f = sc.factors
    return MacroBias(
        asset=asset,
        score=b.score,
        bias=b.bias,
        confidence=b.confidence,
        risk_level=b.risk_level,
        factors=FactorBreakdown(
            geopolitics=f.get("geopolitics", 0.0),
            dollar=f.get("dollar", 0.0),
            us_rates=f.get("us_rates", 0.0),
            inflation=f.get("inflation", 0.0),
            risk_sentiment=f.get("risk_sentiment", 0.0),
        ),
        updated_at=snap["generated_at"] or dt.datetime.now(dt.UTC),
    )


def build_latest() -> MacroLatest:
    snap = STATE.snapshot()
    assets: dict[str, MacroBias] = {}
    for asset in ("gold", "btc", "commodities"):
        mb = _asset_bias(asset)
        if mb:
            assets[asset] = mb

    headlines = [
        Headline(
            ts=n.ts,
            category=n.category,
            title=n.title,
            impact_gold=n.impact_gold,
            severity=n.severity,
            url=n.url,
        )
        for n in sorted(snap["news"], key=lambda x: x.severity, reverse=True)[:8]
    ]
    gold_score = snap["scores"].get("gold")
    gold_drivers = dict(gold_score.drivers) if gold_score else {}
    sources = {
        "market": snap["market"].source,
        "geo": snap["geo"].source,
        "news": str(len(snap["news"])),
    }
    return MacroLatest(
        generated_at=snap["generated_at"] or dt.datetime.now(dt.UTC),
        assets=assets,
        headlines=headlines,
        gold_drivers=gold_drivers,
        sources=sources,
    )

"""API v1 : surface consommée par l'application MacroLens.

Toutes les réponses sont des **lectures de contexte**. Aucune n'expose de
recommandation d'exécution (Tome 0 §9) ; les textes générés ont traversé les
garde-fous anti-signal.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, is_dataclass

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.ai import guardrails
from app.ai.analyst import analyse_event
from app.ai.knowledge import TOPICS
from app.api.serializers import build_latest
from app.platform_state import PLATFORM, refresh_platform
from app.providers.market_extended import LABELS

router = APIRouter(prefix="/v1", tags=["platform"])

_ASSET_LABELS = {
    "gold": "Or — XAUUSD",
    "btc": "Bitcoin",
    "commodities": "Matières premières",
}


def _dump(obj):
    """Sérialise dataclasses / listes / dictionnaires imbriqués."""
    if obj is None:
        return None
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _dump(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_dump(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    return obj


def build_dashboard() -> dict:
    """Charge utile complète de l'écran principal."""
    plat = PLATFORM.read()
    macro = build_latest()

    assets = {
        key: {
            "label": _ASSET_LABELS.get(key, key),
            "score": bias.score,
            "bias": bias.bias,
            "confidence": bias.confidence,
            "risk_level": bias.risk_level,
            "factors": bias.factors.model_dump(),
        }
        for key, bias in macro.assets.items()
    }

    prices = [
        {
            "key": key,
            "label": LABELS.get(key, key),
            "price": entry.get("price"),
            "change_pct": entry.get("change_pct"),
            "group": key.split(".", 1)[0],
        }
        for key, entry in sorted(plat["prices"].items())
    ]

    indicators = {
        "dxy": macro.gold_drivers.get("dxy"),
        "dxy_change_pct": macro.gold_drivers.get("dxy_change_pct"),
        "us10y": macro.gold_drivers.get("us10y"),
        "us10y_change_bps": macro.gold_drivers.get("us10y_change_bps"),
        "real_rate_10y": macro.gold_drivers.get("real_rate_10y"),
        "real_rate_change_bps": macro.gold_drivers.get("real_rate_change_bps"),
        "breakeven_inflation": macro.gold_drivers.get("breakeven_inflation"),
        "geo_risk_index": macro.gold_drivers.get("geo_risk_index"),
        "us2y": plat["extras"].get("us2y"),
        "us30y": plat["extras"].get("us30y"),
        "vix": plat["extras"].get("vix"),
        "vix_change_pct": plat["extras"].get("vix_change_pct"),
    }

    # Qualité des données : l'UI doit pouvoir dire la vérité sur ce qu'elle montre.
    live_sources = sum(
        1
        for value in (macro.sources.get("market"), macro.sources.get("geo"))
        if value not in (None, "", "fallback", "init")
    )
    data_quality = {
        "degraded": bool(plat["extras"].get("degraded")) or live_sources == 0,
        "market_source": macro.sources.get("market", "unknown"),
        "geo_source": macro.sources.get("geo", "unknown"),
        "prices_available": len(prices),
        "news_analysed": len(plat["analyses"]),
        "note": (
            "Certaines sources sont injoignables : des valeurs de repli neutres sont "
            "utilisées pour garder la lecture de contexte possible."
            if bool(plat["extras"].get("degraded")) or live_sources == 0
            else "Sources de données actives."
        ),
    }

    return {
        "generated_at": plat["generated_at"] or macro.generated_at,
        "regime": _dump(plat["regime"]),
        "curve": _dump(plat["curve"]),
        "briefing": plat["briefing"],
        "indicators": indicators,
        "assets": assets,
        "prices": prices,
        "analyses": [_dump(a) for a in plat["analyses"]],
        "correlations": [_dump(c) for c in plat["correlations"]],
        "cot": [_dump(c) for c in plat["cot"]],
        "energy": _dump(plat["energy"]),
        "sources": macro.sources,
        "data_quality": data_quality,
        "disclaimer": guardrails.DISCLAIMER,
    }


@router.get("/dashboard")
def dashboard():
    """Écran principal : régime, indicateurs, actifs, prix, analyses, corrélations."""
    return build_dashboard()


@router.get("/regime")
def regime():
    """Régime de marché dominant et ses moteurs."""
    data = _dump(PLATFORM.read()["regime"])
    if data is None:
        raise HTTPException(status_code=503, detail="Régime pas encore calculé")
    return data


@router.get("/briefing")
def briefing():
    """Synthèse de contexte rédigée (descriptive)."""
    plat = PLATFORM.read()
    return {
        "generated_at": plat["generated_at"],
        "briefing": plat["briefing"],
        "regime": _dump(plat["regime"]),
        "disclaimer": guardrails.DISCLAIMER,
    }


@router.get("/events")
def events(priority: str | None = Query(None, pattern="^(critical|high|normal|low)$")):
    """Événements analysés : résumé, importance, mécanismes, scénarios, confiance."""
    analyses = [_dump(a) for a in PLATFORM.read()["analyses"]]
    if priority:
        analyses = [a for a in analyses if a["priority"] == priority]
    return {"count": len(analyses), "events": analyses}


@router.get("/correlations")
def correlations(window: int | None = Query(None, ge=1, le=400)):
    """Corrélations glissantes inter-marchés (sur les variations)."""
    readings = [_dump(c) for c in PLATFORM.read()["correlations"]]
    if window:
        readings = [r for r in readings if r["window_days"] == window]
    return {"count": len(readings), "correlations": readings}


@router.get("/topics")
def topics():
    """Base de connaissances : mécanismes économiques documentés."""
    return {
        "count": len(TOPICS),
        "topics": [
            {
                "key": t.key,
                "label": t.label,
                "why": t.why,
                "mechanism": t.mechanism,
                "markets": t.markets,
                "scenarios": t.scenarios,
            }
            for t in TOPICS.values()
        ],
    }


@router.post("/explain")
def explain(title: str = Query(..., min_length=3, max_length=500), category: str = "news"):
    """Explique un événement fourni par l'utilisateur (analyse à la demande)."""
    analysis = analyse_event(title, category=category, severity=0.5)
    return _dump(analysis)


@router.post("/refresh")
def refresh():
    """Force un rafraîchissement de la couche plateforme."""
    data = refresh_platform()
    reg = data["regime"]
    return {
        "refreshed": True,
        "regime": reg.regime if reg else None,
        "analyses": len(data["analyses"]),
    }


@router.get("/stream")
async def stream(request: Request):
    """Flux temps réel du tableau de bord (Server-Sent Events)."""

    async def generator():
        last = None
        yield "retry: 5000\n\n"
        while True:
            if await request.is_disconnected():
                break
            payload = json.loads(json.dumps(build_dashboard(), default=str))
            signature = payload.get("generated_at")
            if signature != last:
                last = signature
                yield f"data: {json.dumps(payload)}\n\n"
            else:
                yield ": keep-alive\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

"""Endpoints de lecture macro (consommés par le dashboard et TradingView)."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.serializers import build_latest
from app.pipeline import run_pipeline

router = APIRouter(prefix="/macro", tags=["macro"])


@router.get("/latest")
def macro_latest():
    """Snapshot complet : score, biais, confiance, risque par actif + headlines."""
    return build_latest()


@router.get("/{asset}")
def macro_asset(asset: str):
    """Biais d'un actif : gold | btc | commodities."""
    latest = build_latest()
    if asset not in latest.assets:
        raise HTTPException(status_code=404, detail=f"Actif inconnu : {asset}")
    return latest.assets[asset]


@router.get("/{asset}/pine")
def macro_asset_pine(asset: str):
    """Format compact texte pour intégration/alerte (clé=valeur)."""
    latest = build_latest()
    b = latest.assets.get(asset)
    if not b:
        raise HTTPException(status_code=404, detail=f"Actif inconnu : {asset}")
    risk_fr = {"low": "FAIBLE", "medium": "MOYEN", "high": "ELEVE"}[b.risk_level]
    bias_fr = {"bullish": "HAUSSIER", "bearish": "BAISSIER", "neutral": "NEUTRE"}[b.bias]
    return {
        "MACRO_SCORE": b.score,
        "MACRO_BIAS": bias_fr,
        "CONFIANCE": b.confidence,
        "RISK_LEVEL": risk_fr,
        "NEWS_IMPACT": "POSITIF" if b.score > 0 else ("NEGATIF" if b.score < 0 else "NEUTRE"),
    }


@router.post("/refresh")
def macro_refresh():
    """Force un cycle de rafraîchissement immédiat."""
    biases = run_pipeline()
    return {"refreshed": True, "gold_score": biases["gold"].score}


@router.get("/stream/sse")
async def macro_stream():
    """Flux Server-Sent Events : pousse le snapshot toutes les 5s (temps réel dashboard)."""

    async def event_generator():
        while True:
            payload = build_latest().model_dump(mode="json")
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

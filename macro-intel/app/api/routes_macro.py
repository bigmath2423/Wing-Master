"""Endpoints de lecture macro (consommés par le dashboard et TradingView)."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.serializers import build_latest
from app.db import get_session
from app.models import MacroSnapshot
from app.pipeline import run_pipeline

router = APIRouter(prefix="/macro", tags=["macro"])

_ASSETS = {"gold", "btc", "commodities"}
_BIAS_FR = {"bullish": "HAUSSIER", "bearish": "BAISSIER", "neutral": "NEUTRE"}
_RISK_FR = {"low": "FAIBLE", "medium": "MOYEN", "high": "ELEVE"}


@router.get("/latest")
def macro_latest():
    """Snapshot complet : score, biais, confiance, risque par actif + headlines."""
    return build_latest()


@router.get("/history/{asset}")
def macro_history(
    asset: str,
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
):
    """Historique des snapshots d'un actif (pour graphiques / backtest léger)."""
    if asset not in _ASSETS:
        raise HTTPException(status_code=404, detail=f"Actif inconnu : {asset}")
    rows = session.scalars(
        select(MacroSnapshot)
        .where(MacroSnapshot.asset == asset)
        .order_by(MacroSnapshot.ts.desc())
        .limit(limit)
    ).all()
    return [
        {
            "ts": r.ts,
            "score": r.score,
            "bias": r.bias,
            "confidence": r.confidence,
            "risk_level": r.risk_level,
            "factors": r.factors,
        }
        for r in rows
    ]


@router.get("/{asset}/pine")
def macro_asset_pine(asset: str):
    """Format compact pour intégration/alerte (clé=valeur)."""
    b = build_latest().assets.get(asset)
    if not b:
        raise HTTPException(status_code=404, detail=f"Actif inconnu : {asset}")
    return {
        "MACRO_SCORE": b.score,
        "MACRO_BIAS": _BIAS_FR[b.bias],
        "CONFIANCE": b.confidence,
        "RISK_LEVEL": _RISK_FR[b.risk_level],
        "NEWS_IMPACT": "POSITIF" if b.score > 0 else ("NEGATIF" if b.score < 0 else "NEUTRE"),
    }


@router.get("/{asset}")
def macro_asset(asset: str):
    """Biais d'un actif : gold | btc | commodities."""
    b = build_latest().assets.get(asset)
    if not b:
        raise HTTPException(status_code=404, detail=f"Actif inconnu : {asset}")
    return b


@router.post("/refresh")
def macro_refresh():
    """Force un cycle de rafraîchissement immédiat."""
    biases = run_pipeline()
    return {"refreshed": True, "gold_score": biases["gold"].score}


@router.get("/stream/sse")
async def macro_stream(request: Request):
    """Flux Server-Sent Events : pousse le snapshot en temps réel.

    N'émet que lorsque le snapshot change (nouveau `generated_at`), avec un
    battement de cœur périodique pour garder la connexion ouverte. S'arrête
    proprement dès que le client se déconnecte.
    """

    async def event_generator():
        last_sig = None
        yield "retry: 5000\n\n"  # côté client : reconnexion auto après 5s
        while True:
            if await request.is_disconnected():
                break
            payload = build_latest().model_dump(mode="json")
            sig = payload.get("generated_at")
            if sig != last_sig:
                last_sig = sig
                yield f"data: {json.dumps(payload)}\n\n"
            else:
                yield ": keep-alive\n\n"  # commentaire SSE = heartbeat
            await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

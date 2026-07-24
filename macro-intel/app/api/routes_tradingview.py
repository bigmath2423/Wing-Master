"""Webhook entrant : l'indicateur TradingView envoie son signal technique ici.

Le backend le fusionne avec le contexte macro courant et renvoie un verdict
(renforcé / avertissement / standard). Le score macro ne déclenche jamais
un trade seul : il module uniquement un signal technique déjà émis.
"""
from __future__ import annotations

import hmac

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.engine.fusion import fuse
from app.notify.notifier import notify
from app.pipeline import STATE, symbol_to_asset
from app.schemas import FusionResult, TradingViewSignal

router = APIRouter(prefix="/tradingview", tags=["tradingview"])


@router.post("/webhook", response_model=FusionResult)
def tradingview_webhook(signal: TradingViewSignal):
    # Auth par secret partagé (comparaison à temps constant).
    if not hmac.compare_digest(signal.secret, settings.api_shared_secret):
        raise HTTPException(status_code=401, detail="Secret invalide")

    asset = symbol_to_asset(signal.symbol)
    snap = STATE.snapshot()
    macro_bias = snap["bias"].get(asset)
    if macro_bias is None:
        raise HTTPException(status_code=503, detail="Contexte macro pas encore prêt")

    result = fuse(
        symbol=signal.symbol,
        side=signal.side,
        technical_score=signal.technical_score,
        macro=macro_bias,
    )

    # Notifie seulement les cas notables (renforcé / avertissement).
    if result["verdict"] in ("reinforced", "warning"):
        notify(result["message"])

    return FusionResult(**result)


@router.post("/simulate", response_model=FusionResult)
def simulate(symbol: str, side: str, technical_score: float):
    """Test rapide sans secret (à désactiver en prod) : simule une fusion."""
    asset = symbol_to_asset(symbol)
    macro_bias = STATE.snapshot()["bias"].get(asset)
    if macro_bias is None:
        raise HTTPException(status_code=503, detail="Contexte macro pas encore prêt")
    return FusionResult(**fuse(symbol=symbol, side=side, technical_score=technical_score, macro=macro_bias))

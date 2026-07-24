"""Fusion signal technique (TradingView) + contexte macro.

RÈGLE FONDAMENTALE : le score macro ne crée JAMAIS un trade seul.
Il ne fait que renforcer ou avertir un signal technique existant.

    Technique 88% + Macro +70 (aligné)  -> "Signal renforcé"
    Technique 90% + Macro -80 (conflit)  -> "Avertissement : contexte macro défavorable"
"""
from __future__ import annotations

from app.engine.bias import BiasResult

_ALIGNED, _CONFLICT, _NEUTRAL = "aligned", "conflict", "neutral"
_REINFORCED, _WARNING, _STANDARD = "reinforced", "warning", "standard"

# Seuils
_STRONG_MACRO = 40.0     # |macro| au-dessus => macro "significatif"
_NEUTRAL_MACRO = 15.0    # |macro| en dessous => macro neutre


def _macro_direction(macro_score: float) -> int:
    if macro_score >= _NEUTRAL_MACRO:
        return 1
    if macro_score <= -_NEUTRAL_MACRO:
        return -1
    return 0


def fuse(
    *,
    symbol: str,
    side: str,                 # "buy" | "sell"
    technical_score: float,    # 0..100
    macro: BiasResult,
) -> dict:
    trade_dir = 1 if side.lower() in ("buy", "long") else -1
    macro_dir = _macro_direction(macro.score)

    if macro_dir == 0:
        alignment = _NEUTRAL
    elif macro_dir == trade_dir:
        alignment = _ALIGNED
    else:
        alignment = _CONFLICT

    strong = abs(macro.score) >= _STRONG_MACRO
    macro_confidence = macro.confidence

    # Ajustement de confiance : la macro module le signal technique.
    #  - alignée & forte  -> bonus proportionnel à la conviction macro.
    #  - en conflit & forte -> malus (avertissement).
    #  - sinon             -> quasi neutre.
    adj = 0.0
    if alignment == _ALIGNED:
        adj = (abs(macro.score) / 100.0) * (macro_confidence / 100.0) * 12.0
        verdict = _REINFORCED if strong else _STANDARD
    elif alignment == _CONFLICT:
        adj = -(abs(macro.score) / 100.0) * (macro_confidence / 100.0) * 18.0
        verdict = _WARNING if strong else _STANDARD
    else:
        verdict = _STANDARD

    final_conf = round(max(0.0, min(100.0, technical_score + adj)), 1)

    if verdict == _REINFORCED:
        message = (
            f"✅ Signal RENFORCÉ — {symbol} {side.upper()} : technique "
            f"{technical_score:.0f}% + macro {macro.score:+.0f} "
            f"({macro.bias}). Contexte favorable."
        )
    elif verdict == _WARNING:
        message = (
            f"⚠️ AVERTISSEMENT — {symbol} {side.upper()} : trade techniquement "
            f"valide ({technical_score:.0f}%) MAIS contexte macro défavorable "
            f"(macro {macro.score:+.0f}, {macro.bias}). Prudence / taille réduite."
        )
    elif alignment == _ALIGNED:
        message = (
            f"ℹ️ Signal standard — {symbol} {side.upper()} : technique "
            f"{technical_score:.0f}%, macro alignée mais modérée "
            f"({macro.score:+.0f}, {macro.bias})."
        )
    elif alignment == _CONFLICT:
        message = (
            f"ℹ️ Signal standard — {symbol} {side.upper()} : technique "
            f"{technical_score:.0f}%, léger vent contraire macro "
            f"({macro.score:+.0f}, {macro.bias})."
        )
    else:
        message = (
            f"ℹ️ Signal standard — {symbol} {side.upper()} : technique "
            f"{technical_score:.0f}%, macro neutre ({macro.score:+.0f})."
        )

    return {
        "symbol": symbol,
        "side": side,
        "technical_score": technical_score,
        "macro_score": macro.score,
        "macro_bias": macro.bias,
        "macro_confidence": macro_confidence,
        "alignment": alignment,
        "verdict": verdict,
        "final_confidence": final_conf,
        "message": message,
    }

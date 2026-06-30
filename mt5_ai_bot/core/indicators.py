"""
core/indicators.py
==================
Indicateurs techniques calculés en pur pandas/numpy (aucune dépendance lourde).
Utilisés par les agents pour analyser les bougies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    """Moyenne mobile exponentielle."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (méthode de Wilder)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range : mesure de la volatilité."""
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def swing_points(df: pd.DataFrame, lookback: int = 5):
    """Détecte les swing highs / swing lows (points pivots).

    Un swing high est une bougie dont le high est supérieur aux `lookback`
    bougies de chaque côté. Idem inversé pour un swing low.

    Retourne deux listes d'indices : (highs_idx, lows_idx).
    """
    highs, lows = [], []
    h, l = df["high"].values, df["low"].values
    n = len(df)
    for i in range(lookback, n - lookback):
        window_h = h[i - lookback:i + lookback + 1]
        window_l = l[i - lookback:i + lookback + 1]
        if h[i] == window_h.max():
            highs.append(i)
        if l[i] == window_l.min():
            lows.append(i)
    return highs, lows


def support_resistance(df: pd.DataFrame, lookback: int = 20):
    """Renvoie le support et la résistance les plus récents/pertinents
    à partir des swing points."""
    highs, lows = swing_points(df, lookback=max(2, lookback // 4))
    resistance = float(df["high"].iloc[highs[-1]]) if highs else float(df["high"].max())
    support = float(df["low"].iloc[lows[-1]]) if lows else float(df["low"].min())
    return support, resistance

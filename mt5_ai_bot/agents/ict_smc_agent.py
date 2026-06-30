"""
agents/ict_smc_agent.py
=======================
Agent ICT / Smart Money Concepts.

Détecte les concepts utilisés par le "smart money" :
- FVG (Fair Value Gap) : déséquilibre de prix entre 3 bougies
- Order Block : dernière bougie opposée avant un mouvement impulsif
- Liquidity sweep : prise de liquidité au-delà d'un swing puis rejet
- BOS (Break of Structure) : continuation de tendance
- CHOCH (Change of Character) : retournement de structure

Toutes les détections sont volontairement simples et lisibles (heuristiques),
pas des modèles "boîte noire", afin que les signaux restent explicables.
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent
from core import indicators as ind


class ICTSMCAgent(BaseAgent):
    name = "ICT/SMC"

    def analyze(self, market: dict) -> AgentOpinion:
        op = AgentOpinion(name=self.name)
        cfg = self.config
        df = market.get(cfg.ENTRY_TIMEFRAME)
        if df is None or len(df) < cfg.SWING_LOOKBACK + 5:
            return op

        bull_signals = 0
        bear_signals = 0

        # --- 1. Structure de marché : BOS / CHOCH ---
        structure = self._market_structure(df, cfg.SWING_LOOKBACK)
        if structure["event"] == "BOS_UP":
            bull_signals += 1
            op.add("BOS haussier : cassure du dernier swing high (continuation)")
        elif structure["event"] == "BOS_DOWN":
            bear_signals += 1
            op.add("BOS baissier : cassure du dernier swing low (continuation)")
        elif structure["event"] == "CHOCH_UP":
            bull_signals += 1
            op.add("CHOCH haussier : changement de caractère vers le haut")
        elif structure["event"] == "CHOCH_DOWN":
            bear_signals += 1
            op.add("CHOCH baissier : changement de caractère vers le bas")

        # --- 2. Fair Value Gap récent ---
        fvg = self._last_fvg(df)
        if fvg:
            if fvg["type"] == "bull":
                bull_signals += 1
                op.add(f"FVG haussier non comblé entre {fvg['low']:.2f} et {fvg['high']:.2f}")
            else:
                bear_signals += 1
                op.add(f"FVG baissier non comblé entre {fvg['low']:.2f} et {fvg['high']:.2f}")
            op.data["fvg"] = fvg

        # --- 3. Order block ---
        ob = self._last_order_block(df)
        if ob:
            if ob["type"] == "bull":
                bull_signals += 1
                op.add(f"Order block haussier vers {ob['low']:.2f}-{ob['high']:.2f}")
            else:
                bear_signals += 1
                op.add(f"Order block baissier vers {ob['low']:.2f}-{ob['high']:.2f}")
            op.data["order_block"] = ob

        # --- 4. Liquidity sweep ---
        sweep = self._liquidity_sweep(df, cfg.SWING_LOOKBACK)
        if sweep == "bull":
            bull_signals += 1
            op.add("Liquidity sweep sous un swing low puis rejet (achat probable)")
        elif sweep == "bear":
            bear_signals += 1
            op.add("Liquidity sweep au-dessus d'un swing high puis rejet (vente probable)")

        # --- Agrégation ---
        total = bull_signals + bear_signals
        if total == 0:
            op.add("Aucun signal ICT/SMC clair")
            return op

        if bull_signals > bear_signals:
            op.bias = "BUY"
            op.score = (bull_signals / total) * 100
        elif bear_signals > bull_signals:
            op.bias = "SELL"
            op.score = (bear_signals / total) * 100
        else:
            op.bias = "NEUTRAL"
            op.score = 50

        return op

    # ------------------------------------------------------------------ #
    # Détections
    # ------------------------------------------------------------------ #
    def _market_structure(self, df, lookback) -> dict:
        """Détermine BOS / CHOCH à partir des deux derniers swings."""
        highs, lows = ind.swing_points(df, lookback=max(2, lookback // 4))
        last_close = float(df["close"].iloc[-1])

        result = {"event": None}
        if len(highs) >= 1 and len(lows) >= 1:
            last_high = float(df["high"].iloc[highs[-1]])
            last_low = float(df["low"].iloc[lows[-1]])

            # Tendance approximée par l'ordre des swings
            uptrend = len(highs) >= 2 and df["high"].iloc[highs[-1]] > df["high"].iloc[highs[-2]]
            downtrend = len(lows) >= 2 and df["low"].iloc[lows[-1]] < df["low"].iloc[lows[-2]]

            if last_close > last_high:
                result["event"] = "BOS_UP" if uptrend else "CHOCH_UP"
            elif last_close < last_low:
                result["event"] = "BOS_DOWN" if downtrend else "CHOCH_DOWN"
        return result

    def _last_fvg(self, df, max_back: int = 30):
        """Cherche le dernier Fair Value Gap non comblé.

        FVG haussier : low de la bougie i > high de la bougie i-2.
        FVG baissier : high de la bougie i < low de la bougie i-2.
        """
        h, l = df["high"].values, df["low"].values
        n = len(df)
        start = max(2, n - max_back)
        last_price = float(df["close"].iloc[-1])
        for i in range(n - 1, start, -1):
            # FVG haussier
            if l[i] > h[i - 2]:
                gap_low, gap_high = h[i - 2], l[i]
                if last_price >= gap_low:  # pas totalement comblé
                    return {"type": "bull", "low": float(gap_low), "high": float(gap_high)}
            # FVG baissier
            if h[i] < l[i - 2]:
                gap_low, gap_high = h[i], l[i - 2]
                if last_price <= gap_high:
                    return {"type": "bear", "low": float(gap_low), "high": float(gap_high)}
        return None

    def _last_order_block(self, df, impulse_factor: float = 1.5, max_back: int = 30):
        """Dernière bougie opposée avant un mouvement impulsif.

        Order block haussier : bougie baissière suivie d'une forte bougie
        haussière. Inverse pour baissier."""
        o, c = df["open"].values, df["close"].values
        h, l = df["high"].values, df["low"].values
        body = abs(c - o)
        avg_body = body[-max_back:].mean() if len(body) >= max_back else body.mean()
        n = len(df)
        start = max(1, n - max_back)
        for i in range(n - 1, start, -1):
            impulse = body[i] > impulse_factor * avg_body
            if not impulse:
                continue
            # bougie précédente opposée
            if c[i] > o[i] and c[i - 1] < o[i - 1]:  # impulsion haussière, OB baissier -> bull OB
                return {"type": "bull", "low": float(l[i - 1]), "high": float(h[i - 1])}
            if c[i] < o[i] and c[i - 1] > o[i - 1]:
                return {"type": "bear", "low": float(l[i - 1]), "high": float(h[i - 1])}
        return None

    def _liquidity_sweep(self, df, lookback):
        """Détecte une prise de liquidité sur les dernières bougies :
        mèche qui dépasse un swing récent puis clôture de l'autre côté."""
        highs, lows = ind.swing_points(df, lookback=max(2, lookback // 4))
        if not highs or not lows:
            return None
        last = df.iloc[-1]
        prev_high = float(df["high"].iloc[highs[-1]])
        prev_low = float(df["low"].iloc[lows[-1]])

        # Balaye sous un low puis clôture au-dessus -> achat
        if last["low"] < prev_low and last["close"] > prev_low:
            return "bull"
        # Balaye au-dessus d'un high puis clôture en-dessous -> vente
        if last["high"] > prev_high and last["close"] < prev_high:
            return "bear"
        return None

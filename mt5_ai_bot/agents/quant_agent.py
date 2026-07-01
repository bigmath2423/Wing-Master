"""
agents/quant_agent.py
=====================
Agent de trading QUANTITATIF (statistique).

Approche mathématique/systématique, complémentaire des agents technique et ICT.
Combine plusieurs signaux quant classiques, calculés sur le timeframe d'entrée :

1. MOMENTUM (Rate of Change) : la tendance persiste-t-elle ?
   ROC > 0 -> haussier, ROC < 0 -> baissier.

2. MEAN REVERSION (Z-score) : le prix est-il sur-étendu ?
   z > +seuil -> trop haut, retour baissier probable.
   z < -seuil -> trop bas, rebond haussier probable.

3. RÉGIME DE VOLATILITÉ (largeur des bandes de Bollinger) :
   position du prix dans les bandes + expansion/compression.

4. RATIO DE SHARPE glissant : qualité/régularité de la tendance récente.
   Sharpe positif élevé -> tendance haussière propre, et inversement.

Chaque signal vote (+1 haussier / -1 baissier), pondéré, puis agrégé en un
biais BUY/SELL/NEUTRAL avec un score de confiance. Tout est explicable.
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent
from core import indicators as ind


class QuantAgent(BaseAgent):
    name = "Quant"

    # Poids de chaque signal quant dans le vote
    SIGNAL_WEIGHTS = {
        "momentum": 1.0,
        "mean_reversion": 1.0,
        "bollinger": 0.7,
        "sharpe": 0.8,
    }

    def analyze(self, market: dict) -> AgentOpinion:
        op = AgentOpinion(name=self.name)
        cfg = self.config
        df = market.get(cfg.ENTRY_TIMEFRAME)

        need = max(cfg.QUANT_ZSCORE_PERIOD, cfg.QUANT_BB_PERIOD,
                   cfg.QUANT_SHARPE_PERIOD, cfg.QUANT_MOMENTUM_PERIOD) + 5
        if df is None or len(df) < need:
            op.add("Données insuffisantes pour l'analyse quantitative.")
            return op

        close = df["close"]
        price = float(close.iloc[-1])
        weighted = 0.0
        total_weight = 0.0

        # --- 1. Momentum (ROC) ---
        roc = float(ind.roc(close, cfg.QUANT_MOMENTUM_PERIOD).iloc[-1])
        w = self.SIGNAL_WEIGHTS["momentum"]
        total_weight += w
        if roc > 0:
            weighted += w
            op.add(f"Momentum positif (ROC {roc:+.2f}% sur {cfg.QUANT_MOMENTUM_PERIOD}) -> haussier")
        elif roc < 0:
            weighted -= w
            op.add(f"Momentum négatif (ROC {roc:+.2f}% sur {cfg.QUANT_MOMENTUM_PERIOD}) -> baissier")
        op.data["roc"] = round(roc, 3)

        # --- 2. Mean reversion (Z-score) ---
        z = float(ind.zscore(close, cfg.QUANT_ZSCORE_PERIOD).iloc[-1])
        w = self.SIGNAL_WEIGHTS["mean_reversion"]
        total_weight += w
        thr = cfg.QUANT_ZSCORE_THRESHOLD
        if z >= thr:
            weighted -= w   # sur-acheté -> retour baissier attendu
            op.add(f"Z-score {z:+.2f} >= {thr} : prix sur-étendu à la hausse -> retour baissier probable")
        elif z <= -thr:
            weighted += w   # sur-vendu -> rebond haussier attendu
            op.add(f"Z-score {z:+.2f} <= -{thr} : prix sur-étendu à la baisse -> rebond haussier probable")
        else:
            op.add(f"Z-score {z:+.2f} dans la zone neutre (pas d'excès)")
        op.data["zscore"] = round(z, 3)

        # --- 3. Régime de volatilité (Bollinger) ---
        mean, upper, lower, bw = ind.bollinger(close, cfg.QUANT_BB_PERIOD, cfg.QUANT_BB_STD)
        up, lo, mid = float(upper.iloc[-1]), float(lower.iloc[-1]), float(mean.iloc[-1])
        w = self.SIGNAL_WEIGHTS["bollinger"]
        total_weight += w
        if price > up:
            weighted -= w
            op.add("Prix au-dessus de la bande de Bollinger sup. -> sur-achat statistique")
        elif price < lo:
            weighted += w
            op.add("Prix en-dessous de la bande de Bollinger inf. -> sur-vente statistique")
        elif price > mid:
            weighted += w * 0.3
            op.add("Prix dans la moitié haute des bandes de Bollinger (léger biais haussier)")
        else:
            weighted -= w * 0.3
            op.add("Prix dans la moitié basse des bandes de Bollinger (léger biais baissier)")
        op.data["bb_bandwidth"] = round(float(bw.iloc[-1]), 3)

        # --- 4. Ratio de Sharpe glissant ---
        sh = ind.sharpe(close, cfg.QUANT_SHARPE_PERIOD)
        w = self.SIGNAL_WEIGHTS["sharpe"]
        total_weight += w
        if sh > 0.05:
            weighted += w
            op.add(f"Sharpe glissant {sh:+.2f} : tendance haussière régulière")
        elif sh < -0.05:
            weighted -= w
            op.add(f"Sharpe glissant {sh:+.2f} : tendance baissière régulière")
        else:
            op.add(f"Sharpe glissant {sh:+.2f} : pas de tendance nette")
        op.data["sharpe"] = round(sh, 3)

        # --- Agrégation ---
        if total_weight == 0:
            return op
        norm = max(-1.0, min(1.0, weighted / total_weight))
        op.score = abs(norm) * 100
        if norm > 0.15:
            op.bias = "BUY"
        elif norm < -0.15:
            op.bias = "SELL"
        else:
            op.bias = "NEUTRAL"
        return op

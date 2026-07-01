"""
agents/sentiment_agent.py
=========================
Agent d'analyse de SENTIMENT (news / actualité).

À court terme, l'or bouge beaucoup sur l'actualité (décisions Fed, tensions
géopolitiques, chiffres de l'emploi/inflation, aversion au risque...).

Cet agent lit les titres d'actualité que tu colles dans config.NEWS_HEADLINES
et les note avec un dictionnaire de mots-clés propres à l'or :
- mots "haussiers or" (safe-haven, rate cut, war, inflation...) -> +1 chacun
- mots "baissiers or" (rate hike, strong dollar, risk-on...)   -> -1 chacun

Le sentiment agrégé donne un biais BUY/SELL/NEUTRAL. Un biais manuel
(config.NEWS_MANUAL_BIAS) est aussi pris en compte si aucun titre n'est fourni.
Approche par mots-clés = simple, rapide et totalement explicable (pas de modèle
opaque ni d'API externe).
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent


class SentimentAgent(BaseAgent):
    name = "Sentiment"

    # Mots-clés HAUSSIERS pour l'or (valeur refuge, dollar faible, taux bas...)
    BULLISH = {
        "rate cut", "rate cuts", "dovish", "cut rates", "lower rates",
        "safe haven", "safe-haven", "war", "conflict", "tension", "tensions",
        "geopolitical", "crisis", "recession", "uncertainty", "inflation",
        "weak dollar", "dollar falls", "dollar weakens", "risk-off", "risk off",
        "haven demand", "gold rises", "gold surges", "gold rally", "stimulus",
        "escalation", "sanctions", "fear", "slowdown", "unemployment rises",
    }

    # Mots-clés BAISSIERS pour l'or (dollar fort, taux hauts, risk-on...)
    BEARISH = {
        "rate hike", "rate hikes", "hawkish", "raise rates", "higher rates",
        "strong dollar", "dollar rises", "dollar strengthens", "dollar surges",
        "risk-on", "risk on", "rally in stocks", "stocks rally", "yields rise",
        "rising yields", "strong jobs", "strong jobs report", "robust economy",
        "gold falls", "gold drops", "gold slides", "gold declines",
        "de-escalation", "ceasefire", "peace deal", "cooling inflation",
        "inflation cools", "soft landing", "profit taking",
    }

    _MANUAL = {
        "bullish": (+1, "Biais news manuel : haussier pour l'or"),
        "bearish": (-1, "Biais news manuel : baissier pour l'or"),
    }

    def analyze(self, market: dict) -> AgentOpinion:
        op = AgentOpinion(name=self.name)
        cfg = self.config

        headlines = [h for h in getattr(cfg, "NEWS_HEADLINES", []) if h and h.strip()]
        bull, bear = 0, 0

        for title in headlines:
            t = title.lower()
            hits_b = [kw for kw in self.BULLISH if kw in t]
            hits_s = [kw for kw in self.BEARISH if kw in t]
            bull += len(hits_b)
            bear += len(hits_s)
            if hits_b or hits_s:
                tag = "haussier" if len(hits_b) >= len(hits_s) else "baissier"
                short = title.strip()
                short = short[:70] + ("..." if len(short) > 70 else "")
                op.add(f"News ({tag}) : \"{short}\"")

        # Biais manuel si aucun titre fourni
        if not headlines:
            manual = str(getattr(cfg, "NEWS_MANUAL_BIAS", "neutral")).lower()
            if manual in self._MANUAL:
                impact, reason = self._MANUAL[manual]
                op.add(reason)
                op.bias = "BUY" if impact > 0 else "SELL"
                op.score = 60.0
                return op
            op.add("Aucune actualité fournie (config.NEWS_HEADLINES vide).")
            return op

        total = bull + bear
        op.data["bullish_hits"] = bull
        op.data["bearish_hits"] = bear

        if total == 0:
            op.add("Titres fournis mais aucun mot-clé pertinent détecté.")
            return op

        net = bull - bear
        op.score = min(100.0, abs(net) / total * 100 + 20)  # +20 : base de confiance
        if net > 0:
            op.bias = "BUY"
            op.add(f"Sentiment news globalement HAUSSIER ({bull} vs {bear}).")
        elif net < 0:
            op.bias = "SELL"
            op.add(f"Sentiment news globalement BAISSIER ({bear} vs {bull}).")
        else:
            op.bias = "NEUTRAL"
            op.add(f"Sentiment news équilibré ({bull} vs {bear}).")
        return op

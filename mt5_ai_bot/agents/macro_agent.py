"""
agents/macro_agent.py
=====================
Agent d'analyse macro-économique (fondamental).

L'OR (XAUUSD) est un actif macro par excellence. Son prix dépend surtout de :
- la politique de la Fed (taux directeurs)
- la force du dollar US (DXY)
- les taux d'intérêt réels
- l'inflation
- le sentiment de risque (valeur refuge)
- les tensions géopolitiques

Contrairement aux agents technique/ICT qui lisent les bougies, cet agent lit un
CONTEXTE MACRO fourni dans config.py (MACRO). Tu mets à jour ces réglages selon
l'actualité (décision Fed, chiffre du CPI, tendance du DXY...), et l'agent en
déduit un biais de fond haussier ou baissier sur l'or.

Ce choix (config plutôt qu'API temps réel) garde le bot simple, transparent et
sans dépendance/clé externe. Chaque facteur produit une raison lisible.
"""

from __future__ import annotations

from .base import AgentOpinion, BaseAgent


class MacroAgent(BaseAgent):
    name = "Macro"

    # Pour chaque facteur : { valeur : (impact_sur_or, phrase) }
    # impact > 0 = haussier or, impact < 0 = baissier or.
    _RULES = {
        "fed_stance": {
            "hawkish": (-1, "Fed hawkish (hausse des taux) -> pression baissière sur l'or"),
            "dovish": (+1, "Fed dovish (baisse/pause des taux) -> soutien haussier pour l'or"),
        },
        "usd_trend": {
            "strong": (-1, "Dollar fort (DXY en hausse) -> baissier pour l'or"),
            "weak": (+1, "Dollar faible (DXY en baisse) -> haussier pour l'or"),
        },
        "real_yields": {
            "rising": (-1, "Taux réels en hausse -> coût d'opportunité, baissier or"),
            "falling": (+1, "Taux réels en baisse -> haussier pour l'or"),
        },
        "inflation": {
            "high": (+1, "Inflation élevée -> l'or joue son rôle de couverture (haussier)"),
            "low": (-1, "Inflation faible -> moins de demande de couverture (baissier)"),
        },
        "risk_sentiment": {
            "risk_off": (+1, "Marché risk-off (aversion au risque) -> or valeur refuge (haussier)"),
            "risk_on": (-1, "Marché risk-on (appétit pour le risque) -> baissier pour l'or"),
        },
        "geopolitics": {
            "high": (+1, "Tensions géopolitiques élevées -> demande de valeur refuge (haussier)"),
            "low": (-1, "Détente géopolitique -> moins de refuge (léger baissier)"),
        },
    }

    def analyze(self, market: dict) -> AgentOpinion:
        # market n'est pas utilisé : l'agent macro lit le contexte config.
        op = AgentOpinion(name=self.name)
        cfg = self.config

        macro = getattr(cfg, "MACRO", {}) or {}
        weights = getattr(cfg, "MACRO_WEIGHTS", {}) or {}

        weighted = 0.0     # >0 haussier or, <0 baissier or
        total_weight = 0.0
        active = 0

        for factor, rules in self._RULES.items():
            value = str(macro.get(factor, "neutral")).lower()
            w = float(weights.get(factor, 1.0))
            total_weight += w
            if value in rules:
                impact, reason = rules[value]
                weighted += impact * w
                op.add(reason)
                active += 1
            # "neutral" ou valeur inconnue -> aucun impact

        op.data["active_factors"] = active

        if active == 0:
            op.add("Contexte macro neutre (aucun facteur renseigné dans config.MACRO).")
            op.bias = "NEUTRAL"
            op.score = 0.0
            return op

        # Normalise vers -1..1 puis vers un score 0..100.
        # On divise par le poids des facteurs ACTIFS pour ne pas diluer
        # le signal quand peu de facteurs sont renseignés.
        active_weight = sum(
            float(weights.get(f, 1.0))
            for f in self._RULES
            if str(macro.get(f, "neutral")).lower() in self._RULES[f]
        )
        norm = max(-1.0, min(1.0, weighted / max(active_weight, 0.01)))
        op.score = abs(norm) * 100

        if norm > 0.15:
            op.bias = "BUY"
            op.add(f"Biais macro global : HAUSSIER sur l'or ({active} facteur(s)).")
        elif norm < -0.15:
            op.bias = "SELL"
            op.add(f"Biais macro global : BAISSIER sur l'or ({active} facteur(s)).")
        else:
            op.bias = "NEUTRAL"
            op.add("Facteurs macro contradictoires -> biais neutre.")

        return op

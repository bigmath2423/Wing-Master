# MT5 AI Trading Bot — XAUUSD

Bot de trading **multi-agents IA** pour MetaTrader 5, spécialisé sur l'or (XAUUSD).
Inspiré de [TradingAgents](https://github.com/TauricResearch/TradingAgents) (architecture multi-agents)
et de [aiomql](https://github.com/Ichinga-Samuel/aiomql) (intégration MetaTrader 5).

> ⚠️ **Par défaut, le bot n'exécute AUCUN trade.** Il affiche seulement un signal clair
> (BUY / SELL / NO TRADE). L'exécution réelle est désactivée et limitée aux comptes démo.

---

## 🧠 Architecture multi-agents

| Agent | Rôle |
|-------|------|
| **TechnicalAgent** | Tendance (EMA 50/200), RSI, support/résistance, multi-timeframe |
| **ICTSMCAgent** | FVG, Order Block, Liquidity Sweep, BOS / CHOCH (Smart Money Concepts) |
| **MacroAgent** | Contexte macro de l'or : Fed, dollar/DXY, taux réels, inflation, risque, géopolitique |
| **QuantAgent** | Signaux statistiques : momentum (ROC), mean-reversion (z-score), Bollinger, ratio de Sharpe |
| **RiskAgent** | Calcule lot, stop loss, take profit — risque max **1%** du capital |
| **DecisionAgent** | Agrège les opinions → **BUY / SELL / NO TRADE** + niveau de confiance |
| **ExecutionAgent** | Envoie l'ordre à MT5 (démo uniquement, désactivé par défaut) |

Le flux : `MT5 → données H1/M15/M5 → agents d'analyse → décision → (exécution)`.

## 📁 Structure

```
mt5_ai_bot/
├── config.py              # Tous les réglages (risque, symbole, timeframes…)
├── main.py                # Point d'entrée : python main.py
├── requirements.txt
├── core/
│   ├── mt5_client.py      # Connexion MT5 + données (+ mode simulation)
│   └── indicators.py      # EMA, RSI, ATR, swings, S/R
├── agents/
│   ├── base.py            # AgentOpinion + BaseAgent
│   ├── technical_agent.py
│   ├── ict_smc_agent.py
│   ├── macro_agent.py
│   ├── quant_agent.py
│   ├── risk_agent.py
│   ├── decision_agent.py
│   └── execution_agent.py
└── utils/
    └── display.py         # Affichage du signal
```

## 🚀 Installation

```bash
cd mt5_ai_bot
pip install -r requirements.txt
```

> Le module `MetaTrader5` ne s'installe que sous **Windows**. Sur Linux/Mac,
> le bot bascule automatiquement en **mode simulation** (bougies synthétiques)
> pour que tu puisses tester toute la logique sans terminal MT5.

## ▶️ Lancement

```bash
python main.py
```

Exemple de sortie :

```
========================================================
  SIGNAL XAUUSD   2026-06-30 00:26:27
========================================================
  DÉCISION       : BUY
  CONFIANCE      : 72%
  ENTRÉE         : 2301.12
  STOP LOSS      : 2294.82
  TAKE PROFIT    : 2313.72
  LOT            : 0.16
  RISQUE         : 100.0$  (RR 2.0)
  RAISON DU TRADE:
     - Consensus BUY ...
========================================================
```

## ⚙️ Configuration (`config.py`)

| Réglage | Description | Défaut |
|---------|-------------|--------|
| `SYMBOL` | Symbole tradé | `XAUUSD` |
| `TIMEFRAMES` | Timeframes analysés | `H1, M15, M5` |
| `RISK_PER_TRADE` | Risque par trade | `0.01` (1%) |
| `RISK_REWARD_RATIO` | Ratio TP/SL | `2.0` |
| `MIN_CONFIDENCE` | Confiance min. pour signaler | `55` |
| `AUTO_TRADE` | Exécuter les trades | `False` |
| `DEMO_ONLY` | Bloquer les comptes réels | `True` |

### Connexion à ton compte démo MT5

Ouvre simplement MetaTrader 5 connecté à un compte démo (le bot utilise le
terminal ouvert), **ou** renseigne dans `config.py` :

```python
MT5_LOGIN = 12345678
MT5_PASSWORD = "ton_mot_de_passe"
MT5_SERVER = "MetaQuotes-Demo"
```

## 🌍 Agent Macro (contexte fondamental de l'or)

L'or réagit surtout à la macro. L'agent `MacroAgent` lit un contexte que **tu
renseignes** dans `config.py` (`MACRO`) selon l'actualité économique :

```python
MACRO = {
    "fed_stance":     "dovish",    # hawkish | dovish | neutral
    "usd_trend":      "weak",      # strong | weak | neutral
    "real_yields":    "falling",   # rising | falling | neutral
    "inflation":      "high",      # high | low | neutral
    "risk_sentiment": "risk_off",  # risk_off | risk_on | neutral
    "geopolitics":    "high",      # high | low | neutral
}
```

Règle générale pour l'or : **dollar faible + Fed dovish + taux réels en baisse +
inflation + aversion au risque + tensions = haussier**. L'inverse est baissier.
Laisse `"neutral"` pour ignorer un facteur. Mets ces valeurs à jour avant chaque
grande annonce (décision Fed, CPI, NFP...).

## 📊 Agent Quant (trading quantitatif)

`QuantAgent` ajoute une couche **statistique/systématique**, calculée sur le
timeframe d'entrée. Il combine 4 signaux :

| Signal | Mesure | Lecture |
|--------|--------|---------|
| **Momentum (ROC)** | variation % sur N bougies | positif → haussier, négatif → baissier |
| **Mean reversion (Z-score)** | écart à la moyenne en σ | `\|z\| > 2` → prix sur-étendu, retour attendu |
| **Volatilité (Bollinger)** | position dans les bandes | hors bandes → sur-achat/sur-vente |
| **Ratio de Sharpe** | régularité des rendements | positif → tendance propre haussière |

Réglages dans `config.py` : `QUANT_MOMENTUM_PERIOD`, `QUANT_ZSCORE_PERIOD`,
`QUANT_ZSCORE_THRESHOLD`, `QUANT_BB_PERIOD`, `QUANT_BB_STD`, `QUANT_SHARPE_PERIOD`.

## 🔒 Passer en exécution automatique (démo)

Quand tu es prêt et **sur un compte démo** uniquement :

```python
# config.py
AUTO_TRADE = True   # le bot enverra les ordres
DEMO_ONLY = True    # garde TOUJOURS cette sécurité activée
```

L'agent d'exécution refusera d'envoyer un ordre si le compte n'est pas démo.

## ⚠️ Avertissement

Outil **éducatif**. Le trading comporte des risques de perte en capital.
Teste longuement en démo avant toute utilisation réelle. Les détections
ICT/SMC sont des heuristiques simplifiées, pas des garanties de marché.

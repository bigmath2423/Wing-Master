# 🛰️ Macro-Intel

**Couche d'intelligence macroéconomique & géopolitique** pour compléter un
indicateur de trading TradingView. Module **100 % indépendant** : il n'ajoute
qu'une couche d'information et **ne crée jamais un trade seul** — il renforce ou
avertit un signal technique existant.

> Cible : **XAUUSD (or)**, **BTC**, **matières premières**.

---

## Ce que fait le système

| # | Fonction | Implémentation |
|---|----------|----------------|
| 1 | **Collecte** news, calendrier éco, banques centrales, géopolitique, drivers de l'or (DXY, rendements US, inflation, taux réels, risque géo) | `app/providers/*` |
| 2 | **Analyse IA** → scores par facteur | `app/engine/scoring.py` + `ai_classifier.py` |
| 3 | **Biais marché** (haussier/baissier/neutre) + **confiance** | `app/engine/bias.py` |
| 4 | **Connexion TradingView** (webhook + API JSON) | `app/api/*`, `tradingview/*` |
| 5 | **Fusion** technique + macro (renforcé / avertissement) | `app/engine/fusion.py` |
| 6 | **Architecture pro** (API, DB, scheduler, Docker, tests) | tout le dépôt |

### Exemple de sortie

```
GOLD MACRO SCORE : +75/100
  Géopolitique    : +30
  Dollar          : +15
  Taux US         : -10
  Inflation       : +20
  Sentiment risque: +20

XAUUSD → MACRO BIAS : HAUSSIER · CONFIANCE : 82% · RISQUE : FAIBLE
```

### Exemple de fusion (le cœur de la valeur)

```
Technique : SMC + Liquidité + VWAP + Structure = 88%
Macro     : +70 (aligné)
Résultat  : ✅ Signal RENFORCÉ

Technique : 90%
Macro     : -80 (conflit)
Résultat  : ⚠️ « Trade techniquement valide mais contexte macro défavorable »
```

---

## Démarrage rapide (aucune clé API requise)

```bash
cd macro-intel
./run.sh
```

Puis ouvrez :
- **Dashboard temps réel** → http://localhost:8000/
- **Docs API interactives** → http://localhost:8000/docs

> Sans clé API, le système fonctionne en mode « repli » (sources gratuites
> GDELT/RSS + valeurs neutres). Ajoutez vos clés dans `.env` pour des données
> réelles complètes (voir `.env.example`).

### Avec Docker

```bash
cp .env.example .env
docker compose up --build
```

### Tester la fusion sans TradingView

```bash
curl -X POST "http://localhost:8000/tradingview/simulate?symbol=XAUUSD&side=buy&technical_score=88"
```

---

## Choix techniques (résumé — détails dans `ARCHITECTURE.md`)

| Brique | Choix | Pourquoi |
|--------|-------|----------|
| **Langage** | Python 3.11 | Écosystème data/finance + IA |
| **API** | FastAPI + Uvicorn | Async, typé, docs auto, webhooks |
| **Base de données** | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy | Historisation scores & news |
| **Temps réel** | APScheduler + Server-Sent Events | Rafraîchissement + push dashboard |
| **IA** | Claude (optionnel) + moteur de règles | Nuance sémantique avec repli déterministe |
| **TradingView** | Webhook entrant + API JSON + overlay Pine | Contourne la limite HTTP de Pine |
| **Notifications** | Telegram / Discord | Verdicts renforcé/avertissement |

### Sources de données

| Domaine | Source (gratuite) | Clé ? |
|---|---|---|
| Drivers or (DXY, rendements, taux réels, inflation) | **FRED**, yfinance | FRED : gratuite |
| News économiques | **Finnhub** / NewsAPI / RSS | optionnelle |
| Calendrier éco (CPI, NFP, FOMC…) | **FMP** / Trading Economics | optionnelle |
| Banques centrales | RSS **Fed** / **BCE** | non |
| Risque géopolitique | **GDELT** | non |

---

## Structure du projet

```
macro-intel/
├── app/
│   ├── main.py            # App FastAPI, lifespan, dashboard
│   ├── config.py          # Configuration (env)
│   ├── db.py / models.py  # SQLAlchemy (historisation)
│   ├── schemas.py         # Contrats API (Pydantic)
│   ├── domain.py          # Types internes
│   ├── pipeline.py        # Orchestration collecte→score→biais
│   ├── scheduler.py       # Rafraîchissement temps réel
│   ├── providers/         # Sources de données (repli gracieux)
│   │   ├── market_data.py economic_calendar.py news.py
│   │   ├── central_banks.py geopolitics.py
│   ├── engine/            # Cœur analytique
│   │   ├── scoring.py     # GOLD/BTC/commodities MACRO SCORE
│   │   ├── bias.py        # biais + confiance + risque
│   │   ├── fusion.py      # technique + macro (jamais seul)
│   │   └── ai_classifier.py
│   ├── api/               # Routes (macro, tradingview, SSE)
│   └── notify/            # Telegram / Discord
├── tradingview/           # Pine Script (signal_bridge, overlay) + guide
├── dashboard/index.html   # Tableau de bord temps réel
├── tests/                 # Tests du moteur (16 tests)
├── Dockerfile / docker-compose.yml / run.sh
└── requirements.txt / .env.example
```

---

## Tests

```bash
source .venv/bin/activate
pytest -q          # 16 tests : scoring, biais, fusion
```

---

## Garde-fous & limites

- ⚠️ **Aide à la décision, pas conseil financier.** Les scores sont heuristiques.
- Le score macro **ne déclenche jamais un ordre** — il module un signal technique.
- Les pondérations (`app/engine/scoring.py`, `_CAPS`) sont **transparentes et
  ajustables** ; calibrez-les à votre style.
- Pine Script ne peut pas lire l'API : voir `tradingview/README.md` pour
  l'architecture retenue.

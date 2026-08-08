# 🛰️ MacroLens

**Plateforme d'analyse macroéconomique assistée par IA.** Elle centralise les
informations, analyse les données économiques, **explique** les événements, en
présente les **scénarios** possibles et met en avant ce qui compte — pour faire
gagner plusieurs heures d'analyse par jour.

> ⚠️ **Ce n'est pas un robot de trading.** MacroLens n'ouvre aucune position,
> n'achète ni ne vend, et **n'émet jamais de signal d'achat ou de vente**.
> La décision finale appartient toujours au trader. Cette règle n'est pas une
> mention légale : c'est une contrainte technique implémentée
> (`app/ai/guardrails.py`) et testée (`tests/test_guardrails.py`).

Couverture : inflation, taux directeurs, banques centrales, NFP, CPI, PPI, PMI,
PIB, chômage, minutes du FOMC, rendements obligataires, courbe des taux, DXY,
VIX, COT, OPEP et stocks de pétrole, géopolitique, matières premières, Forex,
indices, crypto et corrélations inter-marchés.

## Démarrage en 30 secondes

```bash
cd macro-intel && make install && make run
# Application  → http://localhost:8000/
# API & docs   → http://localhost:8000/docs
```

Fonctionne **sans aucune clé API** (sources gratuites + repli honnêtement
signalé). L'application `dashboard/app.html` s'ouvre aussi **directement dans un
navigateur** : elle bascule alors en mode démonstration, clairement étiqueté.

### Brancher l'application sur une API distante

Le fichier `dashboard/app.html` est autonome et peut pointer vers **n'importe
quel backend compatible**, sans être modifié :

1. ouvrez le fichier dans un navigateur ;
2. cliquez sur **⚙ API** en haut à droite ;
3. saisissez l'adresse de votre serveur (ex. `https://macro.mon-domaine.fr`) et
   validez avec **Connecter**.

L'adresse est mémorisée dans le navigateur. Champ vide = même origine que la page.

L'API doit exposer `GET /v1/dashboard` (charge utile complète) et, pour le temps
réel, `GET /v1/stream` (Server-Sent Events). En cas d'appel depuis une origine
différente, elle doit autoriser cette origine (**CORS**) — c'est déjà le cas du
backend fourni.

## Documentation

📚 Spécification professionnelle complète en **13 tomes** dans
[`docs/`](docs/README.md) — commencez par le
[Cahier des charges (Tome 0)](docs/TOME-00-cahier-des-charges.md), puis
l'[Architecture (Tome 1)](docs/TOME-01-architecture.md).

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
├── dashboard/index.html   # Tableau de bord temps réel (Simulateur + Live SSE)
├── tests/                 # 29 tests (scoring, biais, fusion, API, pipeline)
├── .github/workflows/     # CI (ruff + pytest)
├── Dockerfile / docker-compose.yml / Makefile / run.sh
├── pyproject.toml         # config ruff / pytest / mypy
└── requirements.txt / .env.example / LICENSE
```

---

## Endpoints principaux

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET`  | `/` | Application MacroLens |
| `GET`  | `/simulateur` | Simulateur d'impact macro sur l'or |
| `GET`  | `/health` | Sonde de santé |
| `GET`  | `/v1/dashboard` | Charge utile complète de l'application |
| `GET`  | `/v1/regime` · `/v1/briefing` | Régime dominant · synthèse de contexte |
| `GET`  | `/v1/news` | **Fil d'actualité en direct** (filtres `category`, `limit`) |
| `GET`  | `/v1/calendar` | **Calendrier économique** (filtres `importance`, `days`) |
| `GET`  | `/v1/events` · `/v1/correlations` · `/v1/topics` | Événements analysés · corrélations · mécanismes |
| `POST` | `/v1/explain?title=` | Analyse d'un événement à la demande |
| `GET`  | `/v1/stream` | Flux temps réel de l'application (SSE) |
| `GET`  | `/macro/latest` | Snapshot complet (scores, biais, drivers, headlines) |
| `GET`  | `/macro/{asset}` | Biais d'un actif (`gold` / `btc` / `commodities`) |
| `GET`  | `/macro/{asset}/pine` | Format compact `MACRO_SCORE / BIAS / RISK_LEVEL` |
| `GET`  | `/macro/history/{asset}` | Historique des snapshots (graphiques / backtest) |
| `GET`  | `/macro/stream/sse` | Flux temps réel (Server-Sent Events) |
| `POST` | `/macro/refresh` | Force un cycle de rafraîchissement |
| `POST` | `/tradingview/webhook` | Réception du signal technique + fusion |
| `GET`  | `/docs` | Documentation OpenAPI interactive |

---

## Développement & qualité

```bash
make install     # venv + dépendances + outils
make run         # lance l'API en rechargement auto
make check       # lint (ruff) + tests (pytest) — identique à la CI
make format      # formate le code
make typecheck   # analyse de types (mypy)
```

- **Lint & format** : `ruff` (config dans `pyproject.toml`).
- **Tests** : `pytest` — 29 tests couvrant le moteur (scoring/biais/fusion) et
  l'API (webhook, validation, historique, mapping symboles).
- **CI** : GitHub Actions exécute `ruff check`, `ruff format --check` et
  `pytest` à chaque push touchant `macro-intel/`.

---

## Garde-fous & limites

- ⚠️ **Aide à la décision, pas conseil financier.** Les scores sont heuristiques.
- Le score macro **ne déclenche jamais un ordre** — il module un signal technique.
- Les pondérations (`app/engine/scoring.py`, `_CAPS`) sont **transparentes et
  ajustables** ; calibrez-les à votre style.
- Pine Script ne peut pas lire l'API : voir `tradingview/README.md` pour
  l'architecture retenue.

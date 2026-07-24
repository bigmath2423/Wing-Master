# Architecture — Macro-Intel

Document de conception. Cible : un outil de qualité « quant » mais dimensionné
pour un **trader individuel** (déployable sur un petit VPS, sans clé payante
obligatoire).

## 1. Vue d'ensemble

```
                    ┌──────────────────────────────────────────┐
                    │              SOURCES DE DONNÉES            │
                    │  FRED · yfinance · Finnhub · FMP · GDELT   │
                    │  RSS Fed/BCE · NewsAPI                     │
                    └───────────────┬──────────────────────────┘
                                    │ providers/*  (repli gracieux)
                                    ▼
    ┌───────────────┐     ┌──────────────────────┐     ┌──────────────────┐
    │  SCHEDULER    │────►│      PIPELINE         │────►│   BASE DE DONNÉES │
    │ (APScheduler) │     │ collecte→IA→score→biais│     │ SQLite/PostgreSQL │
    └───────────────┘     └───────────┬──────────┘     └──────────────────┘
                                       │ STATE (mémoire, thread-safe)
                    ┌──────────────────┼───────────────────┐
                    ▼                  ▼                    ▼
            ┌──────────────┐   ┌───────────────┐   ┌──────────────────┐
            │  API MACRO   │   │ WEBHOOK TV     │   │  DASHBOARD (SSE) │
            │ /macro/*     │   │ /tradingview/* │   │  temps réel      │
            └──────┬───────┘   └───────┬────────┘   └──────────────────┘
                   │                   │
                   ▼                   ▼
           Overlay Pine        Fusion technique+macro ──► Telegram/Discord
```

## 2. Flux de données (cycle)

1. **Collecte** (`providers/`) — chaque provider est isolé et **ne lève jamais** :
   en cas d'échec réseau/quota il renvoie une source alternative gratuite ou une
   valeur neutre. Le pipeline reste vivant 24/7.
2. **Classification IA** (`engine/ai_classifier.py`) — chaque titre de news est
   transformé en impact chiffré `{gold, btc, commodities, severity}`. Claude si
   `ANTHROPIC_API_KEY`, sinon lexique pondéré déterministe.
3. **Scoring** (`engine/scoring.py`) — combine drivers de marché + risque géo +
   news en 5 facteurs bornés → score signé `[-100, +100]`.
4. **Biais** (`engine/bias.py`) — direction (seuil ±15), confiance (amplitude +
   cohérence des facteurs), niveau de risque (géo + événements imminents + DXY).
5. **Publication** — `STATE` en mémoire (lecture instantanée par l'API) +
   historisation en base (`MacroSnapshot`, `MarketDatum`, `NewsEvent`).

## 3. Modèle de scoring (transparent & calibrable)

Chaque facteur a une **borne** (`_CAPS`) pour empêcher un seul signal de dominer :

| Facteur | Logique économique (or) | Borne |
|---|---|---|
| Géopolitique | risque ↑ → valeur refuge → or ↑ | `[-10, +35]` |
| Dollar (DXY) | DXY ↑ → or ↓ (relation inverse) | `[-25, +25]` |
| Taux US | **taux réel** ↑ → coût d'opportunité → or ↓ | `[-30, +30]` |
| Inflation | anticipations ↑ → couverture → or ↑ | `[-20, +25]` |
| Sentiment risque | news + ton médiatique | `[-25, +25]` |

> Les taux **réels** (TIPS, série FRED `DFII10`) sont le driver dominant de l'or,
> pas les taux nominaux — d'où leur pondération supérieure.

Confiance = `0.65·amplitude + 0.35·cohérence` (facteurs alignés = plus sûr).

## 4. Règle de fusion (garde-fou central)

`engine/fusion.py` applique une règle non négociable : **la macro ne trade
jamais seule**. Elle ajuste la confiance d'un signal technique reçu :

- **Aligné + fort** → `reinforced` (bonus de confiance).
- **Conflit + fort** → `warning` (malus + message d'avertissement).
- **Sinon** → `standard` (quasi neutre).

Le bonus/malus est proportionnel à `|macro| × confiance_macro`, borné, de sorte
que la macro ne peut jamais transformer un mauvais signal technique en bon.

## 5. Temps réel

- **APScheduler** (`scheduler.py`) déclenche `run_pipeline()` à intervalle
  configurable (`REFRESH_MARKET_SECONDS`, défaut 300 s), job unique, coalescé.
- **Server-Sent Events** (`/macro/stream/sse`) pousse le snapshot au dashboard
  toutes les 5 s (repli automatique sur polling côté client).
- **Webhook** entrant : latence de fusion = lecture mémoire (millisecondes).

## 6. Persistance

`SQLAlchemy 2.0`. SQLite par défaut (zéro installation). Pour la prod :
`DATABASE_URL=postgresql+psycopg://…` (option TimescaleDB pour les séries
temporelles). Tables : `market_data`, `news_events`, `calendar_events`,
`macro_snapshots` (historique auditable des décisions).

## 7. Sécurité

- Webhook protégé par **secret partagé** (`API_SHARED_SECRET`, comparaison à
  temps constant `hmac.compare_digest`).
- Aucune clé en dur : tout via `.env`.
- CORS ouvert en dev → à restreindre en prod.
- Recommandé : tunnel HTTPS (cloudflared/ngrok) ou reverse-proxy (Caddy/Nginx)
  devant Uvicorn, TradingView exigeant une URL HTTPS publique.

## 8. Extensibilité

- **Nouveau driver** : ajouter un provider dans `providers/` (interface = une
  fonction `fetch_*`) et l'appeler dans `pipeline.run_pipeline`.
- **Nouvel actif** : ajouter une fonction `score_<actif>` + mapping symbole.
- **Nouvelle sortie** : ajouter un canal dans `notify/notifier.py`.
- **Backtesting** : les `MacroSnapshot` historisés permettent de rejouer et
  calibrer les pondérations a posteriori.

## 9. Coût & dimensionnement

- Fonctionne sur un VPS 1 vCPU / 1 Go.
- Toutes les sources ont un palier **gratuit** ; l'IA est optionnelle.
- Empreinte mémoire dominée par l'état courant (léger) — pas de dépendance
  lourde obligatoire (yfinance/anthropic sont des imports paresseux).

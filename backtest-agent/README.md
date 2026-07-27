# 📊 Backtest Analysis Agent — Analyste quantitatif de backtests

Un agent IA spécialisé dans **l'analyse de backtests de trading**. Il se comporte
comme un **chercheur quantitatif** : il lit les données, chiffre ses conclusions,
et propose des **tests** — il ne cherche jamais à « améliorer le win rate » pour
faire joli. À ce stade, **il ne modifie pas ton indicateur** : il l'analyse et te
recommande quoi tester.

> Principe fondateur : **les chiffres sont calculés par du code** (déterministe,
> reproductible, vérifiable). **Le LLM interprète** ces chiffres sous une
> discipline stricte. L'IA n'invente aucune statistique.

---

## 1. Architecture

```
                         ┌──────────────────────────────────────────┐
   TradingView           │            BACKTEST ANALYSIS AGENT         │
   ┌───────────┐         │                                            │
   │ Indicateur│         │  ingest.py     → normalise CSV/JSON        │
   │     ↓     │  CSV /  │  metrics.py    → analyse globale           │
   │ Stratégie │ ───────▶│  losses.py     → analyse des pertes        │
   │ (Pine)    │  JSON   │  winners.py    → analyse des gains         │
   └───────────┘         │  suggestions.py→ pistes + tests A/B        │
        │                │  features.py   → segmentation (buckets)    │
        │ alertes        │        │                                   │
        ▼                │        ▼                                   │
   webhook_server.py ───▶│  report.py ──┬─▶ payload JSON (chiffres)   │
   (forward live)        │              │                             │
                         │   llm.py ────┴─▶ rapport narratif (Claude) │
                         │        (posture « chercheur quant »)       │
                         └──────────────────────────────────────────┘
```

**Deux couches, séparées volontairement :**

| Couche | Rôle | Qui l'exécute |
|--------|------|----------------|
| **Calcul** | Toutes les métriques, corrélations, tests A/B | Code Python (déterministe) |
| **Interprétation** | Le rapport « analyste », les nuances, les priorités | LLM Claude (optionnel) |

L'agent **fonctionne sans clé API** : il produit alors un rapport complet en mode
déterministe. Avec une clé `ANTHROPIC_API_KEY`, il ajoute la lecture d'analyste
par-dessus les mêmes chiffres.

### Modules

| Fichier | Responsabilité |
|---------|----------------|
| `backtest_agent/ingest.py` | Lit CSV/JSON, détecte les colonnes (multi-langue TradingView), normalise vers un schéma stable, dérive `result` et le multiple de `R`. |
| `backtest_agent/metrics.py` | **Analyse globale** : win rate, profit factor, drawdown (abs + %), payoff, espérance, régularité mensuelle, séries, Sharpe/trade. |
| `backtest_agent/features.py` | Segmentation : sessions, heures, buckets d'ATR/volatilité, buckets de confiance ; mesure d'impact d'une condition. |
| `backtest_agent/losses.py` | **Analyse des pertes** : conditions récurrentes avant les pertes (lift), hypothèses structurelles (stop trop serré, entrée tardive, volatilité). |
| `backtest_agent/winners.py` | **Meilleurs trades** : combinaisons de filtres, meilleures sessions/heures, R:R — classées par **score robuste**, jamais par win rate. |
| `backtest_agent/suggestions.py` | **Améliorations + tests A/B** : filtres/paramètres à tester, avec **risque de sur-optimisation** explicite. |
| `backtest_agent/prompts.py` | Le *system prompt* qui impose la posture de chercheur quant. |
| `backtest_agent/llm.py` | Client Claude optionnel. |
| `backtest_agent/report.py` | Assemble le rapport (JSON + Markdown). |
| `backtest_agent/cli.py` | Ligne de commande. |
| `tradingview/strategy_template.pine` | Gabarit pour transformer ton indicateur en stratégie exportable. |
| `tradingview/webhook_server.py` | Récepteur d'alertes TradingView → CSV (suivi forward). |

---

## 2. Installation

```bash
cd backtest-agent
pip install -r requirements.txt        # pandas + numpy suffisent pour le coeur
```

La couche LLM (`anthropic`) et le webhook (`flask`) sont optionnels.

---

## 3. Utilisation en 30 secondes

```bash
# 1) Générer un jeu de données de démonstration (structuré exprès)
python examples/generate_sample.py -n 300

# 2) Analyser (mode déterministe, sans IA)
python -m backtest_agent.cli analyze examples/sample_trades.csv \
       -o reports/rapport.md --json reports/stats.json --no-llm

# 3) Avec la couche analyste Claude
export ANTHROPIC_API_KEY=sk-...
python -m backtest_agent.cli analyze examples/sample_trades.csv -o reports/rapport.md
```

Le rapport `reports/rapport.md` contient les 5 sections demandées : analyse
globale, analyse des pertes, meilleurs trades, suggestions, plan de tests A/B.

---

## 4. Le rapport produit

1. **Analyse globale** — taux de réussite, profit factor, drawdown, ratio
   gain/perte, régularité mensuelle, nombre de trades.
2. **Analyse des pertes** — causes probables (mauvais contexte, faux signaux,
   manque de confirmation, volatilité, entrée tardive, stop mal placé) et
   **conditions qui reviennent avant les pertes** (mesure de *lift*).
3. **Meilleurs trades** — combinaisons de filtres gagnantes, horaires/sessions
   performants, régimes favorables, meilleurs R:R.
4. **Suggestions** — quels filtres/paramètres tester, quelles règles renforcer
   ou supprimer.
5. **Tests A/B** — pour chaque piste : *problème détecté → modification proposée
   → résultat attendu (A vs B) → risque de sur-optimisation → règle de décision*.

### La discipline anti-« IA qui gonfle les chiffres »

L'agent applique des règles non négociables (dans `prompts.py` **et** dans le
code) :

- **Jamais** de recommandation basée sur le seul win rate.
- Critères de décision, dans l'ordre : **robustesse → profit factor → drawdown →
  taille d'échantillon → stabilité de l'espérance**.
- Classement par **score robuste** = `espérance × √N × pénalité_petit_échantillon`.
  Une « pépite » sur 12 trades ne remonte jamais devant un effet stable sur 150.
- Chaque filtre A/B porte un **risque de sur-optimisation** (FAIBLE/MOYEN/ÉLEVÉ)
  calculé sur la taille d'échantillon restante et la part de trades supprimés.
- Un filtre qui jette > ~75 % des trades est signalé **ÉLEVÉ** et déclassé.
- Corrélation ≠ causalité : les conditions « avant les pertes » sont des pistes.

> ⚠️ Les tests A/B intégrés sont **in-sample** (sur les mêmes données) : ce sont
> des **pré-sélections d'hypothèses**, pas des preuves. La validation réelle se
> fait en **walk-forward hors échantillon** (§6).

---

## 5. Connecter les résultats TradingView

Tu as **deux voies**, complémentaires.

### Voie A — Export du Strategy Tester (recommandée pour le backtest historique)

C'est la source la plus fiable car elle contient le **résultat et le PnL réels**.

1. Transforme ton indicateur en stratégie avec `tradingview/strategy_template.pine` :
   remplace les blocs `>>> REMPLACE` par les vraies variables de ton indicateur
   (signaux + conditions OB/FVG/sweep/VWAP/structure/ATR…). On **ne touche pas** à
   la logique : on l'expose.
2. Ajoute la stratégie au graphique → onglet **Strategy Tester**.
3. Onglet **List of Trades** → bouton d'export → **Export CSV**.
4. Analyse le fichier :
   ```bash
   python -m backtest_agent.cli analyze mon_export_tradingview.csv -o reports/rapport.md
   ```

L'ingestion gère les noms de colonnes TradingView (FR/EN) automatiquement. Pour
enrichir l'export avec tes conditions (OB, FVG…), ajoute-les dans la stratégie via
`strategy.entry(..., comment=...)` ou des colonnes de plot exportables, ou utilise
la Voie B en parallèle pour capturer le contexte.

### Voie B — Webhook (pour le suivi forward / temps réel)

TradingView (offre payante) peut envoyer une **alerte** vers une URL à chaque
signal. `strategy_template.pine` construit déjà un **payload JSON** avec toutes les
conditions du moment.

```bash
pip install flask
python tradingview/webhook_server.py --out data/live_trades.csv --port 8080
# expose le port publiquement (ex: ngrok http 8080) et mets l'URL /tradingview
# dans l'alerte TradingView, message = {{strategy.order.alert_message}}
```

Chaque alerte devient une ligne de `data/live_trades.csv`, analysable comme un
backtest :

```bash
python -m backtest_agent.cli analyze data/live_trades.csv -o reports/forward.md
```

### Format attendu (schéma interne)

Peu importe la source, l'agent cherche à retrouver ces champs (voir
`config/schema.yaml` pour toutes les correspondances) :

| Champ | Exemple | Requis |
|-------|---------|--------|
| `datetime` | `2025-01-02 14:30:00` | recommandé |
| `symbol` | `BTCUSDT` | recommandé |
| `timeframe` | `15m` | recommandé |
| `direction` | `BUY` / `SELL` | recommandé |
| `entry_price`, `stop_loss`, `take_profit`, `exit_price` | nombres | pour calculer le R |
| `result` | `WIN` / `LOSS` | dérivé du PnL si absent |
| `pnl` ou `pnl_r` | `+1.8` | **au moins un des deux** |
| `duration_min` | `45` | optionnel |
| `confidence` | `0.72` ou `72` | optionnel |
| *conditions* | `ob, fvg, sweep, vwap_up, structure_up, atr…` | tout le reste |

**Toute colonne supplémentaire est traitée comme une condition de marché** et
entre automatiquement dans l'analyse des pertes/gains et des combinaisons.

---

## 6. Bien valider (walk-forward) — indispensable avant de toucher l'indicateur

Les tests A/B de l'agent te disent *quelles hypothèses valent la peine*. Pour
éviter la sur-optimisation :

1. **Découpe** tes données en période *in-sample* (ex. 70 %) et *out-of-sample*
   (30 %). Analyse l'IS, retiens une piste, puis **re-mesure-la sur l'OOS**.
2. Ne garde une règle que si elle améliore **profit factor + drawdown** de façon
   **stable** sur les deux périodes, avec **assez de trades**.
3. Répète sur plusieurs actifs / plusieurs régimes de marché.
4. **Seulement alors**, envisage de modifier l'indicateur (étape suivante, hors
   périmètre de cet agent d'analyse).

### Walk-forward automatique (intégré)

La commande `walkforward` fait tout : elle découpe le backtest
chronologiquement, cherche des filtres sur l'**in-sample**, les **rejoue sur
l'out-of-sample**, et rend un **verdict par règle** (`TIENT`, `REJETÉ`,
`AMBIGU`, `NON TESTABLE`).

```bash
python -m backtest_agent.cli walkforward examples/sample_trades.csv \
       --split 0.7 -o reports/walkforward.md --json reports/wf.json
```

Exemple de sortie :

```
Règles testées : 4 — confirmées hors échantillon : 2

## Règle #2 — TIENT (confirmé hors échantillon)
- Règle : Exclure les trades où _hour = 22.
- In-sample :     ΔPF 0.15, Δespérance 0.045 (199 trades, 0.95 conservés)
- Out-of-sample : ΔPF 0.07, Δespérance 0.032 (88 trades, 0.98 conservés)
```

Une règle n'est marquée `TIENT` que si elle améliore **profit factor ET
espérance** en IS **ET** en OOS, avec un échantillon OOS suffisant. C'est le
garde-fou anti-sur-optimisation le plus important de l'agent.

> Analyse manuelle équivalente si tu préfères deux fichiers séparés :
> ```bash
> python -m backtest_agent.cli analyze data/in_sample.csv  -o reports/is.md
> python -m backtest_agent.cli analyze data/out_sample.csv -o reports/oos.md
> ```

---

## 7. Roadmap (extensions possibles)

- Walk-forward automatisé multi-période intégré au CLI.
- Détection de régimes de marché (tendance/range) via clustering.
- Export du rapport en HTML/PDF.
- Intégration Monte-Carlo sur l'ordre des trades (robustesse du drawdown).
- Étape 2 du projet : agent *proposant* des modifications d'indicateur, une fois
  les hypothèses validées ici.

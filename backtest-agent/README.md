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
                    ┌─────────────────────────────────────────────────┐
  TradingView       │           BACKTEST ANALYSIS AGENT               │
  ┌───────────┐     │                                                 │
  │ Indicateur│     │  ANALYSER      ingest → metrics → losses        │
  │     ↓     │ CSV │                       → winners → suggestions   │
  │ Stratégie │────▶│                                                 │
  │  (Pine)   │JSON │  VALIDER       walkforward  (split unique)      │
  └───────────┘     │                rolling      (fenêtres glissantes)│
       │            │                robustness   (Monte-Carlo)       │
       │ alertes    │                                                 │
       ▼            │  PROPOSER      proposals → strategy_candidate.pine
  webhook_server ──▶│                                                 │
  (suivi forward)   │  TRANCHER      validate → compare               │
                    │                                                 │
                    │  report.py ──┬─▶ payload JSON (chiffres)        │
                    │   llm.py ────┴─▶ rapport narratif (Claude)      │
                    │        (posture « chercheur quant »)            │
                    └─────────────────────────────────────────────────┘
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
| `backtest_agent/ingest.py` | Lit CSV/JSON, détecte les colonnes (multi-langue TradingView), normalise vers un schéma stable, dérive `result` et le multiple de `R`, décode le score de qualité de signal si présent dans le Signal enrichi. |
| `backtest_agent/metrics.py` | **Analyse globale** : win rate, profit factor, drawdown (abs + %), payoff, espérance, régularité mensuelle, séries, Sharpe/trade. |
| `backtest_agent/features.py` | Segmentation : sessions, heures, buckets d'ATR/volatilité, buckets de confiance ; mesure d'impact d'une condition. |
| `backtest_agent/losses.py` | **Analyse des pertes** : conditions récurrentes avant les pertes (lift), hypothèses structurelles (stop trop serré, entrée tardive, volatilité). |
| `backtest_agent/winners.py` | **Meilleurs trades** : combinaisons de filtres, meilleures sessions/heures, R:R — classées par **score robuste**, jamais par win rate. |
| `backtest_agent/suggestions.py` | **Améliorations + tests A/B** : filtres/paramètres à tester, avec **risque de sur-optimisation** explicite. |
| `backtest_agent/walkforward.py` | **Validation walk-forward** : split IS/OOS, rejoue les filtres hors échantillon, verdict par règle. |
| `backtest_agent/proposals.py` | **Étape 2** : traduit les règles validées en **code Pine**, génère une stratégie candidate à re-backtester. |
| `backtest_agent/robustness.py` | Monte-Carlo sur l'ordre des trades, cohérence par segment (actif / période). |
| `backtest_agent/validate.py` | **Étape 3** : valide la pile de filtres combinée, compare deux re-backtests réels. |
| `backtest_agent/rolling.py` | **Walk-forward glissant** : fenêtres successives, stabilité des règles, WFE, optimisation de seuil. |
| `backtest_agent/prompts.py` | Le *system prompt* qui impose la posture de chercheur quant. |
| `backtest_agent/llm.py` | Client Claude optionnel. |
| `backtest_agent/report.py` | Assemble le rapport (JSON + Markdown). |
| `backtest_agent/jsonutil.py` | Sérialisation JSON stricte (jamais de `NaN`/`Infinity`, non conformes RFC 8259). |
| `backtest_agent/htmlview.py` | Convertisseur Markdown → HTML minimal (sans dépendance), pour afficher un rapport dans le navigateur. |
| `backtest_agent/cli.py` | Ligne de commande (`analyze`, `walkforward`, `propose`, `validate`, `compare`, `rolling`, `view`, `pipeline`). |
| `tests/` | 135 tests, dont la vérification de la discipline anti-sur-optimisation. |
| `tradingview/strategy_template.pine` | Gabarit pour transformer ton indicateur en stratégie exportable. |
| `tradingview/webhook_server.py` | Récepteur d'alertes TradingView → CSV (suivi forward). |

---

## 2. Installation

```bash
cd backtest-agent
pip install -e .              # installe la commande `backtest-agent`
```

Extras optionnels — l'agent est pleinement fonctionnel sans eux :

```bash
pip install -e ".[llm]"       # couche d'interprétation Claude
pip install -e ".[webhook]"   # récepteur d'alertes TradingView
pip install -e ".[dev]"       # pytest
```

### Vérifier que tout marche

```bash
pytest                        # 135 tests
```

La suite couvre l'ingestion, les métriques, le walk-forward, la traduction Pine,
la validation, le CLI **et la discipline anti-sur-optimisation elle-même**
(cf. `tests/test_discipline.py` : on vérifie par le code qu'une « pépite » sur
5 trades ne peut pas primer sur un effet stable sur 150, et que sur du bruit pur
l'agent ne conclut jamais `ADOPTER`).

---

## 3. Utilisation en 30 secondes

Le plus simple — **tout le cycle en une commande** :

```bash
python examples/generate_sample.py -n 300      # jeu de démo
backtest-agent pipeline examples/sample_trades.csv -o reports/
```

Ça produit dans `reports/` : `1_analyse.md`, `2_walkforward.md`,
`3_propositions.md`, `4_validation.md`, `5_walkforward_glissant.md` et
`strategy_candidate.pine`, puis affiche un récapitulatif :

```
  Trades analysés           : 400
  Règles confirmées (OOS)   : 2
  Propositions générées     : 2
  Règles robustes (glissant): 0
  Verdict final             : REJETER
```

> Les deux dernières lignes se lisent ensemble : le walk-forward simple confirme
> 2 règles, le glissant n'en retient aucune. C'est le glissant qui a raison.

Ou commande par commande :

```bash
backtest-agent analyze examples/sample_trades.csv -o reports/rapport.md --no-llm

# avec la couche analyste Claude
export ANTHROPIC_API_KEY=sk-...
backtest-agent analyze examples/sample_trades.csv -o reports/rapport.md
```

> Toutes les commandes s'utilisent aussi via `python -m backtest_agent.cli …`
> si tu préfères ne rien installer.

Le rapport contient les 5 sections demandées : analyse globale, analyse des
pertes, meilleurs trades, suggestions, plan de tests A/B.

### Afficher un rapport en HTML (`view`)

Tous les rapports sont écrits en Markdown brut — lisibles dans un éditeur de
code, mais peu agréables dans le Bloc-notes (les `#`, `**`, `|` restent
visibles au lieu d'être mis en forme). La commande `view` convertit n'importe
quel rapport `.md` en page HTML stylée et l'ouvre dans le navigateur par défaut :

```bash
backtest-agent view reports/1_analyse.md
```

Aucune dépendance externe : le convertisseur (`backtest_agent/htmlview.py`)
couvre exactement la syntaxe que les rapports du paquet utilisent (titres,
gras, tableaux, listes, citations), sans installer de bibliothèque Markdown
tierce. Utilise `--no-open` pour générer le `.html` sans ouvrir de fenêtre
(utile en script ou en CI).

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

L'ingestion gère les noms de colonnes TradingView (FR/EN) automatiquement,
**y compris le format « deux lignes par trade »** (une ligne « Entrer long/short »,
une ligne « Sortir du long/short », reliées par un numéro de trade commun) que
produit l'export standard du Strategy Tester : les deux lignes sont fusionnées
en un seul trade avant tout calcul, pour ne jamais compter un trade deux fois.
Le contexte supplémentaire (raison de sortie, commission, MFE/MAE, durée en
barres) est conservé comme conditions analysables. Pour
enrichir l'export avec tes conditions (OB, FVG…), ajoute-les dans la stratégie via
`strategy.entry(..., comment=...)` ou des colonnes de plot exportables, ou utilise
la Voie B en parallèle pour capturer le contexte.

Cas particulier reconnu automatiquement : si `comment=` sur `strategy.entry()`
contient la décomposition d'un score de qualité de signal au format
`S<total> L<liquidite> T<structure> Z<zone> W<wyckoff> H<htf> V<volume> P<vwap>`
(entiers, séparés par des espaces), l'ingestion la décode en colonnes
`score_total`, `score_liquidity`, `score_structure`, `score_zone`,
`score_wyckoff`, `score_htf`, `score_volume`, `score_vwap` — analysables comme
n'importe quelle condition (pertes, meilleurs trades, buckets de score). Aucun
effet si le Signal ne suit pas ce format.

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

## 7. Étape 2 — Proposer des modifications d'indicateur

Une fois des règles **confirmées en walk-forward**, l'agent peut passer de
l'analyse à la **proposition de code**. Il reste un chercheur : il ne propose
**que** des règles au verdict `TIENT` (améliorent PF *et* espérance IS *et* OOS),
et il ne les applique jamais tout seul — il génère un **fichier candidat à
re-backtester**.

```bash
python -m backtest_agent.cli propose examples/sample_trades.csv \
       -o reports/propositions.md \
       --candidate reports/strategy_candidate.pine
```

Ce que ça produit :

- **`propositions.md`** : pour chaque modification → hypothèse validée, preuve
  chiffrée **in-sample ET out-of-sample**, code Pine exact, plan de rollback.
- **`strategy_candidate.pine`** : une copie de ta stratégie où l'agent a inséré,
  entre les marqueurs `AGENT_FILTERS`, les gardes d'entrée correspondantes :

  ```pine
  // <<< AGENT_FILTERS_BEGIN >>>
  filter1 = not (hour(time) == 22)              // règle validée
  filter2 = dayofweek == dayofweek.saturday     // règle validée
  passFilters = filter1 and filter2
  // <<< AGENT_FILTERS_END >>>
  ```

  Les entrées de la stratégie sont déjà conditionnées par `and passFilters`, donc
  il suffit de **coller le fichier candidat dans TradingView et de relancer le
  Strategy Tester** pour mesurer l'effet réel.

**Traducteur condition → Pine.** L'agent sait convertir : conditions booléennes
(OB, FVG, sweep, VWAP, structure), heures, sessions, jours de semaine, seuils de
confiance, plages d'ATR. Toute condition qu'il ne peut pas traduire **de façon
sûre** est marquée « à implémenter manuellement » plutôt que de générer du code
faux.

**S'il n'y a aucune règle validée**, l'agent le dit et **ne propose rien** — c'est
le comportement voulu : ne rien changer vaut mieux que sur-optimiser.

> ⚠️ Un fichier candidat n'est **pas** une amélioration prouvée. Il faut le
> re-backtester (idéalement sur d'autres actifs et périodes) avant d'adopter la
> moindre modification.

## 8. Étape 3 — Boucle fermée : valider avant d'adopter

**Limite assumée d'emblée :** on ne peut **pas exécuter du Pine localement**
(TradingView est une plateforme fermée). La boucle se ferme donc en deux temps.

### A. `validate` — tester la pile de filtres **combinée**

L'étape 2 valide chaque règle **individuellement**. Or des règles saines prises
séparément peuvent très mal se combiner : elles retirent souvent les mêmes trades
et l'empilement vide l'échantillon. `validate` teste la pile **entière** :

```bash
python -m backtest_agent.cli validate examples/sample_trades.csv \
       -o reports/validation.md --json reports/validation.json
```

Ce qu'il contrôle :

| Contrôle | Question posée |
|---|---|
| **Effet combiné** | La pile complète améliore-t-elle vraiment PF + espérance ? |
| **Contribution marginale** | Que perd-on en retirant *ce* filtre de la pile ? |
| **Cohérence par actif** | L'effet tient-il sur tous les symboles, ou un seul ? |
| **Cohérence par période** | L'effet tient-il sur toutes les tranches de temps ? |
| **Monte-Carlo** | Le drawdown observé est-il de la chance d'ordonnancement ? |

Verdict : **`ADOPTER`** / **`PRUDENCE`** / **`REJETER`**, avec chaque motif explicité.

**Exemple réel sur le jeu de démo** — les 2 propositions de l'étape 2 semblaient
excellentes isolément (PF +3.6 !), mais la validation combinée les **rejette** :

```
## Verdict : ❌ REJETER
- ❌ La pile de filtres supprime 87% des trades : stratégie dénaturée.
- ⚠️ 1 segment(s) par période ne conservent AUCUN trade après filtrage (P1).
```

C'est le comportement voulu : **refuser un beau chiffre obtenu en jetant les
données**. Un agent qui « améliore » aurait adopté ; celui-ci refuse.

### B. `compare` — comparer deux **vrais** re-backtests

C'est l'étape qui ferme réellement la boucle. Tu re-backtestes le `.pine`
candidat sur TradingView, tu exportes, et tu compares les deux exports réels :

```bash
python -m backtest_agent.cli compare baseline_export.csv candidat_export.csv \
       -o reports/comparaison.md
```

Ici les deux jeux viennent du Strategy Tester, donc le **chaînage des positions
est correct des deux côtés** — ce qu'un simple rejeu ne peut pas simuler.

> ⚠️ `validate` rejoue les filtres sur les trades **existants**. Or un filtre
> change aussi **quels trades existent** (une position non prise libère le
> créneau pour une autre). Seul `compare` sur deux vrais exports est exempt de
> ce biais.

### Le cycle complet

```
analyze → walkforward → propose → validate → rolling → [re-backtest TV] → compare
   │          │            │          │          │                           │
 lire les  valider      traduire   tester la  vérifier                   trancher sur
 données   hors         en Pine    pile       la tenue                   des données
           échantillon  les règles combinée   dans le temps              réelles
```

## 9. Walk-forward glissant — la validation la plus sévère

Le walk-forward simple (§6) coupe **une fois**. Il ne répond donc pas à la vraie
question : *l'effet survit-il au passage du temps et au changement de régime ?*
La commande `rolling` rejoue le cycle « chercher puis vérifier » sur **plusieurs
fenêtres successives**.

```bash
backtest-agent rolling trades.csv -o reports/glissant.md
backtest-agent rolling trades.csv --anchored          # fenêtre qui grandit
backtest-agent rolling trades.csv --folds 8 --train-window 4
```

Deux modes :

| Mode | Fenêtre d'apprentissage | Quand l'utiliser |
|---|---|---|
| `rolling` (défaut) | taille **fixe** qui glisse | marchés qui changent de régime |
| `--anchored` | **grandit** depuis le début | effet supposé stationnaire |

### Ce qu'il apporte qu'un split unique ne peut pas donner

**1. La stabilité prime sur le score.** Une règle n'est `ROBUSTE` que si elle
franchit **quatre** exigences cumulatives — chacune bouche un trou par lequel du
bruit passait :

| Exigence | Pourquoi |
|---|---|
| ≥ 3 fenêtres | « 2 fois sur 2 » arrive une fois sur quatre au hasard |
| effet moyen > 0 | évidence de base |
| **t ≥ 2** | l'effet doit dépasser sa propre dispersion |
| **taille d'effet ≥ 0,15** | et peser assez face à la volatilité d'un trade |

Sans le dernier critère, un gain de 0,07R sur des trades d'écart-type 1,0R
passait pour « robuste » alors qu'il est économiquement nul.

**2. La walk-forward efficiency (WFE)** — quelle part de l'avantage trouvé en
apprentissage survit réellement :

```
- Avantage moyen en apprentissage : 0.3872
- Avantage moyen hors échantillon : 0.008
- WFE = 0.021

> Moins de 30% de l'avantage survit : forte sur-optimisation.
```

**Démonstration concrète.** Sur le jeu de démo, la règle « Saturday » avait été
confirmée `TIENT` par le walk-forward simple. Le glissant la classe **`REJETÉE`**
(0/4 fenêtres). Le split unique produisait un faux positif ; le glissant le
rattrape.

### Optimiser un seuil en walk-forward

```bash
backtest-agent rolling trades.csv --threshold confidence
```

Choisit le meilleur seuil sur chaque fenêtre d'apprentissage, puis mesure ce
qu'il donne sur la suivante. **Le diagnostic utile n'est pas le gain moyen mais
la stabilité du seuil** : s'il saute d'une fenêtre à l'autre, il s'ajuste au
bruit et aucune valeur ne mérite d'être figée dans l'indicateur.

> ⚠️ On ne peut optimiser ici que des **seuils de filtrage** (confiance, plage
> d'ATR…). Un paramètre qui change *quels trades existent* — un multiplicateur
> de stop, par exemple — exige un vrai re-backtest TradingView.

## 10. Roadmap (extensions possibles)

- Walk-forward automatisé multi-période intégré au CLI.
- Détection de régimes de marché (tendance/range) via clustering.
- Export du rapport en HTML/PDF.
- Automatisation de l'aller-retour TradingView (l'export reste manuel aujourd'hui).

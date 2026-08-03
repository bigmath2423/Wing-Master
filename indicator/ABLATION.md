# Journal d'ablation — XAUUSD SMC Confluence Signals

Méthode quant : **une amélioration = un commit = un interrupteur indépendant**. Chaque
amélioration peut être activée/désactivée sans toucher aux autres. La comparaison
avant/après se fait en flippant le toggle dans TradingView (ou en chargeant
`xauusd_smc_v14_baseline.pine`, gelé, sur un second graphique).

## Fichiers

| Fichier | Rôle |
|---------|------|
| `xauusd_smc_v14_baseline.pine` | **Référence GELÉE.** Ne jamais modifier. Version d'origine (v14). |
| `xauusd_smc_working.pine` | Version de travail. Reçoit les améliorations, chacune derrière un toggle. |

> ⚠️ **Compilation** : aucun compilateur Pine v6 n'est disponible hors TradingView.
> Chaque étape est validée par revue statique. Coller dans TradingView pour la
> validation finale avant backtest.

## Convention des interrupteurs

Tous les toggles d'amélioration sont regroupés dans le groupe d'inputs
`⓪ AMÉLIORATIONS (audit) — interrupteurs A/B`. Mettre **tous** à leur valeur
« baseline » reproduit EXACTEMENT le comportement de `xauusd_smc_v14_baseline.pine`.

## Suivi des améliorations

| ID | Amélioration | Toggle | Défaut | Impact signaux | Risque de dégradation | Statut |
|----|--------------|--------|--------|----------------|----------------------|--------|
| B1 | Faux BOS/CHoCH (crossover sur niveau mobile) | `fixBreakOn` | ON | Oui | Faible (peut manquer de rares breaks same-bar) | ✅ fait |
| B2 | `showLiq` ne doit plus gater la détection de sweep | `fixSweepGateOn` | ON | Oui (marginal) | Très faible | ✅ fait |
| B3 | Buffer exec défait le snapping TP structurel | `fixTpSnapOn` | OFF | Non (exécution) | Faible (arbitrage hit-rate/RR) | ✅ fait |
| S1 | Confiance affichee calibree (affichage seul) | `scoreRealistOn` | OFF | Non (affichage seul) | Nul | ✅ fait |
| B1b | Faux BOS/CHoCH sur la structure MTF (f_msStructure) | `fixBreakMtfOn` | OFF | Oui (via score HTF) | Faible | ✅ fait |
| C1 | Signaux confirmés en clôture (anti-repaint intrabar) | `sigConfirmOn` | ON | Non en historique (backtest identique), améliore le réel | Nul (neutre en backtest) | ✅ fait |
| B4 | Faux cross Wyckoff au démarrage d'un range | — | — | — | — | ✅ vérifié : non-bug (na → pas de cross) |
| P1 | Nettoyage code mort (sous-ensemble sûr) | — | — | Non (inerte) | Nul | ✅ partiel (voir ci-dessous) |

Statut actuel : **B1, B2, B3, S1, B1b implémentés + P1 partiel.** Tous les toggles à leur valeur baseline
(`fixBreakOn=false`, `fixSweepGateOn=false`, `fixTpSnapOn=false`, `scoreRealistOn=false`, `fixBreakMtfOn=false`) →
comportement de trading identique à `xauusd_smc_v14_baseline.pine` (P1 ne retire que du code write-only inerte).
`scoreRealistOn=false`) → le fichier de travail = `xauusd_smc_v14_baseline.pine`.

---

## Protocole de backtest / ablation (à exécuter dans TradingView)

1. Coller `xauusd_smc_working.pine` → vérifier qu'il **compile** sans erreur.
2. **Baseline** : mettre les 4 toggles ⓪ sur leur valeur baseline. Backtester
   XAUUSD M5 puis M15 sur une période représentative (tendance + range + news).
   Noter : nb trades, winrate, R:R moyen réalisé, drawdown max, profit factor.
3. **Une amélioration à la fois** : activer UN SEUL toggle, re-backtester,
   comparer aux mêmes métriques. Ne garder que si l'effet est positif ou neutre.
4. Ordre suggéré : B2 (quasi neutre) → B1 (le plus impactant) → S1 (affichage,
   ne change pas les trades, juste la lecture) → B3 (arbitrage exécution).
5. **Empilement** : une fois chaque toggle validé seul, tester les combinaisons
   retenues ensemble (les effets ne sont pas toujours additifs).

> Astuce A/B côte-à-côte : charger `xauusd_smc_v14_baseline.pine` sur un 2ᵉ
> graphique du même symbole/UT et comparer visuellement les signaux.

---

## Guide de tuning (inputs EXISTANTS — aucun code à changer, juste des valeurs à tester)

Ces réglages sont déjà des inputs à leur valeur baseline. À tester **un par un**,
comme les toggles, en gardant la baseline comme référence.

| Input | Baseline | À tester (M5) | Pourquoi (audit) | Risque |
|-------|----------|---------------|------------------|--------|
| `chopFilterOn` (ADX anti-range) | OFF | **ON** | Le range est la 1ʳᵉ source de pertes ; seul filtre directionnel | Coupe des breakouts précoces |
| `slMinAtr` (dist. min SL) | 0.5 | **0.7–0.8** | 0.5 ATR se fait sweeper par spread+mèche sur l'or M5 | SL plus large = R par trade ↑ |
| `slExecBufSpread` (plancher spread) | 0.0 | **0.15–0.30** | À 0, le SL ignore le coût broker réel (optimiste) | Idem, risque absolu ↑ |
| `pfUseVolFilter` (filtre volume) | ON | **OFF** (comparer) | Tick-volume or peu fiable | Perte d'un filtre (à mesurer) |
| `signalCooldown` | 10 | **15–20** (M5) | Anti-whipsaw en range | Moins de trades |
| `deScoreMin` / `deScoreAPlus` | 80 / 85 | Recalibrer après backtest | Score gonflé (voir S1) | Change la sélectivité |

---

## P1 — Nettoyage

### ✅ Appliqué (sous-ensemble sûr — code write-only inerte, aucun impact de trading)

| Variable | Où | Statut |
|----------|----|--------|
| `barsSinceLiqSweepLow` / `barsSinceLiqSweepHigh` | LIQUIDITY SWEEPS | **retiré** (décl + `+=1` + `:=0`, jamais lus) |
| `msSwingTrend` | fin Module 1 (swings) | **retiré** (jamais consommé) |

> ⚠️ À re-compiler dans TradingView pour confirmation. Le fichier gelé conserve l'original.

### ⏸️ Volontairement NON retiré (lié à une fonctionnalité utilisateur)

| Variable | Raison |
|----------|--------|
| `rawK` / `stochK` / `stochD` / `oscVal` | Chaîne stochastique morte (jamais affichée), MAIS reliée à l'option d'input `oscType = "Stochastic"`. La retirer neutraliserait cette option UI. Consigne « ne pas supprimer de fonctionnalité non testée » → laissée intacte. À trancher : soit **reconnecter** `oscVal` au dashboard (réparer la feature), soit retirer l'option Stochastic + sa chaîne (−4 `ta.*`/barre). |

### ⏸️ Redondance `request.security` (perf, non appliqué — risque de changement de comportement)

Sur un chart M5, `msTfExec="5"` interroge le TF courant (redondant + déclenche
`f_msTfWarn`). D1 est demandé 2× (`msTfContext` et `pzoD1C`) avec des EMA
différentes. À factoriser prudemment **après** vérification de compilation.

---

## Optionnel / à valider avant de coder (items mineurs de l'audit)

| ID | Sujet | Décision |
|----|-------|----------|
| B1b | `f_msStructure()` (MTF) a le MÊME bug de crossover que B1, et alimente le score via `msCtxTrend`. | À ajouter en toggle séparé (`fixBreakMtfOn`, défaut OFF) car il modifie le module de score — à faire isolément et backtester. |
| B4 | Faux cross `wyCrossUpMid`/`wyCrossDnMid` au démarrage d'un range (niveau `wyMid` passe de na à une valeur). | Impact faible ; guard possible si le backtest montre des figures Wyckoff parasites. |
| B5 | `smcRangeTop = math.max(swingHighVal, swingLowVal)` sémantiquement flou en fort trend. | Garde défensive, impact très faible ; laisser tel quel sauf anomalie constatée. |

(Le tableau du haut est complété au fur et à mesure.)

---

## 🧪 Version BACKTEST (`xauusd_smc_STRATEGY.pine`)

Copie **strictement identique** de `xauusd_smc_working.pine`, convertie en `strategy()`
pour utiliser le **Strategy Tester** de TradingView.

**Preuve de non-régression** : le `diff` entre le corps des deux fichiers ne contient
**que la ligne 2** (`indicator(` → `strategy(`). Aucune ligne de logique, de score, de
filtre ou de niveau n'a été touchée. Le moteur d'exécution ajouté en fin de fichier
**lit** seulement `buySignal` / `sellSignal` / `tmEntry` / `tmSL` / `tmT1-T3`.

### Réglages ajoutés (aucun filtre, uniquement de l'exécution)

| Groupe | Réglage | Défaut |
|--------|---------|--------|
| Propriétés TradingView | Capital de départ | 10 000 (modifiable dans l'onglet Propriétés) |
| Propriétés TradingView | Commission | 0.0 (onglet Propriétés) |
| Propriétés TradingView | Slippage | 95 ticks (onglet Propriétés) |
| Exécution | Type d'entrée (Marché / Limite) | Marché |
| Exécution | Validité ordre limite (barres) | 10 |
| Exécution | Sorties (3 paliers / TP1 seul / TP Final seul) | 3 paliers |
| Exécution | % position TP1 / TP2 | 40 / 30 |
| Position | Mode de taille (Risque % / Fixe) | Risque % |
| Position | Risque par trade | 1 % |
| Position | Inversion sur signal opposé | ON |

### Métriques fournies par le Strategy Tester
Win rate · Nombre de trades · Profit net · **Profit factor** · **Drawdown maximal** ·
Meilleur / pire trade · **Courbe de capital** (onglet « Performance »).

### ⚠️ À savoir pour lire les résultats
- **Entrée « Marché »** = tous les signaux sont mesurés → mesure honnête de l'indicateur.
  **« Limite »** = plus fidèle au plan de trade, mais des ordres ne seront jamais remplis
  (moins de trades, résultats plus flatteurs). Compare les deux.
- **Commission et slippage à 0 par défaut** : renseigne le coût réel de ton broker
  (spread or ≈ 0.20-0.50) avant toute conclusion, sinon le résultat est optimiste.
- Les ordres s'exécutent à **l'ouverture de la barre suivante** (`process_orders_on_close=false`),
  ce qui est le comportement réaliste.

---

## 💱 Calibrage broker réel — FXCess (spread mesuré 0,95 $ sur XAUUSD)

Valeurs pré-réglées **par défaut** dans `xauusd_smc_working.pine` et
`xauusd_smc_STRATEGY.pine` pour ne rien avoir à configurer.

| Réglage | Avant | Après | Pourquoi |
|---------|-------|-------|----------|
| `slExecBufSpread` | 0.0 | **1.10** | Spread réel 0,95 + marge slippage → le SL n'est jamais placé plus près que le coût d'exécution |
| `slMinAtr` | 0.5 | **1.2** | Un SL de 0,5 ATR (~1,4 $ en M5) est balayé par 0,90 de spread. 1.2 ATR ramène le spread sous ~15 % du risque en M15 |
| `slippage` (stratégie) | 0 | **95 ticks** | 0,95 $ = 95 ticks (tick 0,01). Modélisation prudente : spread + slippage |

> Le site FXCess affiche 0,42 (vitrine, marché calme) ; le **réel mesuré est 0,95**.
> C'est la valeur retenue. Tous ces réglages restent des **inputs** modifiables :
> remettre 0.0 / 0.5 / 0 restaure l'ancien comportement.

### ⚠️ Conséquence majeure — coût du spread = spread ÷ distance du SL

| UT | ATR typique | SL à 1.2 ATR | Poids du spread 0,95 |
|----|-------------|--------------|----------------------|
| M5 | ~2,5-3 $ | ~3,3 $ | ~27 % du risque ⚠️ |
| M15 | ~5-6 $ | ~6,6 $ | ~14 % du risque 🟡 |
| H1 | ~10-13 $ | ~13 $ | ~7 % du risque ✅ |

**M5 reste déconseillé avec ce spread** (même avec le SL élargi). M15 est le
minimum praticable, H1 le plus confortable. Le levier le plus puissant reste un
**compte ECN** (spread ~0,25 + commission) qui diviserait ce coût par ~3.

---

## 💰 Rentabilité face au spread — analyse de seuil (TCA)

Formule exacte du **win rate d'équilibre** avec un coût fixe :

```
W_équilibre = (1 + S/D) / (R + 1)
   S = coût aller-retour (spread)   D = distance du SL   R = multiple R:R
```

Avec **S = 0,95** (FXCess Classic) et un SL à 1.2 ATR :

| UT | SL | spread/risque | Win rate requis (R:R 2) | Win rate requis (R:R 3) |
|----|----|---------------|-------------------------|-------------------------|
| M5 | 3,3 $ | 27 % | **42,4 %** (+9,1 pt) | **31,8 %** (+6,8 pt) |
| M15 | 6,6 $ | 14 % | **37,9 %** (+4,5 pt) | **28,4 %** (+3,4 pt) |
| H1 | 13,2 $ | 7 % | **35,6 %** (+2,3 pt) | **26,7 %** (+1,7 pt) |

Avec un **compte ECN (0,25)** : M5 tombe à 35,9 % / 26,9 % — soit le confort du H1.

### Conclusion opérationnelle
Le levier le plus puissant n'est **pas** d'augmenter le win rate (très difficile),
mais d'**augmenter le R:R** : passer de R:R 2 à R:R 3 réduit l'exigence de ~10 points
de win rate. D'où les réglages recommandés ci-dessous.

### Filtre économique (stratégie uniquement, `btCostGate`, défaut OFF)
Refuse les trades dont le R:R **net de spread** est sous le seuil (`btMinNetR`, 1.5).
Cible pondérée = TP1×%1 + TP2×%2 + TP3×reste. N'ajoute aucun critère de marché :
c'est un filtre de rentabilité, pas de signal. À valider en A/B comme les autres.

### 📊 Tableau de résultats sur le graphique (stratégie)

Panneau affiché directement sur le chart (`btPanelOn`, ON par défaut), lisant
uniquement les compteurs natifs `strategy.*` — aucun impact sur les trades :

Trades clôturés · Gagnants/Perdants · **Win rate** · **Profit net** (+ %) ·
**Profit factor** · **Drawdown max** (+ %) · **Meilleur / pire trade** ·
Gain moyen par trade · **Coût du spread réellement payé** ·
**Profit AVANT spread** · Capital final.

> Les deux dernières lignes sont les plus instructives : l'écart entre
> « Profit net » et « Profit AVANT spread » **chiffre exactement ce que le broker
> te coûte** sur la période testée.

⚠️ Avec les sorties en 3 paliers, TradingView compte **chaque sortie partielle
comme un trade clôturé** : le nombre de trades et le win rate sont donc calculés
sur les partielles. Pour des stats « par trade complet », utiliser le mode
« Sortie unique » le temps de la mesure.

### Mise à jour — spread broker confirmé à **0,95**

| Réglage | Valeur |
|---------|--------|
| `slExecBufSpread` (indicateur + stratégie) | **1.10** (0,95 spread + 0,15 slippage) |
| `slippage` (stratégie) | **95 ticks** |
| `btSpreadEst` (filtre économique + coût affiché) | **0.95** |

Seuils de rentabilité recalculés (SL à 1.2 ATR) :

| UT | spread/risque | R:R 2 | R:R 3 | R:R 4 |
|----|---------------|-------|-------|-------|
| M5 | 29 % | 42,9 % | 32,2 % | **25,8 %** |
| M15 | 14 % | 38,1 % | 28,6 % | **22,9 %** |
| H1 | 7 % | 35,7 % | 26,8 % | **21,4 %** |

Coût par aller-retour : 0,01 lot = 0,95 $ · 0,10 lot = 9,50 $ · 1 lot = 95 $.

### 🐛 Correctif compilation — `input.*` interdit dans `strategy()`

Les paramètres `initial_capital`, `commission_value` et `slippage` de la déclaration
`strategy()` exigent des valeurs **constantes** : y placer des `input.*` provoque une
erreur de compilation. Ils sont désormais **codés en dur** (10 000 / 0.0 / 95 ticks).

Ce n'est pas une perte : TradingView expose nativement ces trois réglages dans
l'onglet **Propriétés** de la stratégie (⚙️ à côté du nom sur le graphique), qui prime
sur les valeurs du code. Capital, commission et slippage restent donc modifiables.

---

## 🧹 Graphique épuré (`cleanChartOn`, défaut OFF)

Interrupteur maître dans le groupe ⓪ qui masque **27 couches d'affichage** d'un coup
(sessions colorées, fond de tendance, zones prédictives/anticipation, labels de
structure HH/LH/BOS/CHoCH, Wyckoff, breakers, imbalances, EQH/EQL, PDH/PDL/PWH/PWL,
raisons détaillées, panneaux secondaires). Ne laisse que : bougies, flèches BUY/SELL,
lignes Entry/SL/TP et panneau principal.

**Aucun impact sur les signaux, le score ou les niveaux** — chaque couche est
simplement `input AND not cleanChartOn`. Les toggles individuels restent utilisables.

### Pourquoi le graphique paraissait « décalé »
Les objets tracés loin du prix (niveaux hebdo/journaliers, zones prédictives à
plusieurs centaines de points) **étirent l'échelle de prix** : TradingView compresse
alors les bougies dans une bande étroite, et tout le reste s'entasse en bas. Les labels
sont bien à leur prix — c'est l'échelle qui est écrasée.

Deux correctifs : `cleanChartOn = ON`, et côté TradingView, clic droit sur l'échelle
des prix → **« Mise à l'échelle du graphique des prix uniquement »**, qui fait ignorer
les objets d'indicateur lors du calcul de l'échelle.

## 🐛 Correctif — taille du tick sur TVC:GOLD

TVC:GOLD cote avec **3 décimales** (4041,180) → 1 tick = **0.001**, pas 0.01.
Le slippage passe donc de 95 à **950 ticks** pour représenter 0,95 $ de spread.

> ⚠️ Vérifier sur le symbole réellement utilisé : si ton flux cote 2 décimales
> (4041,18), il faut 95. Le réglage est modifiable dans l'onglet **Propriétés**.

---

## 🎯 Mode PRO — évolution premium (`proMode`, défaut ON)

Aucun module supprimé, aucune logique recréée : l'indicateur implémentait **déjà**
toute la philosophie demandée (biais, Premium/Discount, liquidité, sweep→CHoCH/BOS,
FVG/OB, Fibonacci, risque). Le travail a porté sur la **hiérarchie visuelle** et
3 ajouts ciblés.

### Ce que le mode PRO affiche (liste blanche)
ATH · Premium/Discount · Buy/Sell Limit (zones prédictives) · Sweeps de liquidité ·
CHoCH/BOS · FVG **ou** Order Block (selon `ezMode`) · Fibonacci · EMA/VWAP.

### Ce qu'il masque (13 couches, purement décoratives)
Sessions colorées · fond de tendance · labels HH/HL/LH/LL · historique BOS/CHoCH ·
Wyckoff (range + figures + WY+) · Breakers · Imbalances · labels FAKE? ·
raisons détaillées · zones Module 7 · zones d'anticipation Module 11 · fiches
détaillées des zones · panneau MTF.

> Chaque couche reste pilotable individuellement. `proMode = OFF` restaure l'affichage complet.

### Ajouts (tous optionnels)

| Ajout | Input | Défaut | Impact signaux |
|-------|-------|--------|----------------|
| **ATH** (plus haut historique chargé) | `athShow` | ON | Aucun (affichage) |
| **Fibonacci visible** (0.5/0.618/**0.705 OTE**/0.786) | `fibDraw` | ON | Aucun (le moteur interne était déjà là, il était juste invisible) |
| **Mode de zone d'entrée** | `ezMode` | « FVG + Order Block » | Défaut = comportement d'origine exact ; « FVG seul » / « OB seul » = plus sélectif |
| **R:R personnalisé** | `rrCustomOn` | OFF | Remplace les cibles du TP Engine par des multiples fixes du risque |

`ezMode` pilote à la fois **ce qui est dessiné** et **ce qui valide une entrée**
(`gateBuyZone` / `gateSellZone`), conformément à la philosophie demandée.

---

## 🧼 `xauusd_smc_PRO.pine` — reconstruction du moteur de décision

Fichier **nouveau et autonome** (803 lignes contre 2 785). Le cerveau a été
reconstruit uniquement autour des 10 briques demandées. Les anciens modules ne sont
pas masqués : **ils n'existent plus dans le code**.

### Supprimés du moteur (vérifié : zéro occurrence hors commentaires)
Wyckoff · Accumulation/Distribution · RSI/Stochastique · DXY · rendements 10Y-2Y ·
filtre news · sessions & kill zones · filtre volume · Breakers · Imbalances ·
filtre ADX · avertissement d'entrée tardive · zones potentielles (module 7) ·
zones d'anticipation (module 11) · panneau multi-timeframe · labels HH/HL/LH/LL.

### Le moteur restant
`Biais → Premium/Discount → Liquidité → Sweep → CHoCH/BOS → FVG/OB → Entrée → Risque`

**Barème rééquilibré sur 100** (l'ancien tombait à 70 max une fois les modules
retirés, ce qui aurait rendu le seuil de 80 inatteignable) :

| Composant | Points |
|-----------|-------:|
| Liquidité (sweep 12 + cassure adossée 13) | 25 |
| Structure BOS/CHoCH (18 + alignement 7) | 25 |
| OB / FVG (une zone 15, les deux 20) | 20 |
| Biais HTF + EMA (8 + 7) | 15 |
| Premium / Discount | 10 |
| VWAP | 5 |
| **Total** | **100** |
| Bonus Fibonacci (confluence uniquement) | +0 à 10, plafonné à 100 |

**2 règles éliminatoires conservées** : aucun signal sans sweep récent, aucun signal
sans cassure structurelle récente. Plus le filtre de biais et le filtre
Premium/Discount, tous deux actifs par défaut.

### Identité visuelle préservée
Mêmes couleurs (teal FVG, bleu/violet OB, aqua/fuchsia sweeps, lime/rouge BOS,
jaune/orange CHoCH), mêmes styles de labels, même palette de panneau (ardoise + or),
même format d'alerte, mêmes lignes Entry/SL/TP.

### Gestion du risque
SL structurel anti-chasse borné [1.2 ; 2.8] ATR, **coût du spread (0,95) intégré au
placement du stop**, entrée de précision sur bord d'OB / milieu de FVG, TP en
multiples R configurables (1.5 / 3 / 5).

### 🧪 `xauusd_smc_PRO_STRATEGY.pine` — backtest de la version PRO

Copie **strictement identique** de `xauusd_smc_PRO.pine` (diff du corps = ligne 2
seule), convertie en `strategy()`. Le moteur d'ordres ajouté ne fait que **lire**
`buySignal` / `sellSignal` / `tmEntry` / `tmSL` / `tmT1-T3`.

| Réglage | Défaut | Note |
|---------|--------|------|
| Capital / commission / slippage | 10 000 / 0 % / **950 ticks** | Codés en dur (Pine exige des const) — surchargeables dans l'onglet **Propriétés** |
| Type d'entrée | Marché | « Limite » = plus fidèle mais moins de trades |
| Sorties | 3 paliers | **TP1 à 20 %** (et non 40) : sortir gros à TP1 écrase le R:R, fatal avec un spread large |
| Taille | Risque 1 % du capital | Calculée sur la distance du stop |

Le tableau de résultats reprend le coût du spread depuis l'input `spreadCost` (0,95)
de la stratégie : **« Profit net » vs « Profit AVANT spread »** chiffre exactement ce
que le broker coûte sur la période.

---

## ➕ Ajouts à la version PRO (cycle AMD + zones anticipées)

### 1. Cycle de marché — Accumulation → Manipulation → Distribution
Phase **dérivée** des états déjà calculés (aucun moteur séparé, aucun nouveau calcul) :

| Phase | Condition |
|-------|-----------|
| **ACCUMULATION** | aucune cassure depuis N barres ET prix contenu dans le range des swings |
| **MANIPULATION** | sweep qualifié récent (la liquidité vient d'être prise) |
| **DISTRIBUTION ↑/↓** | cassure de structure adossée à ce sweep (le mouvement se livre) |

C'est le pipeline du moteur rendu lisible. Affiché en label sur le graphique + ligne
« Cycle » dans le panneau. **Display-only : ne filtre aucun signal** (la logique
sweep→cassure était déjà le cœur du moteur).

> Ce n'est pas le module Wyckoff retiré : celui-ci classait des phases via un moteur
> dédié (range box, Spring/Upthrust/SOS/SOW, 15 pts de score). Ici, rien n'est calculé
> en plus — la phase est une lecture de `barsSinceBreak`, `barsSinceSweep` et `backed`.

### 2. Zones anticipées Buy Limit / Sell Limit — moteur de précision
Chaque zone candidate (OB et/ou FVG du bon côté du prix) est **notée /100** :

| Facteur | Points |
|---------|-------:|
| Premium/Discount favorable | 20 |
| Recouvre la bande OTE Fibonacci (0.618-0.786) | 25 |
| Type : OB+FVG superposés 20 · OB 15 · FVG 12 | 12-20 |
| Liquidité à prendre au-delà (cible du sweep) | 15 |
| Biais HTF aligné | 20 |
| Structure du graphique alignée | 10 |

Seules les zones **≥ `zoneMinScore` (70 par défaut)** sont affichées → peu de zones,
mais de haute qualité. Note affichée A+ / A / B.

**Resserrage OTE** (`zoneFibClip`, ON) : si la zone croise la bande 0.618-0.786, elle
est réduite à cette **intersection** → le point d'entrée devient un niveau précis au
lieu d'une plage large. C'est ce qui rend les zones réellement exploitables.

Chaque zone affiche son plan complet : Entrée · SL (buffer + spread) · TP1 · TP2 · TP Final.

---

## 🎯 A1 — Mode ALIGNEMENT TOTAL (`saOn`, défaut ON)

Constat de l'utilisateur : **rentable en manuel avec les zones**, mais le déclencheur
automatique tire sur des configurations qu'il ne prendrait pas.

Constat dans le code : l'indicateur **détectait déjà** les entrées tardives
(`lwLateBuy` / `lwLateSell`) mais ne s'en servait que pour afficher un avertissement —
le signal partait quand même. Le bloc de calcul a été **remonté avant le moteur de
signal** (il était défini après) pour pouvoir servir de filtre.

### Les 6 exigences (chacune désactivable seule)

| Sous-toggle | Exige |
|-------------|-------|
| `saUseLate` | Aucune entrée tardive (sur-extension ATR / premium-discount profond) |
| `saUseBias` | Biais HTF **et** structure du graphique alignés |
| `saUseChop` | Marché directionnel (ADX ≥ seuil) — plus de signaux dans le bruit |
| `saUsePd` | BUY en discount / SELL en premium |
| `saUseZone` | Prix en interaction avec un Order Block ou un FVG |
| `saUseSweep` | Cassure adossée à un sweep de liquidité |

`saOn = OFF` restaure exactement le comportement précédent. Chaque sous-exigence peut
être relâchée individuellement si le backtest montre qu'elle coûte trop de trades.

> ⚠️ Attendu : **forte baisse du nombre de signaux**. C'est l'objectif — ne garder que
> les configurations qu'un trader discrétionnaire prendrait réellement. À mesurer :
> le profit factor doit monter même si le nombre de trades s'effondre.

---

## 🎯 P1 — Précision des zones institutionnelles (défaut ON)

Le maillon le plus faible de l'indicateur : l'**Order Block** était pris
**mèche à mèche** (`high[i]` / `low[i]`), sans vérifier qu'un vrai displacement
suivait, et l'entrée se faisait au bord de cette zone large.

| Raffinement | Toggle | Effet |
|-------------|--------|-------|
| **Zone = corps de la bougie** | `obBodyOnly` | `open`-`close` au lieu de `high`-`low` → zone typiquement 2 à 3× plus étroite, centrée sur le vrai niveau institutionnel |
| **Displacement exigé** | `obNeedDisp` + `obDispAtr` (1.0) | L'OB n'est retenu que si le prix a parcouru ≥ 1 ATR depuis lui. Élimine les OB mous qui ne tiennent pas |
| **Entrée au Consequent Encroachment** | `entryCE` | Entrée au **50 % de la zone** (référence ICT) au lieu du bord proximal → meilleur prix, stop plus serré, R:R mécaniquement supérieur |

Le FVG utilisait déjà son milieu comme entrée : il était déjà au CE, donc précis.

> Effet attendu : moins d'Order Blocks retenus (ceux sans displacement disparaissent),
> et ceux qui restent sont beaucoup plus fins. À mesurer : le R:R réalisé doit monter.

---

## ⚖️ A1 corrigé — quorum au lieu du « tout ou rien »

**Problème constaté par l'utilisateur : 100 % de réussite, mais ~6 trades par an.**
Le mode A1 exigeait les 6 critères SIMULTANÉMENT, en plus des filtres déjà présents
(biais EMA, biais HTF, Wyckoff, volume, zone, sweep éliminatoire). Le sur-filtrage
rendait l'échantillon inutilisable — et 100 % sur 6 trades n'a aucune valeur
statistique (il faut ~30 trades minimum pour conclure).

### Nouveau fonctionnement
`saMinCount` (défaut **4**) = nombre de critères devant être satisfaits parmi ceux
activés. Réglage progressif :

| Valeur | Effet attendu |
|--------|---------------|
| 6 | ultra strict — quasi aucun trade (l'ancien comportement) |
| **4** | **équilibré (défaut)** |
| 3 | permissif — beaucoup plus de signaux |
| 1-2 | proche du comportement d'origine |

Le label du signal affiche désormais **`X/Y crit.`** : combien de critères étaient
réunis. Utile pour calibrer — si les gagnants sont presque tous à 5/6, monter le
seuil ; s'ils sont à 3/6, le descendre.

### Si le nombre de trades reste trop faible
Les filtres de base s'empilent avec A1. Leviers suivants, dans l'ordre :
1. `saMinCount` → 3
2. `wyUseFilter` → OFF (Wyckoff bloque déjà le contre-cycle)
3. `pfUseVolFilter` → OFF (tick-volume peu fiable sur l'or)
4. `deScoreMin` → 75

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
| Compte | Capital de départ | 10 000 |
| Compte | Commission (% par ordre) | 0.0 |
| Compte | Slippage (ticks) | 0 |
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

## 💱 Calibrage broker réel — FXCess (spread mesuré 0,90 $ sur XAUUSD)

Valeurs pré-réglées **par défaut** dans `xauusd_smc_working.pine` et
`xauusd_smc_STRATEGY.pine` pour ne rien avoir à configurer.

| Réglage | Avant | Après | Pourquoi |
|---------|-------|-------|----------|
| `slExecBufSpread` | 0.0 | **1.00** | Spread réel 0,90 + marge slippage → le SL n'est jamais placé plus près que le coût d'exécution |
| `slMinAtr` | 0.5 | **1.2** | Un SL de 0,5 ATR (~1,4 $ en M5) est balayé par 0,90 de spread. 1.2 ATR ramène le spread sous ~15 % du risque en M15 |
| `slippage` (stratégie) | 0 | **90 ticks** | 0,90 $ = 90 ticks (tick 0,01). Modélisation prudente : spread + slippage |

> Le site FXCess affiche 0,42 (vitrine, marché calme) ; le **réel mesuré est 0,90**.
> C'est la valeur retenue. Tous ces réglages restent des **inputs** modifiables :
> remettre 0.0 / 0.5 / 0 restaure l'ancien comportement.

### ⚠️ Conséquence majeure — coût du spread = spread ÷ distance du SL

| UT | ATR typique | SL à 1.2 ATR | Poids du spread 0,90 |
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

Avec **S = 0,90** (FXCess Classic) et un SL à 1.2 ATR :

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

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
| P1 | Nettoyage code mort + security redondants | — | — | Non | Nul | à venir |

Statut actuel : **B1, B2, B3, S1 implémentés.** Tous à leur valeur baseline
(`fixBreakOn=false`, `fixSweepGateOn=false`, `fixTpSnapOn=false`,
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

## P1 — Nettoyage (DOCUMENTÉ, non appliqué : à faire dans TradingView avec compilateur)

Code mort confirmé (variables **write-only**, jamais lues → suppression sûre, gain
de lisibilité/perf marginal). Retirer dans TradingView puis re-compiler :

| Variable | Où | Action |
|----------|----|--------|
| `barsSinceLiqSweepLow` / `barsSinceLiqSweepHigh` | section LIQUIDITY SWEEPS | déclaration + `+= 1` + `:= 0` jamais lus → supprimer les 3 lignes de chaque |
| `msSwingTrend` | fin Module 1 (swings) | ligne d'assignation jamais réutilisée → supprimer |
| `oscVal` | Momentum Oscillator | assigné, jamais lu (l'oscillateur affiché utilise `rsiVal`/`stochK`) → supprimer |
| `stochD` | Momentum Oscillator | `ta.sma(stochK, oscSmoothD)` jamais lu → supprimer |

Redondance `request.security` (perf) : sur un chart M5, `msTfExec="5"` interroge le
TF courant (redondant + déclenche l'avertissement `f_msTfWarn`). D1 est demandé 2×
(Module 1 contexte via `msTfContext` et Module 10 `pzoD1C`) avec des EMA
différentes. À factoriser prudemment, **après** avoir vérifié la compilation.

---

## Optionnel / à valider avant de coder (items mineurs de l'audit)

| ID | Sujet | Décision |
|----|-------|----------|
| B1b | `f_msStructure()` (MTF) a le MÊME bug de crossover que B1, et alimente le score via `msCtxTrend`. | À ajouter en toggle séparé (`fixBreakMtfOn`, défaut OFF) car il modifie le module de score — à faire isolément et backtester. |
| B4 | Faux cross `wyCrossUpMid`/`wyCrossDnMid` au démarrage d'un range (niveau `wyMid` passe de na à une valeur). | Impact faible ; guard possible si le backtest montre des figures Wyckoff parasites. |
| B5 | `smcRangeTop = math.max(swingHighVal, swingLowVal)` sémantiquement flou en fort trend. | Garde défensive, impact très faible ; laisser tel quel sauf anomalie constatée. |

(Le tableau du haut est complété au fur et à mesure.)

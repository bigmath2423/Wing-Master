# Modèle de résultats de backtest — XAUUSD SMC

But : comparer chaque amélioration à la **baseline** de façon rigoureuse et reproductible,
et ne garder que ce qui améliore ou reste neutre. Une ligne = une configuration testée.

> ⚠️ C'est un **indicateur** (pas une stratégie) → pas de rapport auto. Deux options :
> - **Manuel (recommandé pour commencer)** : TradingView → *Bar Replay*, avancer barre par
>   barre, journaliser chaque signal et son issue (voir « Comment mesurer » plus bas).
> - **Automatisé** : je peux fournir un wrapper `strategy()` (entrées/SL/TP identiques) pour
>   obtenir le rapport TradingView (winrate, profit factor, drawdown) automatiquement. Demande-le.

---

## Cadre de test (à figer avant de commencer)

| Élément | Valeur utilisée |
|---------|-----------------|
| Symbole | XAUUSD (préciser le broker/flux : ________) |
| Unités de temps | M5 et M15 |
| Période testée | du __________ au __________ |
| Nb de barres / jours | __________ |
| Conditions couvertes | ☐ tendance ☐ range ☐ forte volat. ☐ faible volat. ☐ news |
| Spread moyen broker | ________ (ex : 0.20) |
| Slippage supposé | ________ |
| Définition d'un « gain » | TP1 touché AVANT le SL (à garder identique partout) |
| Capital / risque par trade | ________ (ex : 1 % fixe) |

> **Règle d'or A/B** : ne change QU'UNE chose entre deux lignes. Même période, même symbole,
> même UT. Sinon la comparaison n'a aucune valeur.

---

## Comment mesurer chaque métrique (relevé manuel)

- **Nb signaux** : compter les flèches BUY + SELL sur la période.
- **Nb A+ (alerte)** : ceux affichés « · A+ » (score ≥ seuil A+).
- **Gagnants** : signal dont le prix atteint **TP1** avant de toucher le **SL** (lignes tracées).
- **Winrate** = Gagnants / Nb signaux × 100.
- **R réalisé moyen** : pour chaque trade, +1R si TP1, +2R/+3R si TP2/TP Final atteints (choisir
  UNE règle de sortie et la garder : ex. « sortie 100 % au TP1 » = +1R/gagnant, −1R/perdant).
- **Expectancy (R/trade)** = (Winrate × R moyen gagnant) − ((1−Winrate) × 1R).
- **Drawdown max (R)** : plus longue série de pertes cumulées en R.
- **Profit factor** = somme des R gagnés / somme des R perdus (>1 = profitable).

---

## Bloc 1 — BASELINE (référence)

Tous les toggles ⓪ à leur valeur baseline : `fixBreakOn=OFF`, `fixSweepGateOn=OFF`,
`fixTpSnapOn=OFF`, `scoreRealistOn=OFF`, `fixBreakMtfOn=OFF`, `sigConfirmOn=OFF`.
(= comportement de `xauusd_smc_v14_baseline.pine`.)

| UT | Nb sig. | Nb A+ | Gagnants | Winrate % | R moyen | Expectancy (R) | DD max (R) | Profit factor | Notes |
|----|--------:|------:|---------:|----------:|--------:|---------------:|-----------:|--------------:|-------|
| M5 |         |       |          |           |         |                |            |               |       |
| M15|         |       |          |           |         |                |            |               |       |

---

## Bloc 2 — A/B PAR AMÉLIORATION (un seul toggle changé vs baseline)

Ordre suggéré : B2 → B1 → B1b → S1 → B3 → C1. Reporter le **Δ** (delta) vs baseline.

### B1 · `fixBreakOn = ON` (anti faux BOS/CHoCH)

| UT | Nb sig. | Winrate % | Expectancy (R) | DD max (R) | Profit factor | Δ vs baseline | Verdict (garder/jeter) |
|----|--------:|----------:|---------------:|-----------:|--------------:|---------------|------------------------|
| M5 |         |           |                |            |               |               |                        |
| M15|         |           |                |            |               |               |                        |

### B2 · `fixSweepGateOn = ON` (détection sweep indépendante de l'affichage)

| UT | Nb sig. | Winrate % | Expectancy (R) | DD max (R) | Profit factor | Δ vs baseline | Verdict |
|----|--------:|----------:|---------------:|-----------:|--------------:|---------------|---------|
| M5 |         |           |                |            |               |               |         |
| M15|         |           |                |            |               |               |         |

### B1b · `fixBreakMtfOn = ON` (anti faux break MTF)

| UT | Nb sig. | Winrate % | Expectancy (R) | DD max (R) | Profit factor | Δ vs baseline | Verdict |
|----|--------:|----------:|---------------:|-----------:|--------------:|---------------|---------|
| M5 |         |           |                |            |               |               |         |
| M15|         |           |                |            |               |               |         |

### S1 · `scoreRealistOn = ON` (affichage seul — vérifier que les TRADES sont identiques)

| UT | Trades identiques à baseline ? | Confiance affichée plus réaliste ? | Verdict |
|----|-------------------------------|-----------------------------------|---------|
| M5 | ☐ oui ☐ non (si non = bug à signaler) |                                   |         |
| M15|                               |                                   |         |

### B3 · `fixTpSnapOn = ON` (TP sur structure, R:R non conservé)

| UT | Winrate % | R moyen | Expectancy (R) | Profit factor | Δ vs baseline | Verdict |
|----|----------:|--------:|---------------:|--------------:|---------------|---------|
| M5 |           |         |                |               |               |         |
| M15|           |         |                |               |               |         |

### C1 · `sigConfirmOn = ON` (confirmation clôture — doit être NEUTRE en backtest)

| UT | Trades identiques à baseline (historique) ? | Repaint intrabar disparu en réel ? | Verdict |
|----|--------------------------------------------|-----------------------------------|---------|
| M5 | ☐ oui ☐ non (si non = à investiguer)        |                                   |         |
| M15|                                            |                                   |         |

---

## Bloc 3 — GUIDE DE TUNING (inputs existants, un seul changé vs meilleure config retenue)

| Réglage testé | Valeur | UT | Winrate % | Expectancy (R) | Profit factor | Δ | Verdict |
|---------------|--------|----|----------:|---------------:|--------------:|---|---------|
| `chopFilterOn` ON | ON | M5 |           |                |               |   |         |
| `slMinAtr` 0.7 | 0.7 | M5 |           |                |               |   |         |
| `slExecBufSpread` 0.20 | 0.20 | M5 |    |                |               |   |         |
| `pfUseVolFilter` OFF | OFF | M5 |       |                |               |   |         |
| `signalCooldown` 15 | 15 | M5 |         |                |               |   |         |

---

## Bloc 4 — CONFIGURATION FINALE RETENUE

Après avoir validé chaque brique isolément, empiler les gagnantes et re-tester ensemble
(les effets ne sont pas toujours additifs).

| Toggle / réglage | Valeur retenue | Justifié par (ligne ci-dessus) |
|------------------|----------------|--------------------------------|
| B1 `fixBreakOn` |                |                                |
| B2 `fixSweepGateOn` |            |                                |
| B1b `fixBreakMtfOn` |            |                                |
| S1 `scoreRealistOn` |            |                                |
| B3 `fixTpSnapOn` |               |                                |
| C1 `sigConfirmOn` |              |                                |
| (tuning) |                        |                                |

**Résultat config finale vs baseline (M5) :** Winrate ____ → ____ | PF ____ → ____ | Expectancy ____ → ____
**Résultat config finale vs baseline (M15) :** Winrate ____ → ____ | PF ____ → ____ | Expectancy ____ → ____

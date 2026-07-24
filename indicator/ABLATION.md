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
| B2 | `showLiq` ne doit plus gater la détection de sweep | `fixSweepGateOn` | — | Oui (marginal) | Très faible | à venir |
| B3 | Buffer d'exécution défait le snapping TP structurel | `fixTpSnapOn` | — | Non (exécution) | Faible | à venir |
| S1 | Score de confiance recalibré (dégonflage des 40 pts pré-acquis) | `scoreRealistOn` | — | Non (affichage) | Nul | à venir |
| P1 | Nettoyage code mort + security redondants | — | — | Non | Nul | à venir |

(Le tableau est complété au fur et à mesure.)

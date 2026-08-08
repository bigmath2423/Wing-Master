# Tome 4 — Moteur d'analyse macro & Corrélations

> **Statut : ✅ Rédigé & implémenté** · Dépend de : Tomes 0-3.
> Code : `app/analysis/` (regime, yield_curve, correlations) + `app/engine/` (scoring, bias, fusion).

---

## 1. Rôle du moteur
Transformer des données brutes en **lectures de contexte** interprétables :
régime dominant, forme de la courbe, relations entre marchés, scores par actif.
Tout est **descriptif** ; aucun signal directionnel d'exécution n'est produit.

## 2. Détection de régime (`analysis/regime.py`)

Sept régimes reconnus : `risk_off`, `risk_on`, `tightening`, `easing`,
`reflation`, `stagflation_watch`, `neutral`.

**Méthode** : faisceau d'indices pondérés plutôt que règle unique — chaque
observation ajoute des points à un ou plusieurs régimes, le dominant l'emporte.

| Faisceau | Condition | Régime renforcé |
|----------|-----------|-----------------|
| Volatilité | VIX ≥ 25 / ≤ 14 | risk_off / risk_on |
| Géopolitique | indice ≥ 0,65 | risk_off |
| Taux réels (variation) | ≥ +8 bps / ≤ −8 bps | tightening / easing |
| Taux réel (niveau) | ≥ 2,2 % / ≤ 0,5 % | tightening / easing |
| Dollar | ±0,5 % | risk_off+tightening / risk_on |
| Inflation anticipée × croissance | ≥ 2,4 % et activité ↑ / ↓ | reflation / stagflation_watch |
| Courbe inversée | pente ≤ −0,05 | stagflation_watch + risk_off |

**Confiance** = `0,6 × force du régime + 0,4 × marge sur le second`, plafonnée à
92 % (une lecture macro n'est jamais certaine). Le régime `neutral` est plafonné
à 45 % : ne rien détecter n'est pas une conviction.

## 3. Courbe des taux (`analysis/yield_curve.py`)
Qualifie la pente 10 a − 2 a en quatre formes (`inverted`, `flat`, `normal`,
`steep`) avec une interprétation cyclique documentée. L'inversion est présentée
comme un **signal historique de ralentissement à délai très variable** — pas une
prédiction.

## 4. Corrélations (`analysis/correlations.py`)

**Choix méthodologique important** : les corrélations sont calculées sur les
**variations** (rendements), pas sur les niveaux. Deux séries tendancielles
paraissent toujours corrélées en niveau — c'est un artefact trompeur.

Paires suivies par défaut : DXY↔or, taux réels↔or, VIX↔S&P, pétrole↔S&P,
DXY↔BTC, S&P↔BTC, 10 ans↔S&P. Fenêtres : 30 et 90 jours.
Implémentation sans dépendance externe (Pearson maison), renvoyant `None` quand
l'historique est insuffisant plutôt qu'une valeur fragile.

## 5. Scoring par actif (`engine/scoring.py`, inchangé)
Conservé du socle : 5 facteurs bornés (géopolitique, dollar, taux US, inflation,
sentiment) → score signé [−100, +100] par actif, avec décomposition visible.
Les **taux réels** dominent la pondération de l'or, conformément à la littérature.

## 6. Biais & fusion (`engine/bias.py`, `engine/fusion.py`, inchangés)
- Biais = direction (seuil ±15) + confiance (amplitude × cohérence des facteurs).
- Fusion = module un score technique **reçu** de l'indicateur : `reinforced`,
  `warning` ou `standard`. **Ne crée jamais de trade** (Tome 8).

## 7. Nowcasting (proxy implémenté)
`platform_state._growth_momentum()` estime l'élan de croissance à partir du
comportement des actifs cycliques (S&P, cuivre, pétrole), qui réagissent avant
les statistiques officielles. Borné [−1, 1] et documenté comme **proxy grossier**.
Évolution possible : modèle de nowcasting PIB sur séries FRED.

## 8. Tests (`tests/test_analysis.py`)
16 tests couvrent : formes de courbe, chaque régime, bornes de confiance,
Pearson (cas parfaits, données insuffisantes), robustesse aux séries manquantes.

## 9. Definition of Done
- [x] Régimes détectés avec moteurs explicites et confiance bornée.
- [x] Courbe qualifiée et interprétée.
- [x] Corrélations sur variations, multi-fenêtres, dégradation propre.
- [x] Aucune sortie prescriptive.

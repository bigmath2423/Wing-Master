# Validation sur 19 ans — le test qui manquait

Export TradingView de la v12, M15, **11 juin 2007 → 31 juillet 2026**, 1 979 trades.
Treize de ces années (2007-2019) n'ont jamais servi à quoi que ce soit : ni à
construire un module, ni à choisir un paramètre, ni à rejeter un concept.

## Le résultat hors échantillon

| | n | WR | PF | Espérance | Drawdown | t |
|---|---|---|---|---|---|---|
| **2007-2019 — totalement inédit** | **1 248** | 42,3 % | **1,176** | **+0,117 R** | −33,9 R | **+2,36** |
| 2020-2026 — déjà exploré | 731 | 44,2 % | 1,277 | +0,171 R | −25,8 R | +2,86 |
| **Ensemble 19,1 ans** | **1 979** | 43,0 % | **1,212** | **+0,137 R** | −33,9 R | **+3,58** |
| Ancienne référence (6,3 ans) | 783 | 42,9 % | 1,231 | +0,144 R | −26,7 R | +2,53 |

IC95 de l'espérance sur les treize années inédites : **[+0,023 ; +0,213] R**,
P(espérance > 0) = **99,2 %**.

Écart entre période inédite et période explorée : **−0,054 R, p = 0,486**. Un écart
nul est exactement le bon résultat : le système ne se dégrade pas hors des données
qui ont servi à le construire.

## Stabilité par tranches de quatre ans

| Période | n | PF | Espérance |
|---|---|---|---|
| 2007-2011 | 387 | 1,171 | +0,146 R |
| 2011-2015 | 368 | 1,312 | +0,201 R |
| **2015-2019** | 393 | **1,021** | **+0,011 R** |
| 2019-2023 | 391 | 1,230 | +0,140 R |
| 2023-2027 | 440 | 1,317 | +0,183 R |

**5/5 positives.** Mais 2015-2019 est plat sur quatre ans complets — c'est la forme
réelle du système, et il faut le savoir avant de commencer.

## Contrôle du moteur

Sur la fenêtre commune aux deux exports, 597 entrées sont identiques à la seconde
près, et leurs résultats coïncident au quatrième chiffre (écart médian 0,0000 %,
une seule entrée au-delà de 0,01 %). Le moteur de la v12 est donc bien celui de
la v11.

## Une sensibilité à signaler

Sur la même fenêtre 2020-2026, l'ancien run compte 783 trades et le nouveau 693,
avec 76 % d'entrées communes. La cause est la profondeur d'historique : `trend`,
les pivots et le délai entre signaux arrivent à 2020 avec treize ans d'état
derrière eux dans un cas, et repartent de zéro dans l'autre. Ce n'est pas un
défaut de calcul — les trades communs sont identiques — mais cela veut dire que
le nombre exact de trades d'un backtest dépend un peu de sa profondeur. Les
métriques, elles, ne bougent pas : PF 1,212 contre 1,231, espérance +0,137 contre
+0,144.

## Nouvelle référence

**1 979 trades · 19,1 ans · WR 43,0 % · PF 1,212 · espérance +0,137 R ·
drawdown −33,9 R · t = +3,58 · série de pertes max 10.**

C'est la première fois que l'avantage est établi sur un échantillon de cette
taille et confirmé sur des données réellement inédites.

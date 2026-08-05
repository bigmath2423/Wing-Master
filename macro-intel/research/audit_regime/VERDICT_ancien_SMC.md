# Ancien système SMC — verdict sur 6,5 ans

Export TradingView après correction du reliquat d'arrondi : 1 452 tranches,
15/01/2020 → 29/07/2026. Tout est exprimé en R (1 R = risque initial), ce qui
rend la comparaison valide malgré le symbole TVC:GOLD.

## Le système perd de l'argent

| | |
|---|---|
| Tranches | 1 452 |
| Win rate | **53,4 %** |
| Profit Factor | **0,945** |
| Espérance | **−0,029 R** |
| Drawdown | −69,8 R |
| t-stat | −0,89 |
| IC95 de l'espérance | **[−0,093 ; +0,035] R** — P(E > 0) = 18,4 % |

Le win rate élevé vient des prises partielles (265 TP1 + 162 TP2 contre 808 SL) :
il encaisse souvent peu et perd rarement beaucoup. Sorties : 56 % en stop.

Par année : −0,129 · −0,002 · +0,009 · +0,074 · +0,058 · −0,144 · −0,141.
Deux années correctes sur sept, et les deux plus récentes sont les pires.

## Le score /100 — le cœur du système

| Tranche de score | n | PF | Espérance |
|---|---|---|---|
| 85-87 | 521 | 0,952 | −0,024 R |
| 88-90 | 201 | 0,779 | −0,151 R |
| 91-93 | 247 | **0,592** | **−0,246 R** |
| 94-96 | 105 | 1,331 | +0,160 R |
| 97-100 | 378 | 1,286 | +0,119 R |

Le sous-groupe score ≥ 95 est positif : +0,220 R d'écart avec le reste,
t = +3,29, p = 0,0010, 6 années sur 7 meilleures. **Mais il ne passe pas les
deux contrôles qui comptent :**

**Non-monotone.** Un score de qualité doit produire un gradient. Ici la bande
médiane (91-93) est la PIRE de toutes, à −0,246 R. C'est une marche à 94,
pas une échelle de qualité.

**Absent de la première moitié.** 2020-2023 : écart +0,024 R, p = 0,80.
2023-2026 : écart +0,410 R, p < 0,001. L'effet n'existe que dans la moitié
récente — exactement le profil du filtre de régime ADX, qui s'était inversé
dès qu'il rencontrait des données inédites.

Et le mécanisme apparent n'est pas celui qu'on croit : en 2025-2026 le
sous-groupe haut rend −0,020 et +0,742 pendant que le reste s'effondre à
−0,217 et −0,425. Ce sont les scores BAS qui se dégradent, pas les hauts qui
brillent.

## Comparaison directe avec le système actuel

Même période (depuis juin 2020), même unité :

| | n | WR | PF | Espérance | Drawdown | Total |
|---|---|---|---|---|---|---|
| Ancien SMC | 1 401 | 53,0 % | 0,916 | −0,044 R | −69,8 R | −61,3 R |
| **Momentum v11** | 760 | 43,2 % | **1,243** | **+0,149 R** | **−26,7 R** | **+112,9 R** |

Écart d'espérance **+0,192 R, t = +2,93, p = 0,0034**.

C'est le premier écart significatif mesuré entre deux systèmes complets dans
tout ce travail. Le système actuel n'est pas seulement différent de l'ancien :
il est mesurablement meilleur, sur 6,5 ans et 2 161 tranches.

## Rien à récupérer

Les modules de l'ancien système ont été testés un par un au début de ce
travail, puis le score dans son ensemble ici, sur six ans et demi. Ce qui
méritait d'être gardé l'a déjà été : le biais D1/W1, le POC de la veille, le
BOS comme déclencheur, et l'interface. Le reste — sweep de liquidité,
premium/discount, OB, FVG, CHoCH, EQH/EQL, OTE, Wyckoff, et la pondération
en score /100 — ne porte aucune information exploitable.

Le dossier est clos avec une preuve sur 6,5 ans au lieu de 4.

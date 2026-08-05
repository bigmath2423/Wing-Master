# Concepts institutionnels et quantitatifs — cycle 9

Protocole modifié : la **vérification de redondance passe en premier**. Un concept
n'est testé pour sa valeur prédictive que s'il mesure quelque chose d'absent du
système. Cela réduit le nombre d'hypothèses, donc la pénalité de tests multiples,
donc augmente la puissance sur ce qui reste.

## Les douze concepts construits

| Concept | Ce qu'il mesure | Pourquoi il pourrait aider |
|---|---|---|
| **Efficience fractale** (Kaufman, 24 et 96 barres) | \|déplacement net\| / somme des déplacements. 1 = impulsion pure, 0 = bruit | Distingue une tendance d'un aller-retour de même amplitude — ce que l'ATR ne fait pas |
| **Illiquidité d'Amihud** | \|rendement\| / volume | Un prix qui bouge sans volume porte peu d'information ; mesure le coût d'impact |
| **Pression d'ordres** (6 h et 24 h) | position de la clôture dans la barre, pondérée volume | Proxy du déséquilibre acheteur/vendeur sans carnet d'ordres |
| **Ratio de bruit** (Parkinson / close-to-close) | volatilité de range vs volatilité des clôtures | Si le range dépasse largement les clôtures, la barre fait des aller-retours : mouvement bruité |
| **Migration de valeur** (Auction Market Theory) | déplacement du milieu de la Value Area d'un jour à l'autre | Le cœur de la théorie des enchères : c'est le DÉPLACEMENT de la valeur qui informe, pas son niveau |
| **Balance initiale** (Market Profile) | position du prix dans le range de la première heure | Signal d'enchère classique : extension au-delà de l'IB |
| **Structure par terme de la volatilité** | vol 24 h / vol 20 jours | Expansion ou compression en cours, distinct du NIVEAU de volatilité |
| **Coût du mouvement** (brut et normalisé) | volume consommé par unité de déplacement net | Mesure directe de la résistance rencontrée par le prix |

## Étape 1 — Écran de redondance

Corrélation de chaque concept avec les sept informations déjà présentes
(biais D1+W1, tendance H1, côté du VWAP, côté du POC, état de structure, ATR
normalisé, distance à l'EMA200). Seuil d'exclusion : |r| > 0,50.

**Un seul concept éliminé** : la pression d'ordres 24 h, corrélée à +0,698 avec la
distance à l'EMA200 — c'est une moyenne mobile déguisée. Les onze autres mesurent
bien autre chose (|r| max entre 0,02 et 0,50).

## Étape 2 — Valeur prédictive, une hypothèse par concept

Corrélation de Spearman avec le résultat en R sur les 615 trades, plus l'examen
des quintiles (un effet réel doit produire un gradient).

Benjamini-Hochberg, FDR 10 %, sur 10 concepts exploitables :

| Concept | rho | p | Retenu |
|---|---|---|---|
| Coût du mouvement | −0,153 | **0,0001** | oui |
| Coût normalisé | −0,104 | **0,0098** | oui |
| Efficience 96 | +0,081 | 0,0440 | non |
| Structure par terme de la vol | +0,067 | 0,0996 | non |
| Pression d'ordres 6 h | −0,048 | 0,239 | non |
| Illiquidité d'Amihud | +0,026 | 0,513 | non |
| Ratio de bruit | +0,007 | 0,856 | non |
| Efficience 24 | −0,006 | 0,887 | non |
| **Migration de valeur** | −0,005 | 0,903 | non |

La migration de valeur — le concept le plus prometteur sur le papier, celui qui
formalise la théorie des enchères — est **le moins prédictif de tous**.

## Étape 3 — Le confondant temporel

Les deux rescapés ont des **quintiles plats** (+0,163 · +0,207 · +0,197 · +0,211 ·
+0,137), ce qui est incompatible avec une corrélation de rang significative — sauf
s'il existe un confondant.

Il existe, et il est massif :

| | Corrélation avec le TEMPS |
|---|---|
| Coût du mouvement | **rho = −0,290** (p < 0,0001) |
| **Le résultat R lui-même** | **rho = +0,281** (p < 0,0001) |

Le résultat de la stratégie s'améliore avec le temps (2025-2026 sont les bonnes
années). **Toute variable qui dérive dans le temps héritera donc d'une corrélation
avec le résultat, sans aucun lien de cause à effet.**

Corrélation partielle, temps neutralisé : coût du mouvement passe de −0,153 à
**−0,077 (p = 0,055)**, coût normalisé de −0,104 à −0,089. Et l'effet n'est présent
que 2 années sur 5 (2023 et 2024), absent en 2022, nul en 2025, inversé en 2026.

## Étape 4 — Test pratique

Le seul test qui compte : un filtre bâti dessus change-t-il le résultat ?

| Filtre | Gardés | Rejetés | Écart | p |
|---|---|---|---|---|
| Coût du mouvement, 50 % plus bas | PF 1,311 · +0,175 | PF 1,339 · +0,191 | −0,016 R | 0,889 |
| Coût du mouvement, 70 % plus bas | PF 1,354 · +0,198 | PF 1,258 · +0,148 | +0,049 R | 0,688 |
| Coût normalisé, 50 % plus bas | PF 1,391 · +0,216 | PF 1,253 · +0,146 | +0,070 R | 0,538 |
| Coût normalisé, 70 % plus bas | PF 1,329 · +0,185 | PF 1,302 · +0,172 | +0,013 R | 0,915 |

**Aucun.** La corrélation de rang existe dans les queues de distribution mais ne
déplace pas la moyenne — et c'est la moyenne qui fait l'espérance.

## Verdict : aucun concept retenu

12 construits · 1 redondant · 11 testés · 2 survivants à la correction ·
2 expliqués par le temps · 0 exploitable.

## Ce que ce cycle apporte quand même : un contrôle manquant

Le résultat de la stratégie est corrélé au temps à rho = +0,281. **Ce contrôle
aurait dû être en place depuis le début.** Appliqué rétroactivement au filtre de
régime ADX qui avait produit un faux positif :

| | |
|---|---|
| ADX vs temps | rho = −0,092 (p = 0,023) |
| ADX vs résultat | rho = −0,071 |
| **ADX vs résultat, temps neutralisé** | **rho = −0,047 (p = 0,241)** |

L'effet ADX perdait **un tiers de son amplitude** dès qu'on neutralisait le temps —
et cela se voyait avant même de disposer des données 2020-2022.

**La corrélation partielle avec le temps devient un contrôle obligatoire** pour
tout concept futur, au même titre que la monotonie, la sensibilité aux réglages
et la correction de tests multiples.

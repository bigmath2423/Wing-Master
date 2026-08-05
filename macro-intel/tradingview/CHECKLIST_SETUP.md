# Checklist exacte des setups — v13

Extraite du code, pas de la mémoire. Chaque ligne correspond à une condition
réellement présente dans `alignLong` / `alignShort` / `trigLong` / `trigShort`.

## ACHAT — les 6 conditions, toutes obligatoires

| # | Condition | Variable | Effet mesuré |
|---|---|---|---|
| 1 | **Déclencheur** — clôture au-dessus du dernier sommet de structure stable | `bullBos` | +0,224 puis +0,517 — c'est le déclencheur |
| 2 | Tendance de structure haussière | `trend == 1` | **tautologie** avec le BOS : toujours vraie quand testée |
| 3 | Clôture H1 précédente au-dessus de son EMA50 | `htfBull` | +0,016 / +0,096 |
| 4 | Prix au-dessus du VWAP de session | `aboveVwap` | +0,044 / +0,161 |
| 5 | **Clôture D1 > EMA20 ET clôture W1 > EMA10** | `biasBull` | **+0,064 → +0,130 R** — le module qui porte le système |
| 6 | Prix au-dessus du POC de la veille | `abovePoc` | gain surtout sur le drawdown : −18,8 → −16,0 R |

Plus deux gardes techniques : ATR valide et non nul, et **au moins 10 bougies**
depuis le dernier achat (`cooldown`).

Le signal n'est émis qu'à la **clôture confirmée** de la bougie
(`barstate.isconfirmed`) — c'est ce qui garantit l'absence de repaint.

## VENTE — strictement symétrique

Les six mêmes conditions inversées : `bearBos`, `trend == -1`, `htfBear`,
`belowVwap`, `biasBear`, `belowPoc`.

## Ce qui n'entre PAS dans la décision

Ces modules sont **affichés** mais ne conditionnent rien. Mesure sur 6,3 ans :

| Module | Effet apprentissage / validation |
|---|---|
| Order Blocks | −0,188 / **+0,378** — le signe s'inverse |
| Fair Value Gaps | +0,134 / **−0,028** — le signe s'inverse |
| CHoCH | −0,187 / +0,080 — instable |
| Sweep de liquidité | **−0,087 / −0,178** — sélectionne les mauvais trades |
| Premium / Discount | effet négatif |
| Value Area, PDH/PDL, S/R | non significatifs |
| Zones hebdomadaires, score de Confluence | planification seule |
| Panneau multi-timeframe, régime de contexte | affichage seul |

Il n'y a **aucun score minimum** à atteindre. La mesure a montré que pondérer
ces éléments en un score /100 n'apporte rien par rapport à leur simple
conjonction : quand les six sont alignés, tout seuil utile est dépassé
mécaniquement. Le score affiché dans le commentaire des entrées (`BUY 66 A37`)
est informatif — le nombre après `A` est le percentile ADX, conservé pour
d'éventuelles mesures ultérieures.

## Conditions qui invalident un trade

Une seule des six conditions manquante suffit. En pratique, la cause la plus
fréquente d'absence de signal est le **biais divergent** : quand D1 et W1 ne
pointent pas dans le même sens, `biasBull` et `biasBear` sont tous deux faux
et aucun signal ne peut sortir, dans aucun sens.

## SORTIE — identique dans les deux sens

| | |
|---|---|
| Stop initial | **2,5 × ATR(14)** depuis le prix d'entrée |
| Sortie | **trailing** armé à **+1,5 R**, distance suivie **0,3 R** |
| Prise partielle | **aucune** — mesurée à 0,061 R de coût par trade contre 0,028 |
| Take profit fixe | **aucun** par défaut (option `TP fixe` disponible, mesurée) |
| Taille | risque de **1 %** du capital, plafonné à **5× le capital en notionnel** |

Le plafond de levier n'est pas décoratif : sans lui, sur un symbole indiciel
non négociable, la taille calculée atteignait 20× le capital et une perte
coûtait 2,72 % au lieu de 1 %.

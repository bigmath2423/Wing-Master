# Grille de notation des setups — A+ / A / B / INVALID

Document de formalisation. **Aucun code n'a été modifié.** Chaque règle ci-dessous
est reliée à une variable qui existe déjà dans `xauusd_momentum_v13.pine` /
`xauusd_momentum_v13_indicateur.pine`, pour que ce soit codable directement le
jour où tu valides cette grille.

## Principe : deux familles, jamais mélangées

Le système ne connaît que deux statuts pour une règle, et ce document les
sépare partout :

- **DECIDE** — la règle gate réellement `buySignal`/`sellSignal` aujourd'hui,
  ou détermine la taille/le stop du trade. Le grade A+/A/B/INVALID est
  construit **uniquement** avec ces règles-là.
- **CONTEXTE** — la règle est affichée (panneau, zones, tags) mais ne bloque
  et ne débloque rien. Certaines ont même une preuve mesurée **négative**
  (sweep de liquidité : -0.087 R apprentissage / -0.178 R validation).

Mélanger les deux dans le grade referait exactement l'erreur qu'on a déjà
écartée sur ~50 concepts en 10 cycles : donner à un élément descriptif
l'autorité visuelle d'un élément qui décide. Les éléments CONTEXTE apparaissent
quand même plus bas, en tags à côté du grade — jamais dans son calcul.

## Découverte importante : `trend` n'est pas un filtre indépendant — mais reste compté

`trend` (la structure) est mis à jour PAR le BOS lui-même :

```
if bullBos
    trend := 1
if bearBos
    trend := -1
```

Sur la bougie où `bullBos` se déclenche, `trend == 1` est donc **déjà vrai**
avant même que `alignLong` ne soit évalué — en mode BOS (le réglage par
défaut), ce n'est pas une confirmation indépendante, c'est une tautologie du
déclencheur. Mais `trigMode` peut aussi valoir "Cassure Donchian" : dans ce
cas le déclencheur (`donUp`/`donDn`) est totalement indépendant de `trend`,
qui redevient un vrai filtre à part entière — `alignLong` l'exige de toute
façon, quel que soit le déclencheur choisi.

Pour que le grade codé reste identique à `buySignal`/`sellSignal` **quel que
soit le réglage**, `trend` est donc compté comme un 5ᵉ filtre à part entière
(voir grille ci-dessous, désormais sur 5 et non 4). En mode BOS par défaut,
il ne coûte jamais rien : il est automatiquement acquis dès que le
déclencheur s'active, donc les seuils A+/A/B restent gouvernés dans les
faits par les 4 mêmes filtres qu'avant (HTF, VWAP, Biais, POC) — seule la
graduation numérique change (5/5, 4/5, 3/5 au lieu de 4/4, 3/4, 2/4).

## Les 15 dimensions demandées, une par une

| # | Dimension | Définition codable (variable réelle) | Statut | Preuve mesurée |
|---|---|---|---|---|
| 1 | Contexte de tendance | `htfBull`/`htfBear` = EMA50 de l'unité supérieure vs clôture ; `biasBull`/`biasBear` = D1 EMA20 + W1 EMA10 (ou ruban 5/20/50) | **DECIDE** (2 filtres sur les 4) | Biais D1+W1 : espérance +0.064 → +0.130 R à lui seul (poids double dans `ctxScore`) |
| 2 | Liquidité ciblée | `eqhL[]`/`eqlL[]` = poches EQH/EQL (deux pivots quasi égaux, tolérance `liqTolAtr`) | CONTEXTE | Affichage + composante du score de confluence hebdo (20 pts) |
| 3 | Sweep | Poche prise (`high > eqhL` / `low < eqlL`) puis clôture qui rejette | CONTEXTE | **Mesuré négatif** : -0.087 R (apprentissage) / -0.178 R (validation) — inverse le signe. Jamais un filtre. |
| 4 | CHoCH | `bullChoch = bullBos and trend[1] == -1` — un BOS qui inverse la tendance précédente | CONTEXTE | Sous-ensemble étiqueté du BOS, jamais vérifié seul |
| 5 | BOS | `bullBos`/`bearBos` = franchissement du dernier swing (`ta.pivothigh/low`, longueur `swingLen`) | **DECIDE** — c'est le déclencheur par défaut (`trigMode = "BOS (actuel)"`) | Écart vs Donchian : +0.011 R, p = 0.89 (équivalents) |
| 6 | Displacement | `bullImb = (close-open) >= 1.5×ATR` | CONTEXTE (gate de création OB/FVG) — **rejeté comme déclencheur seul** (`useImb`, défaut off) | PF 1.13 → 1.08 si activé seul : dégrade |
| 7 | FVG | `fvBT/fvBB` = écart > `fvgMinAtr` (0.35×ATR) sur bougie à corps ≥ `fvgDispAtr` (1.0×ATR) | CONTEXTE | Composante du score de confluence hebdo (15 pts, partagée avec OB) |
| 8 | OB | Dernière bougie opposée avant un déplacement ≥ `obDispAtr` (1.2×ATR) suivi d'un BOS | CONTEXTE | Idem — jamais isolé |
| 9 | Zone d'entrée | **N'existe pas** en tant que telle : le système entre au marché (`close`) sur la bougie de confirmation du déclencheur | — | Les zones Buy/Sell hebdomadaires sont un plan affiché, "ne génèrent aucun trade" |
| 10 | SL | `slAtr × atrV` = 2.5×ATR(14) depuis l'entrée | **DECIDE** | 1.5×ATR rendait le système négatif sur 2 sous-périodes / 4 |
| 11 | TP | Mode "Trailing (valide)" par défaut : armé à 1.5R, suivi à 0.3R. Mode "TP fixe" optionnel à 0.5R | **DECIDE** | Trailing : PF 1.231, espérance +0.144 R. TP fixe : WR 66.9 % mais espérance +0.053 R (moitié moindre) — measuré sur 783 trades dont 200 hors échantillon |
| 12 | RR minimum | **N'existe pas.** `rr` est calculé pour affichage seul, ne bloque et n'ajuste rien | — | Aucune mesure : ce serait une règle nouvelle, non testée |
| 13 | Filtres M5/M15 | `dirM5`/`dirM15` = votes EMA50 vs EMA200 sur ces unités, affichés dans `mtfAgree/mtfTot` | CONTEXTE | Étape 1 (partition des trades par état M5) : aucun gain significatif trouvé |
| 14 | EMA 50/200 | EMA50 de l'unité supérieure → **DECIDE** (dimension 1). EMA50/200 du panneau MTF → CONTEXTE | Mixte, voir ci-dessus | — |
| 15 | ATR | `ta.atr(14)` → dimensionne le SL (**DECIDE**, sans lui la taille est nulle et le trade est bloqué) ; sert aussi de seuil pour OB/FVG/liquidité (CONTEXTE) | Mixte | — |
| — | Conditions d'exclusion | Voir section dédiée ci-dessous | **EXCLUSION** | — |

## Conditions d'exclusion réelles (les seules qui bloquent un signal)

1. **Cooldown** — `bar_index - lastLong > 10` (ou `lastShort`) : pas deux signaux du même sens en moins de 10 bougies.
2. **ATR invalide** — `atrV` non défini ou ≤ 0 : le risque n'est pas calculable, donc pas de trade.
3. **Bougie non confirmée** — `barstate.isconfirmed` : anti-repaint, aucun signal sur une bougie en cours de formation.
4. **Levier notionnel** — plafonné à `maxLev` (5× le capital) : limite la taille, ne bloque pas le signal lui-même.

**Ce qui n'exclut PAS un signal, à l'inverse de ce qu'on pourrait supposer** :
le régime de contexte (`ctxCode`, 5 niveaux Strong Bullish → Strong Bearish)
ne bloque **jamais** `buySignal`/`sellSignal`. Il ne contrôle que l'affichage
des zones institutionnelles. C'est un choix déjà arbitré dans ce projet, pas
un oubli.

## La grille — BUY

| Grade | Déclencheur | Conditions (sur 5, chacune respecte son interrupteur `useX`) | Exclusion | Équivaut à |
|---|---|---|---|---|
| **A+** | `bullBos` (ou `donUp` si Donchian) | 5/5 : `trend==1` + `htfBull` + `aboveVwap` + `biasBull` + `abovePoc` | aucune | `buySignal` — le trade que le système prend réellement (19 ans, 1979 trades, PF 1.212) |
| **A** | présent | 4/5 (un filtre manquant, nommé dans l'affichage) | aucune | Surveillance — **jamais backtestée isolément** |
| **B** | présent | 3/5 | aucune | Spéculatif — risque plus élevé, **jamais mesuré** |
| **INVALID** | absent, OU conditions ≤ 2/5, OU une exclusion active | — | — | Pas d'entrée |

## La grille — SELL (miroir strict)

| Grade | Déclencheur | Conditions (sur 5) | Exclusion | Équivaut à |
|---|---|---|---|---|
| **A+** | `bearBos` (ou `donDn`) | 5/5 : `trend==-1` + `htfBear` + `belowVwap` + `biasBear` + `belowPoc` | aucune | `sellSignal` |
| **A** | présent | 4/5 | aucune | Surveillance |
| **B** | présent | 3/5 | aucune | Spéculatif |
| **INVALID** | absent, OU conditions ≤ 2/5, OU une exclusion active | — | — | Pas d'entrée |

## Statut : codé

Implémenté dans le panneau des deux fichiers (`xauusd_momentum_v13.pine` et
`xauusd_momentum_v13_indicateur.pine`), ligne **Grade**. Affiche le grade, le
sens (BUY/SELL) et, si incomplet, les filtres manquants — par exemple
`A  BUY  (manque POC)`. Aucune ligne de décision n'est touchée : le grade est
un calcul de lecture, recalculé sur `barstate.islast`, qui ne modifie ni
`alignLong`, ni `trigLong`, ni `buySignal`.

## Tags contextuels affichables à côté du grade (jamais dans le calcul)

CHoCH · Sweep · OB · FVG · Displacement · Zone hebdomadaire (score /100,
`wzArmed`) · Accord MTF M5/H4/D1. Tous mesurés comme descriptifs, deux
explicitement négatifs ou dégradants s'ils décident (sweep, displacement
seul). Les afficher informe le trader ; les compter dans le grade mentirait
sur ce qui a été prouvé.

## Ce que ça change si c'est codé

- **A+ ne crée aucun nouveau trade** : c'est une reformulation de `buySignal`/
  `sellSignal` existants, donc zéro impact sur le backtest.
- **A et B sont de nouvelles catégories, jamais testées.** Les coder pour
  affichage seul (comme le panneau actuel) est sans risque. Les coder comme
  déclencheurs de trade — même à taille réduite — exigerait un backtest
  séparé avant adoption, comme pour toute règle nouvelle sur ce projet.

Dis-moi si cette grille te convient telle quelle, ou si tu veux qu'un tag
CONTEXTE précis (CHoCH, sweep, zone hebdo...) soit promu en filtre A/B —
auquel cas je le backteste isolément avant de coder quoi que ce soit.

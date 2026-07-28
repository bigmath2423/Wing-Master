## Chapitre 13 — Le Fair Value Gap (FVG)

### La définition en trois bougies

```schema
             ┌─┐  bougie 3
             │█│
   ▓▓▓▓▓▓▓▓▓▓│ │  ← FVG : zone jamais négociée dans les deux sens
   ┌─┐  ┌───┐│ │
   │█│  │███││ │  bougie 2 : le déplacement
   └─┘  └───┘└─┘
  bougie 1

   FVG haussier : mèche haute de la bougie 1  <  mèche basse de la bougie 3
   FVG baissier : mèche basse de la bougie 1  >  mèche haute de la bougie 3
```

### Pourquoi le prix y revient

Pendant l'expansion, l'exécution a été si rapide qu'une partie des ordres n'a pas
pu être servie à ces prix. Le retour permet de compléter au meilleur prix moyen.
Ce n'est pas une loi physique : c'est une tendance statistique forte, pas une
garantie.

### Les niveaux d'entrée dans le FVG

| Entrée | Position | Compromis |
|---|---|---|
| **Bord haut** (achat) | Première touche | Meilleur ratio, plus d'entrées manquées |
| **Milieu** (*consequent encroachment*) | 50 % du gap | Le meilleur compromis |
| **Bord bas** | Comblement total | Rarement atteint, mais excellent ratio |

Pratique recommandée : entrée limite au **milieu**, avec la moitié de la taille
au bord si l'on veut être sûr d'être servi.

### La hiérarchie des FVG

| Rang | FVG | Fiabilité |
|---|---|---|
| ★★★ | D1 / H4, créé après une prise de liquidité | Très élevée |
| ★★ | H1 / M15, dans le sens du biais HTF | Élevée |
| ★ | M5, dans le sens du biais | Correcte, exécution seulement |
| ✘ | M1, ou contre le biais HTF | À ignorer |

### Le FVG traversé

Un FVG que le prix traverse sans réaction n'est pas une anomalie : c'est une
information. Il signale une force réelle en sens contraire, et il devient un
**IFVG** (chapitre suivant).

::: retenir
- Trois bougies, absence de chevauchement entre la première et la troisième.
- Entrée limite au milieu du gap, stop au-delà de la bougie d'origine.
- Uniquement dans le sens du biais HTF et du bon côté de l'équilibre.
- Un FVG traversé se retourne contre vous : il devient une résistance.
:::

::: erreur
- Trader tous les FVG visibles, dans les deux sens, sur toutes les unités.
- Exiger un comblement à 100 % : souvent seul le milieu est touché.
- Utiliser un FVG en M1 comme signal de biais.
- Placer le stop à l'intérieur du gap.
:::

::: resume
**FVG en une page.** Quand le prix se déplace violemment, il laisse derrière lui
une zone qui n'a été négociée que dans un sens : c'est le déséquilibre. Le
marché tend à y revenir pour compléter les exécutions manquées, ce qui en fait
la meilleure zone d'entrée limite du modèle : point précis, invalidation courte,
ratio élevé. On l'utilise uniquement dans le sens du biais supérieur, du bon
côté de l'équilibre, avec une entrée au milieu du gap et un stop au-delà de la
bougie qui l'a créé. Un FVG traversé sans réaction change de camp.
:::

## Chapitre 14 — L'IFVG (Inverse Fair Value Gap)

### Le principe

Un FVG traversé **en clôture** est invalidé. Les ordres qui l'avaient créé sont
désormais en perte. La zone conserve pourtant son épaisseur d'ordres : elle
devient une zone de réaction dans le sens opposé.

```schema
   FVG baissier ▓▓▓▓
                     ╱ traversée en clôture
                   ╱
                 ╱     ▓▓▓▓ ← la même zone devient support
               ╱          ▲ entrée à l'achat au retest
```

### La règle de validation

| Condition | Obligatoire |
|---|---|
| Traversée **en clôture** (pas en mèche) | Oui |
| Changement de structure préalable ou simultané | Oui |
| Premier retest seulement | Oui |

Un IFVG testé deux fois n'a plus de valeur. Une zone ne se recycle pas
indéfiniment.

### Quand l'IFVG est supérieur à l'Order Block

Dans les retournements rapides, il n'existe souvent pas encore d'Order Block
propre. L'IFVG donne alors une zone d'entrée immédiate, avec une invalidation
très courte — utile après un MSS en unité basse.

::: retenir
- Un FVG traversé en clôture change de polarité.
- Il faut une clôture, pas une simple mèche.
- Premier retest uniquement.
- C'est l'outil du retournement rapide, quand aucun OB n'est disponible.
:::

::: erreur
- Compter une mèche traversante comme une inversion.
- Utiliser un IFVG sans changement de structure.
- Retester la même zone plusieurs fois.
- L'employer contre une tendance HTF puissante.
:::

::: resume
**IFVG en une page.** Un déséquilibre franchi en clôture devient une barrière
dans l'autre sens : ce qui devait repousser le prix l'attire désormais, et
inversement. Le mécanisme est le même que celui du breaker, appliqué à un gap
plutôt qu'à un bloc : les positions prises dans la zone sont en perte, et leur
liquidation alimente le mouvement opposé. On l'utilise au premier retest
seulement, après un changement de structure, avec un stop de l'autre côté de la
zone. C'est l'outil des retournements rapides, quand aucun Order Block propre
n'a encore eu le temps de se former.
:::

## Chapitre 15 — Le BPR (Balanced Price Range)

### Définition

Un BPR est la **zone de recouvrement de deux FVG de sens opposé**. Le prix a
laissé un déséquilibre haussier, puis un déséquilibre baissier au même endroit —
ou l'inverse. La plage commune est une zone d'équilibre retrouvé, particulièrement
réactive.

```schema
   FVG haussier   ▓▓▓▓▓▓▓▓
   FVG baissier      ░░░░░░░░
   BPR               ▓░▓░      ← zone de recouvrement
```

### Pourquoi c'est réactif

Les deux déséquilibres se sont annulés : la zone a été traversée dans les deux
sens en un temps très court, ce qui y concentre des ordres non servis des deux
côtés. Le premier retour y produit fréquemment une réaction nette.

### Utilisation

| Élément | Règle |
|---|---|
| **Entrée** | Limite au bord de la zone commune |
| **Stop** | Au-delà de la zone entière, jamais à l'intérieur |
| **Sens** | Celui du dernier déplacement (celui qui a créé le second FVG) |
| **Validité** | Premier retour uniquement |

### Fréquence

Le BPR est rare et se forme surtout après une news ou une purge violente, quand
le prix fait un aller-retour rapide. Deux à quatre occasions par mois et par
instrument — pas davantage. Si vous en voyez tous les jours, votre marquage est
trop large.

::: retenir
- Deux FVG opposés qui se recouvrent : la zone commune est le BPR.
- Sens du trade = celui du dernier déplacement.
- Stop au-delà de la zone complète.
- Configuration rare : sa rareté fait sa qualité.
:::

::: erreur
- Élargir les zones jusqu'à créer artificiellement un recouvrement.
- L'utiliser dans le sens du premier FVG au lieu du second.
- En voir tous les jours : c'est le signe d'un marquage trop permissif.
- Placer le stop entre les deux FVG.
:::

::: resume
**BPR en une page.** Quand un déséquilibre haussier et un déséquilibre baissier
se superposent, leur zone commune concentre des ordres non exécutés dans les
deux sens. Le premier retour du prix y produit une réaction nette, dans le sens
du dernier déplacement. Configuration rare — deux à quatre fois par mois — mais
d'une précision remarquable, avec une invalidation courte. Elle se forme surtout
après une publication économique ou une purge violente, quand le prix effectue
un aller-retour rapide sur la même plage.
:::

## Chapitre 16 — Le BOS (Break of Structure)

### Définition

Le BOS est la cassure du dernier pivot **dans le sens de la tendance** : il
confirme la continuation.

```schema
   BOS haussier                       Faux BOS (sweep)
        ╱▲ clôture au-dessus              ▲ mèche seule
   ────┼─────────  sommet         ───────┼──────  sommet
      ╱                                  │╲
    ╱   ← déplacement franc              │  ╲ clôture en dessous
```

### Les deux critères de validation

| Critère | Détail |
|---|---|
| **Clôture au-delà** | Une mèche ne suffit pas : elle indique une purge |
| **Déplacement** | Corps large, idéalement un FVG derrière |

Sans déplacement, un BOS techniquement valide reste suspect : la cassure a été
laborieuse, ce qui signale une absence d'intention.

### Comment le trader

On ne trade **jamais** la cassure elle-même. On attend :

1. le retour dans le FVG créé par le mouvement de cassure, ou
2. le retest de l'Order Block à l'origine du déplacement, ou
3. le retest du niveau cassé devenu support (*flip zone*).

Les trois donnent le même trade, avec un stop court et un ratio favorable.

::: retenir
- BOS = continuation, dans le sens de la tendance.
- Il faut une clôture, pas une mèche.
- On entre au retour, jamais sur la cassure.
- Un BOS sans déplacement est une cassure fragile.
:::

::: erreur
- Acheter la bougie de cassure au marché.
- Compter une mèche comme un BOS.
- Placer un stop juste sous le niveau cassé (c'est là que sont tous les autres).
- Multiplier les BOS en M1 jusqu'à en trouver un qui confirme son envie.
:::

::: resume
**BOS en une page.** La cassure d'un sommet en tendance haussière (ou d'un creux
en tendance baissière) confirme que le déséquilibre se poursuit. C'est le signal
de continuation le plus simple du modèle. Deux conditions le valident : une
clôture au-delà du niveau et un déplacement franc, idéalement accompagné d'un
FVG. Le trade ne se prend jamais sur la cassure, qui offre le pire prix et le
stop le plus large, mais sur le retour dans le déséquilibre ou sur le niveau
cassé devenu support.
:::

## Chapitre 17 — Le CHoCH (Change of Character)

### Définition

Le CHoCH est la cassure du dernier pivot **opposé à la tendance** : il signale
un possible retournement.

```schema
   HH        purge de la BSL ▲
        ╱╲       ╱╲   ╱ ╲
      ╱    ╲   ╱    ╲╱   ╲
    ╱   HL   ╲╱               ╲
  ─────●────────────────────────╲──── cassure du HL = CHoCH
                                  ╲▼
```

### La séquence complète du retournement

```schema
   1. Le prix fait un dernier sommet         (tendance haussière)
   2. Il PURGE la liquidité au-dessus        (le carburant)
   3. Il casse le dernier creux avec force   (le CHoCH)
   4. Il revient sur l'OB / le FVG           (l'entrée)
   5. Il part vers la liquidité inférieure   (l'objectif)
```

L'étape 2 est celle que la majorité des traders omet — et c'est celle qui
distingue un vrai retournement d'un simple retracement profond.

### BOS ou CHoCH ? Le tableau qui tranche

| | BOS | CHoCH |
|---|---|---|
| Sens de la cassure | Celui de la tendance | Opposé à la tendance |
| Signification | Continuation | Retournement possible |
| Ce qu'il précède souvent | Une expansion | Une nouvelle structure |
| Précédé d'une purge ? | Parfois | Presque toujours |

::: retenir
- CHoCH = cassure du dernier pivot opposé = retournement possible.
- Presque toujours précédé d'une purge de liquidité.
- Il faut un déplacement : sans lui, c'est une simple correction profonde.
- Un CHoCH en M1 ne retourne pas une tendance journalière.
:::

::: erreur
- Confondre CHoCH et BOS (retournement contre continuation).
- Trader un CHoCH sans purge préalable.
- Prendre un CHoCH d'unité basse pour un changement de tendance de fond.
- Entrer sur la cassure au lieu d'attendre le retour dans la zone.
:::

::: resume
**CHoCH en une page.** C'est le premier signe qu'une tendance change de mains :
le prix casse, avec force, le dernier pivot qui allait dans son sens. Le CHoCH
n'a de valeur que s'il est précédé d'une prise de liquidité — c'est cette purge
qui fournit la contrepartie au nouveau flux — et s'il s'accompagne d'un
déplacement franc laissant un déséquilibre. On n'entre pas sur la cassure : on
attend le retour dans l'Order Block ou le FVG créé par ce déplacement, avec un
stop au-delà de l'extrême purgé.
:::

## Chapitre 18 — Le MSS (Market Structure Shift)

### Ce qui le distingue du CHoCH

Le MSS est un CHoCH **qualifié** : même mécanique, mais avec des exigences
supplémentaires qui en font un signal de changement de biais, et non un simple
signal d'entrée.

| Exigence | CHoCH | MSS |
|---|---|---|
| Cassure d'un pivot opposé | Oui | Oui |
| Déplacement obligatoire | Souhaitable | **Obligatoire** |
| FVG laissé par la cassure | Fréquent | **Obligatoire** |
| Unité de temps | Toutes | H1 / H4 / D1 |
| Conséquence | Entrée possible | **Changement de biais** |

### La séquence

```schema
   purge ▲
        ╱╲
      ╱   ╲        ███ déplacement + FVG
    ╱      HL ─────────────────────  cassure en clôture = MSS
                        ╲▼ nouveau biais : baissier jusqu'au prochain signal
```

### Ce qu'il autorise

Un MSS sur votre unité de biais **change votre journée** : les achats
deviennent interdits, les ventes deviennent les seuls trades autorisés, et vos
zones de premium/discount doivent être redessinées sur le nouveau range.

C'est le seul événement qui justifie de retourner complètement sa lecture en
cours de séance.

::: retenir
- MSS = CHoCH + déplacement + FVG, sur une unité significative.
- Il autorise à changer de biais, pas seulement à prendre un trade.
- Il impose de redessiner le dealing range.
- Sans FVG laissé par la cassure, ce n'est pas un MSS.
:::

::: erreur
- Appeler MSS n'importe quelle cassure de pivot.
- Changer de biais sur un MSS en M1.
- Oublier de redessiner le range après le MSS, ce qui fausse tous les filtres
  suivants.
- Entrer immédiatement au lieu d'attendre le retour dans le FVG.
:::

::: resume
**MSS en une page.** C'est le changement de structure qui compte : cassure d'un
pivot opposé, sur une unité de temps significative, avec un déplacement franc
et un déséquilibre laissé derrière. Il ne donne pas seulement une entrée, il
donne un **nouveau biais** : à partir de là, seuls les trades dans le nouveau
sens sont autorisés, et le dealing range doit être retracé pour recalculer
premium et discount. C'est le seul événement qui justifie de retourner sa
lecture en pleine séance — et c'est pourquoi ses conditions sont strictes.
:::

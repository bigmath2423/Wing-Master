## Chapitre 5 — Price Action

La *price action* est la lecture du marché sans intermédiaire. Tout indicateur
étant une transformation mathématique du passé du prix, il ne peut, par
construction, contenir plus d'information que le prix lui-même.

### Les trois seules lectures nécessaires

| Lecture | Ce qu'on observe | Ce que cela signifie |
|---|---|---|
| **Rejet** | Longue mèche à un niveau | Le prix y est allé chercher des ordres et a été repoussé |
| **Absorption** | Volume élevé, prix immobile | Quelqu'un de gros prend l'autre côté |
| **Déplacement** | Corps larges, mèches courtes, FVG | Une intention agressive s'exprime |

Tout le reste — noms de figures, combinaisons de chandeliers, motifs à trois
bougies — est du vocabulaire. Ces trois lectures suffisent.

### Impulsion contre correction

```schema
   IMPULSION    ███ ███ ███     corps larges, peu de chevauchement, volume ↑
   CORRECTION   ▪▪ ▪ ▪▪ ▪ ▪     corps étroits, chevauchement, volume ↓

   Règle : on entre DANS le sens des impulsions, PENDANT les corrections.
```

Cette distinction est la compétence la plus rentable de toute la price action.
Elle permet de répondre à la seule question qui compte pendant un retracement :
« est-ce une pause ou un retournement ? »

### Le graphique propre

Un graphique de travail contient : la structure marquée (pivots), quatre lignes
horizontales (plus haut/plus bas de la veille, clôture de la veille, ouverture
du jour), et une ou deux zones actives. Rien d'autre.

Un graphique surchargé ne produit pas plus d'information : il produit plus de
justifications.

::: retenir
- Le prix est l'information de premier rang ; les indicateurs en dérivent.
- Trois lectures suffisent : rejet, absorption, déplacement.
- Distinguer impulsion et correction est la compétence centrale.
- Un graphique propre force une décision claire.
:::

::: erreur
- Mémoriser trente figures de chandeliers au lieu de trois lectures.
- Trader une bougie de retournement sans contexte de niveau ni de structure.
- Ajouter un indicateur après chaque perte.
- Confondre « pas d'indicateur » et « pas de règles » : la price action sans
  règles écrites devient une justification a posteriori.
:::

::: resume
**Price action en une page.** Lisez le corps (qui a gagné la période), la mèche
(où le prix a été refusé) et l'enchaînement (impulsion ou correction).
L'essentiel se résume à trois observations : un rejet montre où sont les
ordres, une absorption montre qu'un acteur important est de l'autre côté, un
déplacement montre une intention. Gardez un graphique propre : structure,
quatre niveaux de référence, une ou deux zones. Ce que vous ne pouvez pas
décider en dix secondes sur un graphique propre, vous ne le déciderez pas mieux
avec cinq indicateurs.
:::

## Chapitre 6 — Le volume

Le volume est la seule donnée qui ne soit pas dérivée du prix. Il mesure la
**participation** : combien de contrats ont réellement changé de mains.

### La loi fondamentale : effort contre résultat

```schema
   Volume ████████  ·  Prix ███████   ──► mouvement sain, participation réelle
   Volume ████████  ·  Prix ▪         ──► ABSORPTION : retournement probable
   Volume ▂         ·  Prix ███████   ──► mouvement creux, peu fiable
   Volume ▂         ·  Prix ▪         ──► désintérêt, range
```

Un gros effort pour un petit résultat est le signal le plus fiable du
retournement. C'est la signature d'un acteur qui encaisse tout ce qui lui est
envoyé.

### Les quatre situations à reconnaître

| Situation | Signature | Interprétation |
|---|---|---|
| **Climax** | Volume record + grande bougie + mèche | Capitulation, borne du mouvement |
| **Absorption** | Volume record + petite bougie | Un gros opère à contre-courant |
| **Test réussi** | Retour sur l'extrême à volume faible | Plus de pression adverse : feu vert |
| **Correction saine** | Retracement à volume décroissant | La tendance reprendra |

### Le cas particulier du Forex

Il n'existe pas de volume centralisé sur le marché des changes au comptant : ce
que votre plateforme affiche est un **volume tick** (nombre de changements de
prix), utile comme approximation de l'activité, mais qui ne mesure pas la
quantité échangée.

Solution pratique : lire le volume sur les **futures** correspondants (6E pour
l'euro, 6B pour la livre, GC pour l'or) et exécuter où vous voulez.

::: retenir
- Effort (volume) contre résultat (prix) : c'est toute la loi.
- Volume élevé sans progression = absorption = retournement probable.
- Volume faible en correction = correction saine.
- Sur le Forex, lisez le volume des futures, pas le volume tick.
:::

::: erreur
- Croire qu'un volume élevé signifie « des acheteurs » : chaque transaction a
  un acheteur **et** un vendeur.
- Interpréter le volume tick du Forex comme un volume réel.
- Utiliser le volume seul, sans niveau de référence.
- Ignorer le volume sur les mèches de purge, qui est pourtant l'élément le plus
  informatif du graphique.
:::

::: resume
**Volume en une page.** Le volume mesure la participation, pas la direction.
Comparez toujours l'effort au résultat : un volume énorme qui ne produit qu'une
petite bougie signale qu'un acteur important absorbe le flux — c'est le meilleur
signal de retournement disponible. Un volume record sur une mèche signale une
purge de stops réussie. Un volume qui décroît pendant une correction confirme
que la tendance reprendra. Sur le Forex de détail, le volume affiché n'est
qu'un compteur de ticks : utilisez les futures pour obtenir la vraie donnée.
:::

## Chapitre 7 — L'order flow

L'order flow est l'étage en dessous du volume : non plus « combien », mais
« qui a été agressif ». C'est l'information la plus proche de la réalité.

### Les quatre outils

| Outil | Ce qu'il montre |
|---|---|
| **Carnet d'ordres (DOM)** | Les intentions affichées — manipulables (*spoofing*) |
| **Time and sales** | Les transactions réellement exécutées |
| **Footprint** | Volume au bid et au ask, prix par prix |
| **Delta cumulé (CVD)** | Agressivité nette accumulée dans le temps |

Seules les **exécutions** comptent. Le carnet affiche des intentions qui peuvent
être retirées en une milliseconde.

### La configuration à connaître : l'absorption

```schema
   Prix    Bid × Ask
   4 501   120 × 340
   4 500  3 000 × 210   ← 3 000 contrats vendus agressivement…
   4 499   180 × 260       …et le prix ne baisse pas
   ➜ un acheteur passif absorbe tout : rebond probable
```

### La divergence prix / delta

```schema
   Prix  ╱╲    ╱╲╱  nouveau plus haut
   CVD   ╱╲   ╱╲    sommet plus bas
   ➜ les acheteurs poussent moins fort : le sommet est vendu
```

### Ce qui est réaliste pour un particulier

L'order flow exige des données centralisées (futures, actions) et un
abonnement. En SMC pur, la mèche et le volume en sont l'équivalent appauvri :
une longue mèche sur volume record **est** une absorption visible à l'œil nu.

::: retenir
- Seules les exécutions comptent, pas les ordres affichés.
- L'absorption — beaucoup d'agressivité, aucun résultat — est la configuration
  clé.
- La divergence prix/delta signale un essoufflement aux extrêmes.
- Sans données de futures, la mèche + le volume jouent le même rôle.
:::

::: erreur
- Faire de l'order flow sur des données Forex de détail.
- Lire le flux sans niveau de référence : on se noie dans le détail.
- Prendre le carnet pour la vérité : il est fait pour être vu, donc pour
  tromper.
- Trader le delta seul, sans structure ni zone.
:::

::: resume
**Order flow en une page.** Il répond à la question que le volume laisse
ouverte : qui a été agressif ? Quand une agressivité massive ne produit aucun
mouvement de prix, c'est qu'un acteur passif absorbe — et c'est le meilleur
signal de retournement qui existe. Quand le prix fait un nouvel extrême sans
que le delta cumulé ne suive, le mouvement n'est pas soutenu. Ces deux lectures
suffisent. Elles exigent des données centralisées ; à défaut, une longue mèche
accompagnée d'un volume record raconte exactement la même histoire.
:::

## Chapitre 8 — La liquidité

Si vous ne deviez retenir qu'un seul chapitre de ce livre, ce serait celui-ci.

### Le principe

Le prix ne se déplace pas vers une valeur : **il se déplace vers les ordres**.
Un acteur qui doit acheter 5 000 contrats a besoin de 5 000 contrats à vendre
en face. Ces vendeurs, il les trouve là où sont les ordres stop : sous les
creux, au-dessus des sommets.

D'où le renversement de perspective qui change tout :

```schema
   Lecture naïve      « le support va tenir »
   Lecture réelle     « sous le support, il y a des ordres à prendre »
```

### La carte de la liquidité

| Zone | Type | Force |
|---|---|---|
| Equal highs / equal lows | BSL / SSL | ★★★ |
| Plus haut / plus bas de la veille (PDH/PDL) | BSL / SSL | ★★★ |
| Plus haut / plus bas de la semaine | BSL / SSL | ★★★ |
| Bornes du range asiatique | BSL / SSL | ★★ |
| Chiffres ronds | Mixte | ★★ |
| Sommet/creux de session | BSL / SSL | ★★ |
| Lignes de tendance suivies | Liquidité diagonale | ★ |

### L'inducement : la liquidité qui précède la vraie zone

```schema
        ╱╲
      ╱   ╲    ● inducement (le creux « évident »)
    ╱       ╲ ╱╲
             ╲  ╲
   ▓▓▓▓▓▓▓▓▓▓▓▓▓ ╲▼  Order Block HTF (la vraie zone)
   ➜ il faut consommer ● avant de pouvoir remplir ▓
```

C'est la réponse à la question la plus douloureuse du trading : « pourquoi mon
stop a-t-il été touché de deux points avant que ça parte sans moi ? »

### Les deux questions obligatoires

Avant chaque entrée, sans exception :

1. **Quelle liquidité vient d'être prise ?** (d'où vient le carburant)
2. **Quelle liquidité est visée ?** (où va le prix)

Sans réponse aux deux, il n'y a pas de trade.

::: retenir
- Le prix va chercher les ordres, pas la valeur.
- Vos stops **sont** la liquidité : placez-les au-delà de l'évidence.
- L'inducement doit être consommé avant que la vraie zone fonctionne.
- Objectif juste **avant** un pool, stop juste **au-delà**, jamais dedans.
:::

::: erreur
- Placer un stop deux points sous des *equal lows*.
- Viser un objectif dans le vide, sans pool de liquidité en face.
- Entrer sur la première zone évidente sans attendre la purge.
- Interpréter chaque purge comme un retournement : sans CHoCH derrière, ce
  n'est qu'une continuation.
:::

::: resume
**Liquidité en une page.** Le marché est un système d'appariement : les gros
ordres ne peuvent s'exécuter que là où de nombreux ordres opposés attendent,
c'est-à-dire aux endroits où le public place ses stops — sous les creux, au-dessus
des sommets, aux chiffres ronds, aux extrêmes de la veille. Le prix se déplace
donc d'une poche de liquidité à l'autre. Cette lecture explique les faux
cassages, les mèches absurdes et les stops touchés au point près. Elle donne
aussi la méthode : attendre que la liquidité soit prise, vérifier que la
structure change, entrer dans le déséquilibre laissé, viser la poche opposée.
:::

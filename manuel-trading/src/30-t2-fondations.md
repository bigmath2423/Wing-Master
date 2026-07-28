# Tome 2 — Les concepts expliqués

Vingt-six chapitres, une seule logique. Chacun se termine par trois blocs :
**à retenir absolument**, **les erreurs**, **résumé en une page**. Si vous êtes
pressé, lisez uniquement ces trois blocs — ils contiennent l'essentiel.

::: astuce L'ordre de lecture recommandé
Dow → Wyckoff → Liquidité → Structure (BOS/CHoCH/MSS) → Zones (OB/FVG) →
Premium/Discount → Sessions. Le reste s'ajoute ensuite. Ces sept chapitres
suffisent à trader.
:::

## Chapitre 1 — La théorie de Dow

Charles Dow, fondateur du *Wall Street Journal*, n'a jamais écrit de livre : sa
théorie a été reconstituée après sa mort à partir de ses éditoriaux. Elle reste
la fondation de toute l'analyse technique, y compris de celles qui prétendent
s'en affranchir.

### Les six principes

| # | Principe | Ce qu'il signifie concrètement |
|---|---|---|
| 1 | Les indices intègrent tout | Toute information connue est déjà dans le prix. Inutile de courir après la nouvelle. |
| 2 | Trois types de tendance | Primaire (mois/années), secondaire (semaines), mineure (jours). |
| 3 | Trois phases | Accumulation, participation du public, distribution. |
| 4 | Les indices doivent se confirmer | Un mouvement non confirmé par un indice corrélé est suspect (ancêtre de la divergence SMT). |
| 5 | Le volume confirme la tendance | Le volume doit croître dans le sens de la tendance. |
| 6 | Une tendance dure jusqu'à signal contraire | Elle continue tant qu'elle n'est pas cassée — pas tant qu'elle « paraît » excessive. |

### Ce qui en reste aujourd'hui

Le cœur opérationnel de Dow tient en une phrase : **une tendance haussière est
une succession de sommets et de creux ascendants**. C'est la définition que le
SMC réutilise mot pour mot sous les noms de HH/HL et de BOS.

```schema
   Tendance primaire (D1/W1)   ▁▂▃▄▅▆▇█  ← ce qu'on suit
     Tendance secondaire (H4)     ▇▆▅▆▇  ← ce qu'on attend (correction)
       Tendance mineure (M15)       ▅▆▅  ← ce qu'on ignore (bruit)
```

Le principe 4 — la confirmation entre indices — est le plus sous-estimé. Il
est aujourd'hui exploité sous le nom de **divergence SMT** : si le S&P fait un
nouveau plus haut mais que le Nasdaq échoue, la hausse n'est pas confirmée.

Le principe 6 est celui qui coûte le plus cher à ignorer : le trader vend parce
que « c'est monté trop vite », alors qu'aucun signal contraire n'a été donné.

::: retenir
- Une tendance se définit par ses **pivots**, pas par une impression visuelle.
- Elle reste valide **jusqu'à la cassure structurelle**, pas jusqu'à ce qu'elle
  vous semble exagérée.
- Trois échelles coexistent en permanence : précisez toujours de laquelle vous
  parlez.
- Deux marchés corrélés doivent se confirmer ; l'absence de confirmation est un
  signal en soi.
:::

::: erreur
- Déclarer un retournement à chaque correction secondaire.
- Vendre « parce que c'est trop haut » : ce n'est pas un signal contraire.
- Confondre l'échelle de son analyse et celle de son exécution.
- Ignorer le volume, qui reste le seul juge de la participation réelle.
:::

::: resume
**Dow en une page.** Le prix contient déjà tout. Il évolue en trois échelles
imbriquées. Une tendance haussière est une suite de HH/HL, une tendance
baissière une suite de LH/LL, et elle dure jusqu'à preuve du contraire — la
preuve étant la cassure d'un pivot majeur, jamais une opinion. Le volume doit
accompagner le mouvement ; les marchés corrélés doivent se confirmer. Tout le
reste de l'analyse technique moderne est une reformulation de ces six points.
:::

## Chapitre 2 — Wyckoff

Richard D. Wyckoff a formalisé, dans les années 1910-1930, ce que font les
grands opérateurs. Sa méthode ne cherche pas à prédire : elle cherche à
identifier **qui contrôle le marché** à un instant donné.

### Les trois lois

| Loi | Énoncé | Application |
|---|---|---|
| **Offre et demande** | Le prix monte quand la demande excède l'offre | Regarder qui est absorbé, pas qui crie le plus fort |
| **Cause et effet** | La durée du range (cause) détermine l'ampleur du mouvement (effet) | Un range de trois semaines produit un mouvement plus grand qu'un range de trois heures |
| **Effort contre résultat** | Un gros volume sans progression signale une absorption | Volume record + bougie étroite = retournement proche |

### L'opérateur composite

Wyckoff propose de considérer l'ensemble des mains fortes comme un seul acteur
rationnel : le *composite operator*. Il achète quand personne n'en veut, vend
quand tout le monde en veut, et a besoin de vous pour le faire.

Ce n'est pas une théorie du complot : c'est un modèle mental. Un ordre de
plusieurs milliers de contrats ne peut être exécuté que là où existe une
contrepartie — donc là où le public est actif.

### Le schéma d'accumulation

```schema
  PHASE A          PHASE B            PHASE C      PHASE D        PHASE E
  arrêt de         construction       test         balisage       tendance
  la baisse        de la cause        final        haussier
     SC              ST  ST  ST       SPRING        LPS  SOS         ▲
      │  AR         ╱╲  ╱╲  ╱╲          ▼          ╱╲   ╱          ╱
   ───┼──╱╲────────╱──╲╱──╲╱──╲────────┼─────────╱──╲─╱──────────╱
      ▼╱    ╲    ╱                      ╲______╱
   volume ████    ▃▂▃▂▃▂▃              ████  ▂▂      ▃▅▇
```

| Sigle | Nom | Signification |
|---|---|---|
| **SC** | Selling Climax | Capitulation, volume record |
| **AR** | Automatic Rally | Rebond mécanique, borne haute du range |
| **ST** | Secondary Test | Retour sur le creux, volume réduit |
| **Spring** | — | Faux cassage bas, dernier piège |
| **LPS** | Last Point of Support | Dernier creux avant la hausse |
| **SOS** | Sign of Strength | Cassure haussière avec volume |

La distribution est le miroir exact : BC (*Buying Climax*), AR, ST, **UTAD**,
LPSY (*Last Point of Supply*), SOW (*Sign of Weakness*).

### Comment l'utiliser aujourd'hui

Wyckoff donne le **contexte** ; le SMC donne l'**exécution**. Situez la phase en
D1/H4 (accumulation ou distribution ?), puis entrez avec un Order Block ou un
FVG en H1/M15.

::: retenir
- Trois lois : offre/demande, cause/effet, effort/résultat.
- Quatre phases, toujours dans le même ordre, à toutes les échelles.
- Le **Spring** et l'**UTAD** sont les deux meilleurs points d'entrée du cycle.
- Le volume n'est pas un accessoire : c'est la seule preuve de l'absorption.
:::

::: erreur
- Forcer le schéma : les cas réels sont irréguliers, incomplets, étirés.
- Confondre accumulation et distribution — regardez toujours **ce qui précède**
  le range.
- Acheter le climax au lieu d'attendre le test à volume faible.
- Oublier la loi de cause à effet : un petit range ne produit pas un grand
  mouvement.
:::

::: resume
**Wyckoff en une page.** Le marché alterne quatre phases : accumulation,
hausse, distribution, baisse. Dans les phases de range, les mains fortes
construisent leur position en absorbant les mains faibles. La preuve de cette
absorption est le rapport entre l'effort (volume) et le résultat (prix) :
beaucoup de volume pour peu de mouvement signifie que quelqu'un prend l'autre
côté. Le faux cassage terminal — Spring en bas, UTAD en haut — est le dernier
piège avant le vrai mouvement, et donc le meilleur point d'entrée du cycle.
Situez la phase en haute unité de temps, exécutez en basse.
:::

## Chapitre 3 — ICT

*Inner Circle Trader* désigne le corpus diffusé par Michael Huddleston. Au-delà
du vocabulaire, il apporte trois idées opérationnelles qui ont transformé le
trading de détail.

### Les trois apports

1. **Le prix cherche la liquidité.** Il ne se dirige pas vers une « valeur »
   mais vers les zones où des ordres sont coincés : au-dessus des sommets, sous
   les creux.
2. **Le prix comble les déséquilibres.** Ce qui a été parcouru trop vite (FVG)
   tend à être revisité.
3. **Le temps compte autant que le prix.** Les mouvements significatifs se
   produisent dans des fenêtres précises (Kill Zones), pas n'importe quand.

### Le modèle AMD

```schema
   A — ACCUMULATION    range calme, souvent la session asiatique
   M — MANIPULATION    faux départ (Judas Swing), purge de la liquidité
   D — DISTRIBUTION    vrai mouvement, expansion vers la liquidité opposée

   ░░░░░░░░  ▼purge   ███████████████►
   Asie      Londres 09 h    direction du jour
```

Ce schéma décrit une majorité de journées de tendance : le mouvement réel
commence **après** que la foule a été piégée dans le sens opposé.

### La séquence d'exécution ICT

```schema
   1. Biais HTF (D1/H4)                  « où je vais »
   2. Liquidité prise (PDH/PDL, EQH/EQL) « le carburant est consommé »
   3. Déplacement + MSS                  « le contrôle a changé »
   4. Retour dans le FVG / OB            « mon prix »
   5. Objectif : liquidité opposée       « ma sortie »
```

### Ce qu'il faut en garder — et ce qu'il faut écarter

À garder : liquidité, déséquilibres, temps, structure. Ces quatre notions
suffisent à construire une méthode complète et testable.

À écarter : la surcharge de sigles interchangeables, l'idée d'un algorithme
unique qui « viendrait vous chercher personnellement », et la tentation d'avoir
un concept différent pour chaque situation — ce qui revient à n'avoir aucune
règle.

::: retenir
- Trois piliers : **liquidité**, **déséquilibre**, **temps**.
- Le modèle **AMD** : accumulation, manipulation, distribution.
- Le mouvement du jour commence souvent après un faux départ.
- Une séquence fixe en cinq étapes, appliquée toujours dans le même ordre.
:::

::: erreur
- Empiler quinze concepts pour justifier une entrée impulsive.
- Trader en M1 des concepts pensés pour H1/H4.
- Croire à une intention personnelle du marché contre vous.
- Marquer des Order Blocks partout, sans prise de liquidité ni déplacement.
:::

::: resume
**ICT en une page.** Le marché se déplace pour prendre les ordres en attente,
puis pour combler ce qu'il a laissé derrière lui, à des heures précises. La
journée type suit un schéma en trois temps : un range calme, une manipulation
qui piège la foule, puis le vrai mouvement. La méthode d'exécution est
invariable : biais en haute unité de temps, attente d'une prise de liquidité,
confirmation par un changement de structure avec déplacement, entrée dans le
déséquilibre laissé par ce déplacement, sortie sur la liquidité opposée. Quatre
notions suffisent ; le reste du vocabulaire est optionnel.
:::

## Chapitre 4 — SMC (Smart Money Concepts)

Le SMC est la synthèse opérationnelle de Wyckoff et d'ICT. Sa force est d'être
une méthode **complète** : il donne le biais, la zone, l'invalidation et
l'objectif à partir d'une seule logique.

### Les quatre piliers

```schema
   ┌───────────────┬────────────────────────────────────────┐
   │ STRUCTURE     │ BOS · CHoCH · MSS · HH/HL              │
   │ LIQUIDITÉ     │ BSL · SSL · EQH/EQL · inducement       │
   │ ZONES         │ Order Block · Breaker · Mitigation     │
   │ DÉSÉQUILIBRES │ FVG · IFVG · BPR · liquidity void      │
   └───────────────┴────────────────────────────────────────┘
        + FILTRE : premium / discount
```

### La séquence complète, dans l'ordre

1. **Régime** (W1/D1) — haussier, baissier ou range ?
2. **Biais** (D1/H4) — direction du jour, cible de liquidité, invalidation.
3. **Attente d'une prise de liquidité** — PDL, PDH, EQH/EQL, range asiatique.
4. **Changement de structure** (M15/M5) — CHoCH ou MSS **avec déplacement**.
5. **Zone** — OB ou FVG créé par ce déplacement, situé en discount (achat) ou
   en premium (vente).
6. **Entrée limite** — stop au-delà de la mèche de purge.
7. **Objectif** — liquidité opposée, en deux paliers.

### Les trois filtres qui éliminent 80 % des mauvais trades

| Filtre | Question | Si la réponse est non |
|---|---|---|
| **Premium/discount** | Suis-je du bon côté de l'équilibre ? | Pas de trade |
| **Inducement** | La liquidité intermédiaire a-t-elle été prise ? | Attendre |
| **Déplacement** | La cassure est-elle impulsive, avec FVG ? | Ce n'est pas un signal |

### Les limites honnêtes du SMC

Le vocabulaire est propre au trading de détail : aucun desk ne parle d'« Order
Block ». Les **mécanismes** décrits sont réels — recherche de contrepartie,
exécution en déséquilibre, concentration des stops — mais la méthode reste une
grille de lecture, pas une science. Sa qualité dépend entièrement de la
discipline de marquage : si vous marquez trois OB par graphique, vous trouverez
toujours une raison d'entrer.

::: retenir
- Quatre piliers : structure, liquidité, zones, déséquilibres.
- Une séquence fixe en sept étapes, jamais dans le désordre.
- Trois filtres éliminent l'essentiel des mauvais trades.
- Sans prise de liquidité **et** sans déplacement, une zone ne vaut rien.
:::

::: erreur
- Marquer des zones partout jusqu'à couvrir le graphique entier.
- Entrer sur un OB situé du mauvais côté de l'équilibre.
- Sauter l'étape de la liquidité : c'est elle qui déclenche tout le reste.
- Utiliser M1 comme unité de biais.
:::

::: resume
**SMC en une page.** Le marché prend d'abord la liquidité (les stops), puis
change de structure (CHoCH ou MSS avec déplacement), puis revient dans le
déséquilibre laissé par ce déplacement (FVG ou Order Block), avant de repartir
chercher la liquidité opposée. Votre travail consiste à attendre ces quatre
événements dans cet ordre, du bon côté de l'équilibre du range, dans une
fenêtre horaire active. Si l'un des quatre manque, il n'y a pas de trade. Cette
seule discipline vaut plus que la connaissance de trente concepts.
:::

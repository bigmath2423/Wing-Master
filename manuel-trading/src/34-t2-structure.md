## Chapitre 19 — Le Liquidity Sweep

### La séquence en trois temps — jamais deux

```schema
   ────────────────── plus bas de la veille (SSL)
          │
   1      ▼ mèche de purge      ← les stops sautent
          ╲__╱ retour rapide
   2          ╱╲__ CHoCH        ← la structure change
   3            ▓▓ entrée dans le FVG / OB
```

L'erreur universelle consiste à entrer à l'étape 1. Une purge seule ne signifie
rien : le prix peut parfaitement continuer. C'est le **CHoCH** qui transforme la
purge en signal.

### Les critères de qualité d'une purge

| Critère | Bon | Mauvais |
|---|---|---|
| Vitesse du retour | 1 à 3 bougies | Plusieurs heures |
| Volume sur la mèche | Élevé | Faible |
| Niveau purgé | PDH/PDL, EQH/EQL, extrême de session | Pivot mineur |
| Ce qui suit | Déplacement franc | Dérive molle |
| Moment | Kill Zone | Milieu de journée |

### Purge simple ou double

```schema
   Purge simple      ▼      retour, CHoCH, départ
   Double purge      ▼  ▼   première purge, faux départ, seconde purge plus basse
```

La double purge est fréquente sur les niveaux majeurs. C'est la raison pour
laquelle le stop se place **au-delà de la mèche avec une marge**, et non à son
extrémité exacte.

### Le cas où la purge n'est pas un signal

Si la structure ne change pas après la purge, c'est une **continuation** : le
niveau a simplement été traversé. Le distinguer est simple — pas de CHoCH, pas
de trade de retournement. On repasse alors en mode continuation.

::: retenir
- Trois étapes : purge, CHoCH, entrée. Jamais deux.
- La purge seule n'est pas un signal.
- Stop au-delà de la mèche, avec marge, à cause des doubles purges.
- Une purge sans changement de structure est une continuation.
:::

::: erreur
- Entrer dès la mèche, avant toute confirmation.
- Considérer chaque nouveau plus bas comme une purge.
- Placer le stop à un point de la mèche.
- Purger, se faire sortir, puis réentrer immédiatement dans le même sens.
:::

::: resume
**Liquidity sweep en une page.** Le marché va chercher les ordres stop
accumulés au-delà d'un extrême évident, les déclenche, puis se retourne parce
que ces ordres viennent de fournir la contrepartie dont un acteur important
avait besoin. Le signal complet compte trois temps : la purge (le carburant), le
changement de caractère (la preuve que le contrôle a changé), l'entrée dans le
déséquilibre laissé (le prix). Sauter l'étape intermédiaire transforme le
meilleur signal du modèle en pari sur une mèche.
:::

## Chapitre 20 — La structure interne

### Définition

La structure interne est celle qui se déploie **à l'intérieur** d'un mouvement
de la structure externe : les oscillations mineures d'une jambe majeure.

```schema
   EXTERNE   ●─────────────────────────● (le mouvement principal)
   INTERNE      ╱╲  ╱╲  ╱╲  ╱╲            (les oscillations à l'intérieur)
```

### À quoi elle sert

| Usage | Détail |
|---|---|
| **Exécution** | Elle fournit le CHoCH d'entrée dans une zone HTF |
| **Inducement** | Ses pivots sont les faux points d'entrée à purger |
| **Stop** | Elle permet un stop court, donc un ratio élevé |

### Le piège majeur

La structure interne produit en permanence des BOS et des CHoCH qui n'ont
**aucune valeur directionnelle**. Un retracement H4 vu en M5 est une tendance
baissière parfaite, avec cinq BOS successifs.

```schema
   H4   ▁▁▁▁▁▁▁▁▁▁▁  un simple retracement
   M5      ▃▃▃▃▃      une « tendance baissière » complète
   ➜ les deux sont vraies · seule la H4 commande
```

### La règle qui évite l'erreur

**La structure interne ne change jamais le biais.** Elle sert uniquement à
l'exécution à l'intérieur d'une zone déjà validée par la structure externe.

::: retenir
- Interne = oscillations dans une jambe externe.
- Elle sert à l'entrée, jamais au biais.
- Ses pivots sont l'inducement à purger.
- Un CHoCH interne n'annule pas un BOS externe.
:::

::: erreur
- Changer de biais sur un CHoCH interne.
- Marquer autant de pivots internes qu'externes, jusqu'à illisibilité.
- Confondre la fin d'une correction interne et un retournement majeur.
- Utiliser la structure interne d'une unité trop basse (M1) par rapport à la
  zone visée (H4).
:::

::: resume
**Structure interne en une page.** Chaque grand mouvement contient de petits
mouvements complets, avec leurs propres sommets, creux et cassures. Cette
structure interne est indispensable à l'exécution : elle fournit le signal
d'entrée précis à l'intérieur d'une zone validée en haute unité de temps, et un
stop court. Mais elle ne détermine jamais la direction. Toute la difficulté du
multi-échelle tient là : ce que vous voyez en M5 est vrai, complet et
convaincant — et pourtant subordonné à ce que dit le H4.
:::

## Chapitre 21 — La structure externe

### Définition

La structure externe est celle des pivots majeurs de votre unité de biais :
ceux qui, une fois cassés, changent réellement la direction.

```schema
   ●───────╲              ●  = pivots externes (majeurs)
             ╲    ●
               ╲╱   ╲
                      ╲───────●
   ➜ ce sont ces points qui définissent la tendance et l'invalidation
```

### Comment marquer proprement

1. Choisissez votre unité de biais (D1 ou H4) et n'en changez pas.
2. Ne marquez qu'un pivot lorsqu'il a été **confirmé** : un sommet est validé
   quand le creux qui le précède est cassé.
3. Trois à cinq pivots visibles par écran, pas davantage.
4. Ne redessinez jamais après coup pour justifier une position.

### Le lien externe / interne

| Niveau | Rôle | Question à laquelle il répond |
|---|---|---|
| **Externe (D1/H4)** | Biais et invalidation | Où vais-je ? |
| **Zone (H1/M15)** | Prix d'entrée | À quel prix ? |
| **Interne (M5)** | Déclencheur | Quand exactement ? |

### La liquidité externe

Les extrêmes de la structure externe sont les pools de liquidité majeurs :
ERL (*External Range Liquidity*). Ce sont vos **objectifs**, jamais vos entrées.

::: retenir
- L'externe donne le biais et l'invalidation.
- Un pivot ne se marque qu'une fois confirmé.
- Trois à cinq pivots par écran suffisent.
- Ses extrêmes sont des objectifs, pas des zones d'entrée.
:::

::: erreur
- Redessiner la structure après une perte pour se donner raison.
- Marquer chaque micro-oscillation comme un pivot majeur.
- Changer d'unité de biais en cours de séance.
- Entrer sur un extrême externe au lieu de l'utiliser comme cible.
:::

::: resume
**Structure externe en une page.** Ce sont les grands pivots de votre unité de
biais : ils définissent la tendance, le niveau qui l'invalide et les pools de
liquidité qui serviront d'objectifs. Marquez-les avec parcimonie — trois à cinq
par écran — et seulement une fois confirmés. Toute votre journée se construit à
partir de là : le biais vient de l'externe, le prix d'entrée d'une zone
intermédiaire, le déclencheur de la structure interne. Le jour où vous
redessinez l'externe pour justifier une position, vous avez cessé d'analyser.
:::

## Chapitre 22 — Kill Zones

### Les fenêtres (heures de Paris)

| Fenêtre | Horaire | Ce qui s'y passe |
|---|---|---|
| **Asian Range** | 00 h – 05 h | Construction du range, faible volatilité |
| **London Kill Zone** | 08 h – 11 h | Purge du range asiatique, direction du jour |
| **New York Kill Zone** | 14 h 30 – 17 h | Publications macro, extension ou retournement |
| **London Close** | 17 h – 19 h | Retournements fréquents, prises de profit |

### Pourquoi elles fonctionnent

Ce ne sont pas des heures magiques. Elles concentrent :

- les ouvertures des marchés au comptant ;
- les publications économiques (14 h 30, 16 h) ;
- les fixings (16 h à Londres) ;
- le passage des ordres institutionnels programmés.

Plus de flux réel, donc plus de mouvements qui aboutissent.

### La discipline horaire

```schema
   00 h ─── 08 h   ░░░░░░  observation
   08 h ─── 11 h   ██████  TRADING
   11 h ─── 14 h 30 ░░░░░  interdit (pièges de mi-journée)
   14 h 30 ─ 17 h  ██████  TRADING
   17 h ─── 00 h   ░░░░░░  observation, gestion des positions ouvertes
```

Une règle horaire écrite supprime, à elle seule, la majorité des trades
d'ennui.

::: retenir
- Deux fenêtres de trading par jour, pas davantage.
- La mi-journée européenne (11 h – 14 h 30) est la zone la plus piégeuse.
- L'heure fait partie du setup : un signal hors fenêtre n'est pas un signal.
- La clôture de Londres retourne fréquemment le mouvement du jour.
:::

::: erreur
- Trader huit heures d'affilée : la qualité des décisions s'effondre.
- Prendre un setup identique à 12 h 45 en pensant qu'il vaut celui de 09 h 30.
- Oublier les décalages horaires saisonniers entre l'Europe et les États-Unis.
- Croire qu'une Kill Zone garantit un mouvement : c'est une condition
  nécessaire, pas suffisante.
:::

::: resume
**Kill zones en une page.** Le marché ne délivre pas ses mouvements de manière
uniforme : le volume, les publications et les ordres institutionnels se
concentrent sur quelques heures. Londres (08 h – 11 h) donne généralement la
direction du jour après avoir purgé le range asiatique ; New York (14 h 30 –
17 h) l'étend ou la renverse. En dehors, les spreads s'élargissent, les
mouvements n'aboutissent pas et les faux signaux se multiplient. Inscrire une
règle horaire dans son plan supprime mécaniquement la majorité des trades pris
par ennui.
:::

## Chapitre 23 — Les sessions

### La personnalité de chaque session

| Session | Horaire (Paris) | Comportement typique |
|---|---|---|
| **Sydney / Tokyo** | 00 h – 09 h | Range étroit, 20-30 % de l'ADR, spreads plus larges |
| **Londres** | 09 h – 18 h | Purge puis expansion ; le plus grand mouvement du jour |
| **Recouvrement** | 14 h 30 – 18 h | Volume maximal, mouvements les plus francs |
| **New York seule** | 18 h – 23 h | Extension, ou retournement de fin de journée |

### Le schéma quotidien le plus fréquent

```schema
   ASIE            LONDRES               NEW YORK
   ░░░░░░░░        ▼ purge               ████████►
   range étroit    puis expansion        extension ou retournement
   ──────────────────────────────────────────────────────────►
   00 h            09 h                  14 h 30          23 h
```

### Les repères à tracer chaque jour

1. Haut et bas du **range asiatique**.
2. Plus haut et plus bas de la **veille**.
3. **Ouverture** de la journée.
4. Haut et bas de la session de **Londres** (une fois formée).

Quatre à six lignes, pas plus. Elles suffisent à expliquer la majorité des
mouvements de la journée.

::: retenir
- L'Asie construit, Londres purge et donne la direction, New York étend ou
  renverse.
- Le recouvrement 14 h 30 – 18 h concentre le volume maximal.
- Les bornes du range asiatique sont les premières cibles de Londres.
- Quatre à six lignes suffisent pour cartographier une journée.
:::

::: erreur
- Trader la session asiatique sur des paires européennes.
- Ignorer le changement d'heure : deux semaines par an, tous vos repères sont
  décalés d'une heure.
- Considérer le premier mouvement de Londres comme la direction du jour.
- Laisser courir une position intraday au-delà de la clôture de New York sans
  décision explicite.
:::

::: resume
**Sessions en une page.** La journée de trading suit une grammaire stable :
l'Asie construit un range étroit qui devient le réservoir de liquidité ; Londres
ouvre en purgeant l'un de ses deux côtés, puis délivre le mouvement principal ;
New York prolonge ce mouvement ou le renverse, souvent autour de la clôture de
Londres. Tracer le range asiatique, les extrêmes de la veille et l'ouverture du
jour suffit à donner une carte complète. Le reste — le choix du moment — découle
des Kill Zones.
:::

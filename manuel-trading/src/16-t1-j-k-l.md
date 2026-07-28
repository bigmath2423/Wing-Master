## J — JOURNAL DE TRADING → JUDAS SWING

### JOURNAL DE TRADING
*Registre de tous les trades, avec leur raison, leur exécution et leur émotion.*

- **Définition simple** — Le carnet où vous écrivez ce que vous faites et pourquoi.
- **Définition pro** — Base de données personnelle permettant de mesurer l'espérance par setup, par session, par heure et par état psychologique, et d'isoler la cause des pertes récurrentes.
- **Pourquoi c'est important** — C'est le seul outil qui transforme l'expérience en compétence. Sans journal, on répète les mêmes erreurs pendant des années en croyant progresser.
- **Comment le reconnaître** — Tableur, application dédiée ou cahier. Ce qui compte est la constance, pas l'outil.
- **Comment les institutions l'utilisent** — Chaque desk conserve un historique complet, revu périodiquement avec le risk manager : attribution de performance, analyse des sorties, coût du slippage.
- **Comment je dois l'utiliser** — Une ligne avant l'entrée (setup, zone, invalidation, cible, risque) et une ligne après la sortie (résultat en R, respect du plan, émotion, capture d'écran). Revue hebdomadaire obligatoire.
- **Erreurs fréquentes** — Ne noter que les gains ; remplir le journal une fois par mois de mémoire ; y consigner des émotions sans jamais en tirer de règle.
- **Pièges** — Un journal sans revue est un journal inutile. La valeur est dans la relecture, pas dans l'écriture.
- **Exemple concret** — Après 60 trades, la relecture montre que tous les trades pris avant 09 h ont une espérance négative : une règle horaire suffit à redresser le mois.

```schema
  AVANT   │ setup · zone · invalidation · cible · risque en R
  PENDANT │ respect du plan ? (oui / non)
  APRÈS   │ résultat en R · émotion · capture · leçon
  ─────────────────────────────────────────────
  REVUE   │ chaque dimanche : 3 chiffres, 1 règle à corriger
```

::: memo
➡ Écrire avant ➡ Mesurer après ➡ Relire chaque semaine ➡ Sinon rien ne change
:::

### JUDAS SWING
*Faux mouvement d'ouverture destiné à piéger les traders avant le vrai départ.*

- **Définition simple** — Le marché part dans un sens à l'ouverture, juste pour tromper, puis fait l'inverse.
- **Définition pro** — Manipulation d'ouverture de session (Londres ou New York) qui balaie la liquidité du range précédent — souvent le range asiatique — avant le déplacement dans la direction réelle de la journée. C'est la phase « manipulation » du modèle *Accumulation – Manipulation – Distribution*.
- **Pourquoi c'est important** — Il transforme le pire moment de la journée (l'ouverture) en meilleur point d'entrée, à condition de l'attendre au lieu de le suivre.
- **Comment le reconnaître** — Dans les 30 à 90 minutes suivant l'ouverture : poussée hors du range asiatique, absence de suivi, retour rapide à l'intérieur, puis déplacement opposé avec FVG.
- **Comment les institutions l'utilisent** — L'ouverture concentre les ordres en attente : c'est le moment de la journée où la liquidité est la plus abondante, donc le meilleur moment pour se remplir à contre-courant du public.
- **Comment je dois l'utiliser** — Je ne trade jamais les 15 premières minutes. J'attends la purge d'un côté, le CHoCH sur M5, puis j'entre au retour dans le FVG.
- **Erreurs fréquentes** — Entrer sur la première impulsion d'ouverture ; conclure que le biais du jour est faux parce que la première heure le contredit.
- **Pièges** — Certains jours de tendance ne comportent aucun Judas : attendre indéfiniment fait rater le mouvement. D'où la nécessité d'une heure limite (par exemple, 11 h pour Londres).
- **Exemple concret** — Biais haussier. À 09 h 05, chute sous le plus bas asiatique de 15 pips, mèche, retour, CHoCH haussier à 09 h 25, puis 70 pips de hausse.

```schema
   09 h 00 ouverture
        │  ▲ faux départ (Judas)
   ─────┼──╲──────── haut du range asiatique
        │    ╲
   ─────┼──────╲──── bas du range asiatique
        │        ▼ purge
        │         ╲__╱▲▲▲ vrai mouvement
```

::: memo
➡ Faux départ à l'ouverture ➡ Purge ➡ Le vrai mouvement part après ➡ Ne jamais suivre la première bougie
:::

## K — KELLY → KILL ZONE

### KELLY (CRITÈRE DE)
*Formule donnant la fraction de capital optimale pour maximiser la croissance à long terme.*

- **Définition simple** — Combien miser pour faire croître le compte le plus vite sans le faire exploser.
- **Définition pro** — `f* = p − q/b`, où `p` est la probabilité de gain, `q = 1 − p` et `b` le ratio gain/perte. Maximise l'espérance du logarithme du capital ; toute mise supérieure réduit la croissance et augmente la ruine.
- **Pourquoi c'est important** — Il prouve mathématiquement qu'il existe une taille au-delà de laquelle même une stratégie gagnante finit par ruiner.
- **Comment le reconnaître** — Se calcule à partir des statistiques de votre journal, jamais à partir d'estimations optimistes.
- **Comment les institutions l'utilisent** — Comme repère théorique, avec application fractionnaire (un quart ou un demi Kelly), car les paramètres sont incertains et instables.
- **Comment je dois l'utiliser** — Je calcule Kelly sur mes 100 derniers trades, puis j'applique un quart de la valeur obtenue. Dans la pratique, cela ramène presque toujours à 0,5–1 % par trade.
- **Erreurs fréquentes** — Utiliser Kelly avec des statistiques issues de 15 trades ; appliquer Kelly plein (volatilité insupportable) ; oublier que `p` varie selon les régimes de marché.
- **Pièges** — Surestimer `p` de 5 points suffit à transformer une taille « optimale » en taille ruineuse.
- **Exemple concret** — p = 0,45, b = 2 : `f* = 0,45 − 0,55/2 = 0,175`, soit 17,5 % du capital. Un quart de Kelly donne 4,4 % — encore trop pour un compte à levier : d'où le plafond pratique de 1 %.

```schema
  f* = p − q/b
  p = 45 %  ·  b = 2  ──►  f* = 17,5 %   (théorique, insoutenable)
  ¼ Kelly              ──►  4,4 %        (encore élevé)
  Pratique             ──►  0,5 – 1 %    (survie et régularité)
```

::: memo
➡ Il existe une taille maximale ➡ Au-delà, même une bonne méthode ruine ➡ Rester sous le quart
:::

### KILL ZONE
*Plage horaire où la probabilité de mouvement significatif est la plus forte.*

- **Définition simple** — Les créneaux de la journée où il faut être devant l'écran.
- **Définition pro** — Fenêtres définies par le modèle ICT autour des ouvertures : Londres (08 h–11 h), New York (14 h 30–17 h), *London Close* (17 h–19 h), *Asian Range* (00 h–05 h), heures de Paris. Elles concentrent volume, volatilité et prises de liquidité.
- **Pourquoi c'est important** — Trader hors de ces plages, c'est accepter des spreads plus larges, moins de volume et des mouvements sans suite. Le même setup n'a pas la même espérance à 10 h et à 13 h.
- **Comment le reconnaître** — Se marquent sur le graphique par des zones verticales ; visibles aussi par le pic de volume à ces heures.
- **Comment les institutions l'utilisent** — Les fixings, les ouvertures de marchés au comptant et les publications macro sont concentrés sur ces créneaux : c'est le moment où les flux réels passent.
- **Comment je dois l'utiliser** — Je ne prends de position que dans deux fenêtres : 09 h–11 h et 14 h 30–17 h. En dehors, j'observe.
- **Erreurs fréquentes** — Trader la pause déjeuner européenne (12 h–14 h), période de faux signaux par excellence ; rester devant l'écran huit heures d'affilée et perdre en concentration.
- **Pièges** — Une Kill Zone n'est pas une garantie de mouvement : c'est une condition nécessaire, pas suffisante. Sans setup, l'heure ne vaut rien.
- **Exemple concret** — Sur l'EURUSD, plus de la moitié du range quotidien se forme entre 09 h et 12 h. Un signal identique à 13 h 15 échoue nettement plus souvent.

```schema
   00 h ──── 05 h  Asie        ░░ range, faible volume
   08 h ──── 11 h  LONDRES     ██ meilleure fenêtre
   12 h ──── 14 h  déjeuner    ░░ pièges, à éviter
   14 h 30 ─ 17 h  NEW YORK    ██ seconde fenêtre
   17 h ──── 19 h  London Close ▓ retournements fréquents
```

::: memo
➡ Deux fenêtres par jour ➡ Hors fenêtre, on observe ➡ L'heure fait partie du setup
:::

## L — LIQUIDATION → LOT / TAILLE DE POSITION

### LIQUIDATION
*Fermeture forcée d'une position par le courtier faute de marge suffisante.*

- **Définition simple** — Le courtier ferme votre position à votre place parce que vous n'avez plus de quoi la tenir.
- **Définition pro** — Déclenchement automatique lorsque le niveau de marge passe sous le seuil réglementaire ou contractuel ; sur les marchés crypto à fort levier, les liquidations s'enchaînent en cascade et amplifient les mouvements.
- **Pourquoi c'est important** — Les zones de liquidation massives sont des aimants : le marché va chercher les niveaux où le plus grand nombre de positions à levier seront fermées de force.
- **Comment le reconnaître** — Mouvements verticaux et sans retracement, mèches de plusieurs pourcents en quelques minutes, cartes de liquidation (crypto).
- **Comment les institutions l'utilisent** — Elles savent où se concentrent les leviers (données publiques sur les dérivés crypto) et poussent le prix vers ces zones, où la liquidité devient gratuite.
- **Comment je dois l'utiliser** — Je ne trade jamais assez gros pour être liquidable avant mon stop. Et je considère les grappes de liquidations comme des cibles, pas comme des accidents.
- **Erreurs fréquentes** — Utiliser un levier tel que la marge saute avant le stop ; ajouter de la marge à une position perdante.
- **Pièges** — La cascade de liquidations dépasse toujours le niveau « raisonnable » : c'est un mouvement mécanique, sans logique de valeur.
- **Exemple concret** — Bitcoin passe de 62 000 à 58 500 $ en douze minutes, 900 millions de dollars de longs liquidés, puis retour à 61 000 $ dans l'heure.

```schema
   Zones de levier concentré
   ▓▓▓▓▓▓▓▓  60 000 $   ← 400 M$ de longs
   ▓▓▓▓▓▓▓▓▓ 58 500 $   ← 900 M$ de longs
   Prix ──────────▼▼▼▼  cascade : chaque liquidation vend, donc fait baisser
```

::: memo
➡ Fermeture forcée ➡ Cascade ➡ Aimant à prix ➡ Ne jamais être liquidable avant son stop
:::

### LIQUIDITÉ
*Présence d'ordres permettant d'acheter ou de vendre sans déplacer fortement le prix.*

- **Définition simple** — Y a-t-il quelqu'un en face pour prendre votre ordre ?
- **Définition pro** — Profondeur du carnet et volume disponible à chaque niveau. En trading directionnel, on parle surtout de *pools de liquidité* : les concentrations d'ordres stop et d'ordres en attente au-delà des extrêmes de prix.
- **Pourquoi c'est important** — C'est le concept central du trading moderne : le prix se déplace **vers** la liquidité, pas vers un objectif de valeur. Comprendre cela remplace des années d'indicateurs.
- **Comment le reconnaître** — Sous les creux et au-dessus des sommets, aux chiffres ronds, sur les *equal highs/lows*, aux extrémités des ranges de session, aux plus hauts et plus bas de la veille et de la semaine.
- **Comment les institutions l'utilisent** — Un ordre de grande taille ne peut être exécuté que là où existe une contrepartie. Elles doivent donc créer ou atteindre la liquidité : d'où les purges, les faux cassages, les mouvements « absurdes ».
- **Comment je dois l'utiliser** — Avant toute entrée, je réponds à deux questions : quelle liquidité vient d'être prise ? quelle liquidité est visée ? Sans réponse, pas de trade.
- **Erreurs fréquentes** — Placer ses stops exactement là où tout le monde les place ; viser un objectif dans le vide, sans pool de liquidité en face.
- **Pièges** — La liquidité évidente est prise en premier : votre stop « bien placé » sous le dernier creux est, littéralement, l'objectif du prochain mouvement.
- **Exemple concret** — Deux creux égaux à 1,0800. Le prix descend à 1,0793, prend tous les stops, puis remonte de 80 pips sans jamais y revenir.

```schema
   ▲▲▲  BSL — stops des vendeurs  ────► cible haussière
   ═══════════════════════════════
        prix actuel
   ═══════════════════════════════
   ▼▼▼  SSL — stops des acheteurs ────► cible baissière
   « le marché se déplace d'une poche de liquidité à l'autre »
```

::: memo
➡ Le prix va chercher les stops ➡ D'où il vient, où il va ➡ Deux questions, toujours
:::

### LIQUIDITY POOL
*Zone où se concentrent de nombreux ordres en attente.*

- **Définition simple** — Un réservoir d'ordres, empilés au même endroit.
- **Définition pro** — Regroupement d'ordres stop, d'ordres limite et d'entrées de cassure sur un niveau ou une zone étroite : sommets/creux égaux, chiffres ronds, extrêmes de session, plus haut ou plus bas de la veille et de la semaine.
- **Pourquoi c'est important** — Les pools sont les seules destinations réellement prévisibles du prix : ce sont les objectifs naturels de tout mouvement.
- **Comment le reconnaître** — Alignement de mèches, niveaux testés plusieurs fois, chiffres ronds majeurs (1,1000 ; 2 000 $ ; 20 000 points).
- **Comment les institutions l'utilisent** — Elles cartographient ces zones (elles voient une partie du flux client) et y dirigent l'exécution.
- **Comment je dois l'utiliser** — Mes objectifs se placent **juste avant** un pool, mes stops **au-delà** d'un pool, jamais à l'intérieur.
- **Erreurs fréquentes** — Prendre profit après le pool (le prix retourne souvent juste avant) ; placer son stop pile au niveau du pool.
- **Pièges** — Deux pools proches : le prix prend le premier, provoque une réaction, puis va chercher le second. La patience coûte moins cher que la réentrée.
- **Exemple concret** — Objectif fixé à 2 349,50 $ alors que les EQH sont à 2 350 : sortie garantie avant le retournement.

```schema
   ═══ 2 350 $ ═══ pool (chiffre rond + equal highs)
       2 349,5 ← objectif : juste avant
   ────────────────────
       prix
   ────────────────────
       2 331   ← stop : au-delà du pool inférieur (2 333)
```

::: memo
➡ Objectif avant le pool ➡ Stop après le pool ➡ Jamais dedans
:::

### LIQUIDITY SWEEP (PURGE DE LIQUIDITÉ)
*Balayage rapide d'un pool d'ordres suivi d'un retournement.*

- **Définition simple** — Le prix va chercher les stops, les prend, et repart dans l'autre sens.
- **Définition pro** — Extension brève au-delà d'un extrême, sans acceptation, déclenchant les ordres stop qui fournissent la contrepartie à une exécution institutionnelle inverse. Synonymes : *stop hunt*, *raid*, *turtle soup*, *SFP*.
- **Pourquoi c'est important** — C'est le signal de retournement le plus fiable du trading moderne, à condition d'être suivi d'un changement de structure.
- **Comment le reconnaître** — Mèche au-delà d'un creux ou d'un sommet évident, retour rapide dans le range, volume élevé, puis CHoCH sur l'unité inférieure.
- **Comment les institutions l'utilisent** — C'est le mécanisme même de leur remplissage : sans stops déclenchés, pas de volume disponible pour construire une position importante.
- **Comment je dois l'utiliser** — Séquence en trois temps : (1) purge d'un pool, (2) CHoCH en LTF, (3) entrée au retour dans le FVG ou l'OB, stop au-delà de la mèche de purge.
- **Erreurs fréquentes** — Entrer dès la mèche, sans confirmation de structure ; confondre purge et vraie cassure (la différence est l'acceptation : temps passé au-delà et clôtures).
- **Pièges** — La purge peut se produire deux fois de suite, la seconde étant plus profonde. D'où le stop placé au-delà de la mèche, avec une marge.
- **Exemple concret** — Plus bas de la veille à 17 950 sur le DAX. À 09 h 12, mèche à 17 932, retour à 17 980 en dix minutes, CHoCH haussier, puis 150 points de hausse.

```schema
   ────────────────── plus bas de la veille (SSL)
          │
          ▼ mèche de purge  ← les stops sautent
          ╲__╱ retour immédiat
              ╱╲__ CHoCH ──► entrée au FVG
   1 purge · 2 CHoCH · 3 entrée
```

::: memo
➡ Purge ➡ CHoCH ➡ Entrée ➡ Trois étapes, jamais deux
:::

### LIQUIDITY VOID
*Zone traversée à très grande vitesse, presque sans échange.*

- **Définition simple** — Un vide dans le prix, laissé par un mouvement éclair.
- **Définition pro** — Segment de prix parcouru en une ou deux bougies avec peu de volume négocié : la découverte de prix y a été inexistante, ce qui laisse une forte probabilité de retour ultérieur pour compléter l'échange.
- **Pourquoi c'est important** — Ces vides constituent des zones de retour rapides et des objectifs de correction très lisibles.
- **Comment le reconnaître** — Grande bougie unique, quasi sans mèches ; sur profil de volume, zone sans épaisseur (*low volume node*).
- **Comment les institutions l'utilisent** — Un vide est un déséquilibre d'inventaire : les teneurs de marché cherchent à y revenir pour se rééquilibrer.
- **Comment je dois l'utiliser** — Objectif de retracement, ou zone à traverser rapidement (le prix y accélère : ne pas y placer un objectif intermédiaire).
- **Erreurs fréquentes** — Placer un objectif au milieu d'un vide (le prix le franchit sans s'arrêter, ou n'y arrive jamais) ; confondre vide et FVG (le FVG est une définition en trois bougies, le vide est une notion de volume).
- **Pièges** — Le prix traverse les vides très vite dans les deux sens : le stop placé dans un vide est touché par simple vitesse.
- **Exemple concret** — À l'annonce du NFP, le prix parcourt 60 points en une bougie M1. Deux heures plus tard, il revient combler 45 de ces 60 points.

```schema
   Profil de volume
   ████████  zone dense (nœud) ← le prix ralentit
   █
   ▏         VIDE              ← le prix accélère
   █
   ████████  zone dense        ← le prix ralentit
```

::: memo
➡ Vide de volume ➡ Le prix y accélère ➡ Ni objectif ni stop à l'intérieur
:::

### LOT / TAILLE DE POSITION
*Quantité engagée sur un trade.*

- **Définition simple** — Combien vous achetez ou vendez.
- **Définition pro** — Unité standardisée (1 lot = 100 000 unités de devise de base sur le Forex ; mini 0,1 ; micro 0,01). La taille correcte n'est jamais choisie : elle est **calculée** à partir du risque et de la distance au stop.
- **Pourquoi c'est important** — C'est le seul paramètre qui relie l'analyse au compte. Une bonne analyse avec une mauvaise taille donne un mauvais résultat.
- **Comment le reconnaître** — Se calcule avant chaque entrée : `taille = (capital × risque %) / (distance au stop × valeur du point)`.
- **Comment les institutions l'utilisent** — La taille est imposée par les limites de risque, jamais par la conviction du trader.
- **Comment je dois l'utiliser** — Je fixe d'abord le stop technique, ensuite je calcule la taille. Jamais l'inverse. Un stop large impose une petite taille, pas un stop plus serré.
- **Erreurs fréquentes** — Choisir une taille ronde et adapter le stop pour « que ça rentre » ; augmenter la taille par conviction ou pour se refaire.
- **Pièges** — Doubler la taille double le stress, pas les compétences : au-delà d'un certain montant, l'exécution se dégrade et le plan n'est plus respecté.
- **Exemple concret** — Capital 10 000 €, risque 1 % = 100 €, stop 25 pips, valeur du pip 10 €/lot : `taille = 100 / (25 × 10) = 0,4 lot`.

```schema
   1. Stop technique      : 25 pips (sous l'Order Block)
   2. Risque autorisé     : 1 % de 10 000 € = 100 €
   3. Valeur du pip       : 10 € par lot
   4. TAILLE = 100 / (25 × 10) = 0,40 lot
   ── la taille est un résultat, jamais une décision ──
```

::: memo
➡ Stop d'abord ➡ Risque ensuite ➡ La taille se calcule ➡ Elle ne se choisit pas
:::

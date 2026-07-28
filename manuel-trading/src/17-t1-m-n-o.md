## M — MACROÉCONOMIE → MSS

### MACROÉCONOMIE
*Étude des grandeurs globales : croissance, inflation, emploi, taux, monnaie.*

- **Définition simple** — Ce qui se passe dans l'économie entière, et qui fait bouger tous les marchés en même temps.
- **Définition pro** — Cadre d'analyse des cycles (expansion, ralentissement, récession, reprise) et des politiques monétaire et budgétaire, dont découle la valorisation relative des classes d'actifs.
- **Pourquoi c'est important** — Elle explique pourquoi tous les actifs bougent parfois ensemble : ils sont tous actualisés au même taux sans risque.
- **Comment le reconnaître** — Calendrier économique, courbe des taux, indicateurs avancés (PMI), politiques des banques centrales. Voir le Tome 3 pour le détail.
- **Comment les institutions l'utilisent** — Le biais macro est la première ligne du processus : allocation entre actions, obligations, matières premières et liquidités.
- **Comment je dois l'utiliser** — Une revue par semaine : où en est l'inflation, que fait la FED, comment se comporte le dollar, où en sont les taux réels. Cette page suffit à cadrer le mois.
- **Erreurs fréquentes** — Trader la macro en intraday sans niveau technique ; croire qu'un « bon » chiffre est haussier indépendamment du consensus.
- **Pièges** — Le marché valorise les anticipations : quand la nouvelle arrive, le mouvement est souvent terminé.
- **Exemple concret** — La FED annonce une pause : l'or monte car les taux réels attendus baissent, le dollar recule, les indices s'apprécient. Un seul événement, quatre marchés.

```schema
   Croissance ↑ + Inflation ↑  ──► matières premières, cycliques
   Croissance ↑ + Inflation ↓  ──► actions (scénario idéal)
   Croissance ↓ + Inflation ↑  ──► or, liquidités (stagflation)
   Croissance ↓ + Inflation ↓  ──► obligations, défensives
```

::: memo
➡ Quatre quadrants ➡ Croissance et inflation ➡ Tout le reste en découle
:::

### MARGE / APPEL DE MARGE
*Dépôt de garantie exigé pour tenir une position à effet de levier.*

- **Définition simple** — L'argent bloqué pour garantir votre position, et le message qui vous prévient qu'il n'y en a plus assez.
- **Définition pro** — Marge initiale (à l'ouverture) et marge de maintien (pour tenir) ; sous le seuil, le courtier exige un dépôt ou liquide la position (*margin call*, puis *stop out*).
- **Pourquoi c'est important** — La marge détermine votre capacité de survie face à un mouvement adverse, indépendamment de la justesse de votre analyse.
- **Comment le reconnaître** — Indicateur « niveau de marge » dans la plateforme, exprimé en pourcentage.
- **Comment les institutions l'utilisent** — Gestion du collatéral et suivi permanent ; un appel de marge institutionnel force des ventes qui, elles-mêmes, alimentent les mouvements de marché.
- **Comment je dois l'utiliser** — Je maintiens un niveau de marge très supérieur au minimum : si mon stop est touché, la perte doit être une fraction du capital, jamais un problème de marge.
- **Erreurs fréquentes** — Utiliser la marge disponible comme mesure de ce qu'on « peut » risquer ; ajouter des fonds pour tenir une position perdante.
- **Pièges** — En cas de gap de week-end, la perte peut dépasser la marge : sans protection contre solde négatif, la dette est réelle.
- **Exemple concret** — Compte de 5 000 €, positions engageant 4 200 € de marge : un mouvement adverse de 1 % déclenche le stop out avant même le stop technique.

```schema
   Marge utilisée ████████████░░  ← danger
   Marge utilisée ███░░░░░░░░░░░  ← sain
   Règle : la marge n'est jamais le critère de taille — le risque l'est
```

::: memo
➡ Garantie bloquée ➡ Trop de marge = liquidation avant le stop ➡ Rester très en dessous
:::

### MARKET MAKER (TENEUR DE MARCHÉ)
*Acteur qui affiche en permanence un prix à l'achat et à la vente.*

- **Définition simple** — Celui qui vous vend quand vous achetez et vous achète quand vous vendez.
- **Définition pro** — Intervenant fournissant de la liquidité contre le spread, gérant un inventaire qu'il doit couvrir. Son intérêt est la rotation, pas la direction : il cherche à revenir à l'équilibre.
- **Pourquoi c'est important** — Sa gestion d'inventaire explique de nombreux retours vers la moyenne et l'attraction du prix vers les zones denses.
- **Comment le reconnaître** — Prix qui revient systématiquement vers une zone d'équilibre, absorption sur les extrêmes, spreads qui s'élargissent quand l'inventaire devient risqué.
- **Comment les institutions l'utilisent** — Les banques et les sociétés spécialisées tiennent le marché sur devises, options et actions ; les *dealers* d'options couvrent leur delta, ce qui crée des flux mécaniques autour des grands strikes.
- **Comment je dois l'utiliser** — Comme modèle mental : le marché a un « inventaire » à écouler, il doit donc aller chercher la contrepartie. Cela explique les purges et les retours.
- **Erreurs fréquentes** — Croire que le courtier « voit votre stop et vient le chercher » : sur les marchés profonds, la liquidité est collective, pas personnelle.
- **Pièges** — Chez certains courtiers de type *dealing desk*, le conflit d'intérêts est réel. C'est un argument pour choisir un courtier régulé, pas pour justifier ses pertes.
- **Exemple concret** — Sur expiration d'options, le prix converge vers le strike où l'exposition des teneurs de marché est maximale (*max pain*) : la gestion de leur couverture crée un aimant.

```schema
   Vous achetez  ──► quelqu'un doit vendre  ──► inventaire du teneur ↓
   Il doit se rééquilibrer ──► il fait revenir le prix ──► retour à la moyenne
```

::: memo
➡ Il vit du spread ➡ Il gère un stock ➡ Il ramène le prix vers l'équilibre
:::

### MARKET STRUCTURE (STRUCTURE DE MARCHÉ)
*Organisation des sommets et des creux qui définit la tendance.*

- **Définition simple** — La forme du graphique : ça monte, ça baisse, ou ça va de côté.
- **Définition pro** — Séquence de pivots (HH/HL, LH/LL) définissant la direction et fournissant les niveaux d'invalidation. Base commune à la théorie de Dow, à Wyckoff et au SMC.
- **Pourquoi c'est important** — C'est la première chose à lire sur un graphique, et la seule qui donne un cadre objectif à toutes les autres décisions.
- **Comment le reconnaître** — Marquage des pivots majeurs sur l'unité de temps choisie, en ignorant le bruit intermédiaire.
- **Comment les institutions l'utilisent** — Les niveaux de structure sont les points de concentration des stops, donc de la liquidité : la structure est simultanément la carte de la tendance et la carte des ordres.
- **Comment je dois l'utiliser** — Trois questions : quelle est la tendance HTF ? où est le dernier point d'invalidation ? où est la liquidité non prise ? Puis seulement, chercher une entrée.
- **Erreurs fréquentes** — Redessiner la structure après coup ; marquer trop de pivots (structure illisible) ou trop peu (retards) ; ignorer la structure HTF au profit d'un signal LTF.
- **Pièges** — Une structure cassée en mèche n'est pas cassée : l'acceptation (clôtures au-delà) fait la différence entre purge et retournement.
- **Exemple concret** — Sur H4, HH/HL depuis dix jours : toute vente est un pari contre la structure. Le premier CHoCH H4 change le cadre, pas avant.

```schema
   HAUSSIÈRE   HH ── HL ── HH ── HL      achats uniquement
   BAISSIÈRE   LH ── LL ── LH ── LL      ventes uniquement
   NEUTRE      chevauchements             rien, ou bords de range
```

::: memo
➡ Marquer la structure d'abord ➡ Tendance, invalidation, liquidité ➡ Ensuite seulement, entrer
:::

### MÈCHE (WICK / SHADOW)
*Extrémité fine d'une bougie, au-delà du corps.*

- **Définition simple** — La partie du mouvement qui a été refusée.
- **Définition pro** — Segment entre le corps (ouverture-clôture) et l'extrême de la période : matérialise une zone où le prix a été négocié puis rejeté, souvent une prise de liquidité.
- **Pourquoi c'est important** — La mèche indique où sont allés les ordres. Une longue mèche à un niveau clé est le signal le plus lisible d'une purge réussie.
- **Comment le reconnaître** — Mèche longue par rapport au corps, à un extrême de structure, avec volume élevé.
- **Comment les institutions l'utilisent** — Elles créent la mèche : le déclenchement des stops puis le retour instantané est la signature d'une exécution absorbée.
- **Comment je dois l'utiliser** — Stop toujours **au-delà** de la mèche, jamais au niveau du corps ; et lecture de la mèche comme confirmation de purge.
- **Erreurs fréquentes** — Placer un stop au niveau de la clôture ; ignorer les mèches lors du marquage de structure (une mèche prend la liquidité tout autant qu'une clôture).
- **Pièges** — Selon le courtier, la mèche diffère de quelques points sur le Forex : un stop calculé à un point près est aléatoire.
- **Exemple concret** — Mèche de 22 points sous le plus bas de la veille, clôture 15 points au-dessus : purge caractérisée, achat sur le retour au FVG.

```schema
        │  ← rejet des acheteurs (offre)
      ┌─┴─┐
      │███│
      └─┬─┘
        │  ← rejet des vendeurs (demande) : la liquidité a été prise ici
   stop toujours au-delà de cette pointe
```

::: memo
➡ La mèche montre le refus ➡ Elle marque la purge ➡ Le stop se place au-delà
:::

### MITIGATION BLOCK
*Zone où une position institutionnelle en perte est ramenée à l'équilibre.*

- **Définition simple** — L'endroit où les gros sortent de leur mauvaise position sans perte.
- **Définition pro** — Dernier bloc d'ordres avant un mouvement contraire, retesté ultérieurement pour permettre la « mitigation » (réduction ou sortie à l'équilibre) des positions engagées au mauvais prix. À la différence du *breaker*, la structure opposée n'a pas été cassée.
- **Pourquoi c'est important** — Il explique des rejets nets à des niveaux sans support ni résistance apparents.
- **Comment le reconnaître** — Dans une tendance baissière : dernier bloc haussier avant l'impulsion baissière, retesté sans que le sommet précédent n'ait été cassé.
- **Comment les institutions l'utilisent** — Une position mal engagée n'est pas coupée mais gérée : elle est réduite au retour du prix, ce qui alimente le mouvement opposé.
- **Comment je dois l'utiliser** — En tendance, comme zone de continuation : je vends le retour dans le mitigation block, stop au-dessus du bloc, objectif sur la liquidité inférieure.
- **Erreurs fréquentes** — Confondre avec le *breaker* (qui suppose une cassure de structure) ; trader un mitigation block à contre-tendance.
- **Pièges** — Un mitigation block traversé signifie que le déséquilibre a changé de camp : il faut alors relire toute la structure.
- **Exemple concret** — En tendance baissière H1, le prix remonte dans la dernière bougie haussière avant la chute : rejet immédiat, poursuite de la baisse.

```schema
   ▓▓▓ mitigation block (dernier bloc haussier)
      ╲
        ╲▼▼▼  impulsion baissière
             ╱  retour dans le bloc ▓▓▓ ──► vente
                ╲▼▼▼  continuation
```

::: memo
➡ Retour au point de départ ➡ Sortie à l'équilibre des gros ➡ Continuation
:::

### MOMENTUM
*Vitesse et force du mouvement en cours.*

- **Définition simple** — À quelle allure ça bouge.
- **Définition pro** — Mesure de la variation du prix sur une fenêtre donnée (ROC, RSI, MACD) ; en gestion, facteur de performance documenté : les actifs qui montent tendent à continuer à court-moyen terme.
- **Pourquoi c'est important** — Le momentum distingue une impulsion (à suivre) d'une correction (à laisser passer), notamment via la taille des corps de bougie.
- **Comment le reconnaître** — Corps larges et mèches courtes dans le sens du mouvement ; retracements peu profonds ; indicateurs de momentum en zone extrême maintenue.
- **Comment les institutions l'utilisent** — Fonds *trend following* et CTA achètent la force et vendent la faiblesse, ce qui amplifie les tendances établies.
- **Comment je dois l'utiliser** — Comme filtre de qualité du déplacement : impulsion = bougies larges ; correction = bougies étroites et chevauchantes. J'entre dans le sens des impulsions.
- **Erreurs fréquentes** — Croire qu'un RSI à 80 signifie « trop haut » : en tendance forte, il y reste des semaines ; vendre la force par principe.
- **Pièges** — Le momentum s'inverse brutalement aux extrêmes de sentiment : les plus fortes hausses journalières se produisent en marché baissier.
- **Exemple concret** — Trois bougies H1 à corps pleins de 40, 45 et 38 points contre des corrections de 10 points : l'impulsion domine, on achète les creux.

```schema
   IMPULSION   ███ ███ ███   corps larges, retracements courts
   CORRECTION  ▪▪ ▪ ▪▪ ▪     corps étroits, chevauchements
   ── on entre dans le sens des impulsions, pas des corrections ──
```

::: memo
➡ Corps larges = impulsion ➡ Corps étroits = correction ➡ Suivre l'impulsion
:::

### MOYENNE MOBILE
*Prix moyen sur les N dernières périodes, recalculé en continu.*

- **Définition simple** — Une ligne qui lisse le prix.
- **Définition pro** — Simple (SMA), exponentielle (EMA, plus réactive) ou pondérée. Les plus suivies : 20, 50, 100, 200 périodes. La MM200 journalière sert de référence institutionnelle de régime.
- **Pourquoi c'est important** — Elle donne un repère de tendance objectif et un niveau dynamique réellement observé par un grand nombre d'acteurs.
- **Comment le reconnaître** — Ligne sur le graphique ; pente = direction, distance = tension.
- **Comment les institutions l'utilisent** — Les algorithmes d'exécution visent le VWAP plus que les moyennes mobiles, mais la MM200 reste un repère de communication et de gestion du risque très largement partagé.
- **Comment je dois l'utiliser** — Une seule, comme filtre de régime : au-dessus de la MM200 journalière, je privilégie les achats ; en dessous, les ventes. Rien de plus.
- **Erreurs fréquentes** — Trader les croisements de moyennes (signal tardif par construction) ; superposer trois moyennes en croyant multiplier l'information.
- **Pièges** — En range, la moyenne est traversée en permanence et produit des signaux contradictoires en série.
- **Exemple concret** — Prix sous la MM200 journalière : les rebonds vers la moyenne sont vendus tant que la structure hebdomadaire reste baissière.

```schema
   Prix > MM200 ─────────────► biais acheteur
   ═══════════ MM200 ═══════════
   Prix < MM200 ─────────────► biais vendeur
   ── un seul usage : filtrer, jamais déclencher ──
```

::: memo
➡ Un filtre de régime ➡ Une seule moyenne ➡ Jamais un signal d'entrée
:::

### MSS — MARKET STRUCTURE SHIFT
*Changement de structure majeur, confirmant un retournement de tendance.*

- **Définition simple** — La structure vient de changer de camp, pour de bon.
- **Définition pro** — Cassure, avec déplacement, du dernier pivot contraire sur une unité de temps significative, généralement précédée d'une prise de liquidité. Souvent employé comme synonyme fort de CHoCH, réservé aux unités supérieures ou aux cassures accompagnées d'un FVG.
- **Pourquoi c'est important** — C'est la validation qui autorise à changer de biais directionnel, et donc à retourner sa lecture de la journée ou de la semaine.
- **Comment le reconnaître** — Purge d'un extrême, puis bougie d'expansion qui clôture au-delà du dernier pivot opposé, laissant un FVG derrière elle.
- **Comment les institutions l'utilisent** — Le MSS est la trace de l'entrée d'un flux important : la vitesse du déplacement témoigne d'une exécution agressive.
- **Comment je dois l'utiliser** — MSS en H1/H4 = nouveau biais. Entrée sur le retour dans le FVG ou l'OB à l'origine du déplacement, stop au-delà de l'extrême purgé.
- **Erreurs fréquentes** — Accepter un MSS sans déplacement ; l'appliquer sur M1 et croire à un retournement de tendance journalière.
- **Pièges** — Un MSS suivi immédiatement d'un retour au-delà de l'extrême purgé est un piège : le stop doit se placer au-delà de la mèche, avec de la marge.
- **Exemple concret** — Or H1 : purge des EQH à 2 362, puis bougie de 14 $ qui clôture sous le dernier HL à 2 338. MSS confirmé : biais baissier jusqu'au prochain signal.

```schema
   purge ▲
        ╱╲
      ╱   ╲        ███ déplacement + FVG
    ╱      HL ─────────────────────  cassure en clôture = MSS
                        ╲▼ nouveau biais baissier
```

::: memo
➡ Purge ➡ Déplacement ➡ Cassure du dernier pivot ➡ Nouveau biais
:::

## N — NFP → NIVEAU PSYCHOLOGIQUE

### NFP — NON-FARM PAYROLLS
*Créations d'emplois non agricoles aux États-Unis.*

- **Définition simple** — Le nombre d'emplois créés le mois dernier aux États-Unis.
- **Définition pro** — Publié le premier vendredi du mois à 14 h 30 heure de Paris, accompagné du taux de chômage et du salaire horaire moyen — ce dernier étant souvent plus déterminant que le chiffre principal, car il alimente l'inflation.
- **Pourquoi c'est important** — C'est l'un des trois événements les plus volatils du mois : il conditionne les anticipations de taux, donc le dollar, l'or et les indices.
- **Comment le reconnaître** — Calendrier économique ; révisions des mois précédents à surveiller autant que le chiffre du mois.
- **Comment les institutions l'utilisent** — Elles comparent au consensus et aux indicateurs avancés (ADP, inscriptions hebdomadaires) ; la réaction dépend du régime : en surchauffe, un bon chiffre est mauvais pour les actions ; en récession, il est bon.
- **Comment je dois l'utiliser** — Aucune position avant 14 h 30. J'observe la première demi-heure, puis je trade le retour dans le FVG créé par l'expansion, avec une taille réduite.
- **Erreurs fréquentes** — Entrer à 14 h 29 ; laisser un stop serré dans une position ouverte ; trader la première bougie M1.
- **Pièges** — Réaction initiale fréquemment inversée dans les dix minutes ; spreads multipliés par cinq à dix ; slippage garanti sur les stops.
- **Exemple concret** — NFP à 310 k contre 180 k attendus, mais salaires en dessous des attentes : le dollar monte puis efface tout en vingt minutes, l'or termine en hausse.

```schema
   14 h 30  ██████ pic de volatilité, spreads ×5
   14 h 45  ▼▼▼▼   inversion fréquente
   15 h 00  ─────   direction réelle, FVG exploitable
   ── on n'entre jamais avant 15 h ──
```

::: memo
➡ Premier vendredi ➡ 14 h 30 ➡ Regarder les salaires ➡ Trader après, jamais pendant
:::

### NIVEAU PSYCHOLOGIQUE (CHIFFRE ROND)
*Prix rond sur lequel se concentrent naturellement les ordres.*

- **Définition simple** — Les nombres ronds attirent les ordres : 1,1000 ; 2 000 $ ; 20 000 points.
- **Définition pro** — Concentration d'ordres limite, d'options à strike rond et de stops due à un biais cognitif d'ancrage ; ces niveaux sont donc de véritables pools de liquidité, indépendamment de toute analyse.
- **Pourquoi c'est important** — Ils fonctionnent parce qu'ils sont utilisés : c'est une prophétie autoréalisatrice mesurable.
- **Comment le reconnaître** — Milliers ronds sur les indices, centaines sur l'or, 00 et 50 sur les paires Forex.
- **Comment les institutions l'utilisent** — Les barrières d'options se placent sur les chiffres ronds : les teneurs de marché défendent ces niveaux jusqu'à l'expiration, puis les laissent céder.
- **Comment je dois l'utiliser** — Je ne place jamais un stop juste au-delà d'un chiffre rond, et je vise systématiquement le chiffre rond comme objectif partiel.
- **Erreurs fréquentes** — Placer un objectif exactement sur le chiffre rond (le prix retourne souvent quelques points avant) ; croire qu'un chiffre rond est une résistance solide.
- **Pièges** — Le prix dépasse presque toujours légèrement le niveau rond pour prendre les stops avant de retourner : c'est le piège de la « résistance psychologique ».
- **Exemple concret** — L'or bute sur 2 000 $ pendant six séances, mèche à 2 006 $, puis retour à 1 960 $.

```schema
   2 006 ▲ purge des stops
   2 000 ══════════════════  chiffre rond (barrière d'options)
   1 998 ← objectif : juste avant
   ── viser avant, protéger après ──
```

::: memo
➡ Les ronds attirent les ordres ➡ Objectif avant ➡ Stop bien au-delà
:::

## O — OHLC → OVERTRADING

### OHLC
*Ouverture, plus haut, plus bas, clôture d'une période.*

- **Définition simple** — Les quatre prix qui résument une bougie.
- **Définition pro** — *Open, High, Low, Close* : l'ouverture donne le point de départ du consensus, la clôture le point d'arrivée (la plus importante), les extrêmes les zones testées.
- **Pourquoi c'est important** — Ces quatre prix, notamment ceux de la veille (PDH/PDL) et de la semaine, sont des références permanentes pour tous les acteurs.
- **Comment le reconnaître** — Se tracent en lignes horizontales : plus haut/plus bas de la veille, clôture de la veille, ouverture journalière, hebdomadaire, mensuelle.
- **Comment les institutions l'utilisent** — La clôture est la référence de valorisation des portefeuilles, ce qui crée des flux réels à l'approche de la fin de séance ; l'ouverture sert de repère de performance intraday.
- **Comment je dois l'utiliser** — Je trace quatre lignes chaque matin : plus haut et plus bas de la veille, clôture de la veille, ouverture du jour. Ce sont mes premières cibles et mes premiers repères de biais.
- **Erreurs fréquentes** — Surcharger le graphique de dizaines de niveaux ; oublier que ces niveaux dépendent du fuseau horaire du courtier.
- **Pièges** — Le plus haut et le plus bas de la veille sont des pools de liquidité évidents : ils seront visités avant tout mouvement de fond.
- **Exemple concret** — Le prix ouvre sous la clôture de la veille, revient la tester, la rejette, puis va chercher le plus bas de la veille : la journée entière tient dans ces trois lignes.

```schema
   ───────── PDH (plus haut de la veille)  ← liquidité acheteuse
   ───────── clôture de la veille          ← repère de biais
   ───────── ouverture du jour             ← repère de performance
   ───────── PDL (plus bas de la veille)   ← liquidité vendeuse
```

::: memo
➡ Quatre lignes ➡ Chaque matin ➡ Cibles et repères ➡ Rien de plus
:::

### OPEN INTEREST
*Nombre de contrats dérivés ouverts et non encore dénoués.*

- **Définition simple** — Combien de paris sont encore en cours sur le marché.
- **Définition pro** — Total des positions ouvertes sur un contrat à terme ou perpétuel. Combiné au prix et au volume, il indique si un mouvement crée de nouvelles positions ou en liquide d'anciennes.
- **Pourquoi c'est important** — Prix en hausse et open interest en hausse = argent frais, tendance saine. Prix en hausse et open interest en baisse = rachat de vendeurs, mouvement fragile.
- **Comment le reconnaître** — Donnée publiée par les places de futures et par les plateformes crypto ; indicateur disponible sur la plupart des graphiques de futures.
- **Comment les institutions l'utilisent** — Analyse de positionnement via l'open interest et les rapports COT : savoir qui est déjà positionné indique qui devra sortir.
- **Comment je dois l'utiliser** — Comme filtre de qualité de tendance et détecteur de risque de purge : open interest record + funding extrême = configuration de liquidation.
- **Erreurs fréquentes** — Confondre volume (activité de la période) et open interest (stock de positions) ; l'utiliser seul comme signal.
- **Pièges** — Un open interest en forte hausse près d'un extrême est un carburant : plus il y a de positions, plus la purge sera violente.
- **Exemple concret** — Bitcoin à 62 000 $, open interest au plus haut historique, funding à 0,12 % : la baisse de 3 % qui suit liquide 700 millions de dollars et accélère jusqu'à −6 %.

```schema
   Prix ↑ · OI ↑  ──► nouvelles positions longues : tendance saine
   Prix ↑ · OI ↓  ──► rachats de shorts : mouvement fragile
   Prix ↓ · OI ↑  ──► nouvelles positions courtes : baisse assumée
   Prix ↓ · OI ↓  ──► liquidation de longs : capitulation
```

::: memo
➡ Stock de positions ➡ Croisé avec le prix ➡ Il dit si le mouvement est solide
:::

### ORDER BLOCK (OB)
*Dernière bougie opposée avant un déplacement fort : trace d'une exécution institutionnelle.*

- **Définition simple** — La dernière bougie baissière avant une grosse hausse (ou l'inverse). Le prix y revient souvent.
- **Définition pro** — Zone d'accumulation ou de distribution d'ordres à l'origine d'un déséquilibre. Un OB valide exige trois conditions : une prise de liquidité avant, un déplacement après (avec FVG), et une cassure de structure.
- **Pourquoi c'est important** — C'est la zone d'entrée de référence du SMC : elle offre un point précis, une invalidation courte et un ratio risque/rendement élevé.
- **Comment le reconnaître** — Dernière bougie de sens opposé avant l'impulsion ; on retient la zone corps-mèche (ou seulement le corps pour un OB « affiné »).
- **Comment les institutions l'utilisent** — L'OB matérialise le prix moyen d'une exécution partielle : le retour permet de compléter la position au même prix, d'où la réaction.
- **Comment je dois l'utiliser** — Ordre limite à l'entrée de la zone, stop au-delà de la bougie d'origine, objectif sur la liquidité opposée. Uniquement dans le sens du biais HTF et seulement si l'inducement a été pris.
- **Erreurs fréquentes** — Marquer un OB sans déplacement ni prise de liquidité (n'importe quelle bougie devient alors un OB) ; utiliser un OB déjà testé (il perd sa valeur après la première mitigation).
- **Pièges** — Les OB évidents en LTF sont innombrables : sans hiérarchie HTF, on trouve un OB tous les dix points et on trade sans arrêt.
- **Exemple concret** — Sur H1, purge du plus bas de la veille, puis trois bougies haussières de 30 points. La dernière bougie baissière avant l'impulsion (1,0842–1,0850) est l'OB : achat limite à 1,0850, stop à 1,0838.

```schema
   ┌──┐ ← Order Block (dernière bougie baissière)
   │▓▓│         ███
   └──┘     ███ ███  ← déplacement + FVG
     ╲   ███
      ▼ purge de liquidité
   Retour dans ▓▓ ──► entrée limite · stop sous la mèche de l'OB
```

::: memo
➡ Purge ➡ Dernière bougie opposée ➡ Déplacement ➡ Retour = entrée
:::

### ORDER FLOW
*Analyse des ordres réellement exécutés, et de leur agressivité.*

- **Définition simple** — Regarder qui achète et qui vend, en temps réel.
- **Définition pro** — Lecture du carnet, du *footprint* (volume au bid/ask par prix), du delta cumulé et des *time and sales*. Permet d'identifier absorption, initiative et épuisement au niveau du prix.
- **Pourquoi c'est important** — C'est l'information la plus proche de la vérité : ni indicateur retardé ni interprétation, seulement des transactions.
- **Comment le reconnaître** — Nécessite des données de marché centralisées (futures, actions) : le Forex au comptant n'en dispose pas.
- **Comment les institutions l'utilisent** — Les traders de flux exécutent en fonction de l'absorption observée ; c'est le cœur du métier sur les desks à court terme.
- **Comment je dois l'utiliser** — En complément aux niveaux : si mon OB coïncide avec une absorption visible en footprint, la probabilité augmente sensiblement. En SMC pur, la lecture des mèches et du volume en est le substitut appauvri.
- **Erreurs fréquentes** — Vouloir faire de l'order flow sur le Forex de détail avec des volumes « tick » ; lire le flux sans niveau de référence (on se noie dans le détail).
- **Pièges** — Le carnet est manipulable (*spoofing* : ordres affichés puis retirés) ; seules les exécutions comptent, pas les intentions affichées.
- **Exemple concret** — Sur le future S&P, à 4 500, le footprint montre 3 000 contrats vendus au bid sans que le prix ne baisse : un acheteur absorbe. Le rebond suit.

```schema
   Prix    Bid × Ask
   4 501   120 × 340
   4 500   3 000 × 210   ← agressivité vendeuse absorbée : prix immobile
   4 499   180 × 260
   ➜ quelqu'un achète tout : signal haussier
```

::: memo
➡ Les vraies transactions ➡ Absorption ➡ Complément des niveaux, pas remplacement
:::

### OTE — OPTIMAL TRADE ENTRY
*Zone d'entrée optimale d'un retracement, entre 62 % et 79 %.*

- **Définition simple** — L'endroit le moins cher pour entrer dans une tendance, sans la rater.
- **Définition pro** — Plage de retracement Fibonacci 0,618–0,79 du dernier segment impulsif, offrant le meilleur compromis entre profondeur de correction et probabilité de reprise ; elle situe l'entrée en discount profond tout en gardant une invalidation courte.
- **Pourquoi c'est important** — Elle transforme « acheter bas » en règle mesurable, et permet des ratios de 1:3 ou davantage sur des mouvements ordinaires.
- **Comment le reconnaître** — Grille Fibonacci tracée sur la dernière impulsion ; l'OTE coïncide fréquemment avec un OB ou un FVG.
- **Comment les institutions l'utilisent** — C'est la zone où un vendeur de correction rencontre un acheteur institutionnel : le rapport de force s'y inverse.
- **Comment je dois l'utiliser** — Ordre limite dans la zone 0,618–0,79 **uniquement** si elle coïncide avec un OB ou un FVG, et si l'inducement a été purgé. Stop sous le 1,0.
- **Erreurs fréquentes** — Entrer à 0,5 par impatience ; attendre 0,79 systématiquement et rater les tendances fortes qui ne corrigent qu'à 0,382.
- **Pièges** — En tendance très puissante, l'OTE n'est jamais atteint. La solution : diviser l'entrée en deux, une partie au FVG, une partie en OTE.
- **Exemple concret** — Impulsion de 17 900 à 18 100 sur le DAX. OTE : 18 024–17 942. Un OB H1 à 18 010 s'y trouve : achat à 18 010, stop 17 890, objectif 18 200 → 1:1,6 sur le premier objectif, 1:3 sur le second.

```schema
   1,0  ─────────── début de l'impulsion (invalidation)
   0,79 ┐
        ├─ ZONE OTE ──► entrée limite
   0,618┘
   0,5  ─────────── équilibre (trop cher)
   0    ─────────── sommet de l'impulsion
```

::: memo
➡ Retracement 62–79 % ➡ Avec OB ou FVG ➡ Après purge de l'inducement
:::

### OVERTRADING
*Prendre trop de positions, trop souvent, sans qualité.*

- **Définition simple** — Trader pour trader.
- **Définition pro** — Augmentation de la fréquence sans avantage statistique, généralement déclenchée par l'ennui, la volonté de se refaire ou l'excès de confiance. Multiplie les coûts et fait converger le résultat vers la somme des spreads.
- **Pourquoi c'est important** — C'est la première cause de perte des traders qui maîtrisent pourtant l'analyse : l'espérance positive d'un setup rare est détruite par des dizaines de trades médiocres.
- **Comment le reconnaître** — Dans le journal : plus de trades les jours de perte, positions hors setup, entrées hors Kill Zone, trades non notés.
- **Comment les institutions l'utilisent** — Elles ne le peuvent pas : les limites de risque et le contrôle hiérarchique l'interdisent structurellement.
- **Comment je dois l'utiliser** — Comme diagnostic : je fixe un nombre maximal de trades par jour (2 à 3) et par semaine (10). Le quota atteint, la plateforme se ferme.
- **Erreurs fréquentes** — Confondre activité et productivité ; croire que ne rien faire est une perte de temps alors que c'est une décision.
- **Pièges** — L'overtrading suit presque toujours une perte : le *revenge trading* est sa forme la plus destructrice, et il ne se ressent pas comme de l'overtrading sur le moment.
- **Exemple concret** — 14 trades le mardi après deux stops le matin : résultat −7 R, dont −5 R sur les onze trades hors plan.

```schema
   Trades/jour   Espérance moyenne
      1 – 2          +0,35 R    ← setups sélectionnés
      3 – 5          +0,05 R    ← dilution
      6 et +         −0,20 R    ← frais + fatigue + émotion
```

::: memo
➡ Quota quotidien ➡ Quota hebdomadaire ➡ Atteint = fermeture de la plateforme
:::

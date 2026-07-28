## T

### TAKE PROFIT (OBJECTIF)
*Prix auquel la position est fermée avec un gain.*

- **Définition simple** — L'endroit où vous décidez d'encaisser.
- **Définition pro** — Niveau de sortie défini par la structure (liquidité opposée, borne de range, déséquilibre à combler) et non par un montant souhaité ; il détermine, avec le stop, le ratio du trade.
- **Pourquoi c'est important** — Un objectif mal placé transforme une bonne entrée en trade médiocre. Le gain se décide au moment de l'analyse, pas sous la pression.
- **Comment le reconnaître** — Se place **juste avant** un pool de liquidité, un chiffre rond, un plus haut de la veille ou une zone HTF opposée.
- **Comment les institutions l'utilisent** — Elles sortent là où il y a de la contrepartie, donc dans la liquidité : elles vendent dans les achats déclenchés au-dessus des sommets.
- **Comment je dois l'utiliser** — Deux objectifs : le premier à 1:2 (sortie de la moitié, stop à l'équilibre), le second sur la liquidité HTF, laissé courir avec un stop suiveur.
- **Erreurs fréquentes** — Sortir dès que la position est en gain, par peur de la voir revenir ; déplacer l'objectif plus loin quand le prix s'en approche (cupidité) ; viser un chiffre rond exact.
- **Pièges** — Le prix retourne très fréquemment quelques points avant le niveau évident : viser 2 349,5 plutôt que 2 350 change la moitié des résultats.
- **Exemple concret** — Achat à 17 980, stop 17 930 (50 pts), premier objectif 18 080 (1:2, moitié soldée), second objectif 18 195 juste sous les EQH à 18 200.

```schema
   EQH 18 200 ══════════════  liquidité
   TP2 18 195 ─── juste avant
   TP1 18 080 ─── 1:2, moitié soldée + stop à l'équilibre
   Entrée 17 980
   Stop 17 930
```

::: memo
➡ Objectif sur la liquidité ➡ Juste avant ➡ Deux paliers ➡ Décidé à l'avance
:::

### TAUX DIRECTEUR
*Taux auquel la banque centrale prête aux banques commerciales.*

- **Définition simple** — Le prix officiel de l'argent.
- **Définition pro** — Instrument principal de politique monétaire (*Fed Funds*, taux de dépôt BCE) : il fixe le coût du financement à court terme et se diffuse à toute la structure des taux, donc à la valorisation de tous les actifs.
- **Pourquoi c'est important** — Toute valorisation est un flux futur actualisé : quand le taux monte, la valeur actuelle de tout baisse mécaniquement.
- **Comment le reconnaître** — Décisions des banques centrales, anticipations lisibles dans les futures de taux et les swaps.
- **Comment les institutions l'utilisent** — Elles ne tradent pas le niveau mais la **trajectoire anticipée** : ce qui compte est l'écart entre le message de la banque centrale et ce qui est déjà valorisé.
- **Comment je dois l'utiliser** — Comme cadre : cycle de hausse = dollar fort, pression sur l'or et les valeurs de croissance ; cycle de baisse = l'inverse, sauf si la baisse est motivée par une récession.
- **Erreurs fréquentes** — Réagir au niveau du taux plutôt qu'à la surprise ; croire qu'une baisse de taux est toujours haussière pour les actions.
- **Pièges** — Le marché valorise six à douze mois à l'avance : quand la décision tombe, le mouvement est souvent terminé.
- **Exemple concret** — Hausse de 25 points de base parfaitement anticipée : aucun mouvement. Une phrase du communiqué évoquant une pause : le dollar perd 1 %.

```schema
   Taux ↑  ──► actualisation ↑ ──► valorisations ↓ · DXY ↑ · Or ↓
   Taux ↓  ──► actualisation ↓ ──► valorisations ↑ · DXY ↓ · Or ↑
   ⚠ sauf si la baisse signale une récession : actions ↓ malgré tout
```

::: memo
➡ Le prix de l'argent ➡ Ce qui compte est la trajectoire ➡ Pas le niveau
:::

### TENDANCE
*Direction dominante du prix sur une échelle de temps donnée.*

- **Définition simple** — Ça monte, ça baisse, ou ça ne fait rien.
- **Définition pro** — Séquence de pivots ordonnés (HH/HL ou LH/LL) selon Dow ; elle existe simultanément à plusieurs échelles, ce qui impose de préciser l'unité de temps avant toute affirmation.
- **Pourquoi c'est important** — Trader dans le sens de la tendance HTF améliore mécaniquement le taux de réussite et la taille des mouvements captés.
- **Comment le reconnaître** — Marquage des pivots ; secondairement, position par rapport à la MM200 et régularité des retracements.
- **Comment les institutions l'utilisent** — Les fonds suiveurs de tendance amplifient les mouvements établis ; c'est une des raisons de la persistance des tendances.
- **Comment je dois l'utiliser** — Une seule règle : je ne prends que des trades dans le sens de la tendance de l'unité supérieure, jusqu'à son CHoCH.
- **Erreurs fréquentes** — Chercher à attraper le sommet ou le creux exact ; déclarer un retournement à chaque correction ; parler de « tendance » sans préciser l'unité de temps.
- **Pièges** — La tendance paraît la plus évidente juste avant son épuisement, quand tout le monde y est enfin convaincu.
- **Exemple concret** — D1 haussier, H1 baissier : les ventes H1 sont des trades contre-tendance à taille réduite, les achats H1 sur support D1 sont les trades principaux.

```schema
   D1  ▲ haussière   ──► trades principaux : achats
   H1  ▼ correction  ──► ventes tolérées, taille réduite, objectifs courts
   M5  ▲ signal      ──► exécution des achats sur zone H1
```

::: memo
➡ Toujours préciser l'unité de temps ➡ Suivre la supérieure ➡ Jusqu'au CHoCH
:::

### TEST (WYCKOFF)
*Retour sur un extrême pour vérifier l'absence d'offre ou de demande.*

- **Définition simple** — Le marché revient voir s'il reste des vendeurs (ou des acheteurs).
- **Définition pro** — Retour vers la zone d'un climax ou d'un spring, dont le **volume faible** signale l'épuisement de la pression opposée. C'est le second temps du couple « action / vérification ».
- **Pourquoi c'est important** — Le test offre une entrée bien meilleure que le climax lui-même, avec une invalidation courte et un risque réduit.
- **Comment le reconnaître** — Retour sur le niveau extrême, volume nettement inférieur au premier passage, mèche courte, absence de nouveau plus bas significatif.
- **Comment les institutions l'utilisent** — Elles vérifient que l'inventaire adverse est vide avant d'engager la phase de balisage : un test réussi autorise le mouvement.
- **Comment je dois l'utiliser** — J'entre au test, pas au climax ni au spring : volume faible = feu vert ; volume élevé = la pression persiste, on attend.
- **Erreurs fréquentes** — Entrer au climax (couteau qui tombe) ; ignorer le volume, qui est le seul élément qualifiant du test.
- **Pièges** — Un test à volume élevé qui casse le plus bas précédent annule le scénario : l'accumulation a échoué.
- **Exemple concret** — Spring à 1 798 sur volume record, test à 1 806 sur volume divisé par trois : achat, stop à 1 795.

```schema
   volume  ████ (spring)      ▂▂ (test)   ← volume faible = plus de vendeurs
   prix    ╲▼ 1 798        ╲▼ 1 806
                              ╱▲▲▲ départ haussier
```

::: memo
➡ Retour sur l'extrême ➡ Volume faible ➡ Feu vert ➡ On entre ici
:::

### TRAILING STOP (STOP SUIVEUR)
*Stop déplacé au fur et à mesure que la position devient gagnante.*

- **Définition simple** — Un stop qui suit le prix pour protéger les gains.
- **Définition pro** — Ajustement dynamique du niveau d'invalidation selon la structure (sous chaque nouveau HL) ou la volatilité (multiple d'ATR). Il transforme un objectif fixe en participation à la tendance.
- **Pourquoi c'est important** — C'est le seul moyen de capter les mouvements exceptionnels : sans stop suiveur, on sort systématiquement à 1:2 et on rate les 1:10.
- **Comment le reconnaître** — Se gère manuellement (structure) ou automatiquement (distance fixe, ATR).
- **Comment les institutions l'utilisent** — Les stratégies suiveuses de tendance reposent entièrement sur ce principe : quelques trades exceptionnels financent une majorité de petites pertes.
- **Comment je dois l'utiliser** — Sur la seconde moitié de position uniquement, calé sur la structure : je remonte le stop sous chaque nouveau HL confirmé, jamais entre deux.
- **Erreurs fréquentes** — Trailer trop serré (sortie dans le bruit du premier retracement) ; remonter le stop à chaque bougie ; l'appliquer sur la totalité de la position.
- **Pièges** — Le stop suiveur transforme souvent un gain en petite perte lorsqu'il est mal calibré : il doit rester au-delà du bruit (au minimum 1 ATR).
- **Exemple concret** — Achat à 100, stop initial 95. À 110, moitié soldée et stop à 100. À 120, stop remonté à 109 (sous le dernier HL). Sortie finale à 131 sur retournement.

```schema
   Entrée 100 · stop 95
   ├─ 110 : moitié soldée, stop → 100 (équilibre)
   ├─ 120 : stop → 109 (sous le HL)
   ├─ 130 : stop → 119
   └─ sortie 131  ──► gain conservé sans prédire le sommet
```

::: memo
➡ Sur la moitié restante ➡ Sous chaque nouveau creux ➡ Jamais dans le bruit
:::

### TRENDLINE (LIGNE DE TENDANCE)
*Droite reliant des creux ascendants ou des sommets descendants.*

- **Définition simple** — Une diagonale qui relie les points d'appui.
- **Définition pro** — Support ou résistance dynamique matérialisant la pente du mouvement ; sa valeur tient moins à sa précision qu'au fait que de nombreux ordres stop se placent juste au-delà.
- **Pourquoi c'est important** — Les lignes de tendance sont des concentrations de stops en diagonale : leur cassure produit une accélération, souvent avant un retournement du mouvement de cassure lui-même.
- **Comment le reconnaître** — Deux points minimum, un troisième pour valider ; à tracer sur les mèches ou sur les corps, mais de manière cohérente.
- **Comment les institutions l'utilisent** — Comme carte de stops : la cassure d'une ligne suivie par tout le monde libère une vague d'ordres exploitable.
- **Comment je dois l'utiliser** — Jamais comme signal d'entrée seul. Je l'utilise pour repérer la liquidité diagonale et anticiper les accélérations.
- **Erreurs fréquentes** — Tracer la ligne qui arrange le scénario du moment ; considérer la cassure d'une ligne comme un retournement de tendance (la structure, elle, peut rester intacte).
- **Pièges** — La cassure de ligne de tendance est l'un des signaux les plus piégeux : le prix casse, tout le monde entre, puis il repart dans le sens initial.
- **Exemple concret** — Ligne de support haussière cassée sur le DAX, entrée massive des vendeurs, puis reprise haussière : la structure HH/HL n'avait jamais été cassée.

```schema
              ╱ ligne de tendance
        ╱╲  ╱
      ╱   ╲╱   ← les stops s'alignent juste sous la ligne
    ╱  ✘ cassure : liquidité libérée, pas forcément retournement
   ➜ vérifier la structure (HL cassé ?) avant de conclure
```

::: memo
➡ Une carte de stops en diagonale ➡ Sa cassure ≠ retournement ➡ Vérifier la structure
:::

### TURTLE SOUP
*Stratégie de retournement sur faux cassage d'un plus haut ou plus bas de 20 périodes.*

- **Définition simple** — Prendre le contre-pied de ceux qui achètent la cassure.
- **Définition pro** — Modèle popularisé par Linda Raschke : lorsqu'un nouveau plus bas (ou plus haut) de 20 périodes est franchi puis immédiatement rejeté, on prend position dans le sens du rejet. C'est l'ancêtre documenté du *liquidity sweep*.
- **Pourquoi c'est important** — Il démontre que ce mécanisme n'est ni récent ni ésotérique : il est publié, testé et rentable depuis les années 1990.
- **Comment le reconnaître** — Nouveau plus bas de 20 périodes, clôture au-dessus de l'ancien plus bas dans les deux bougies suivantes.
- **Comment les institutions l'utilisent** — Elles fournissent la contrepartie aux systèmes de cassure automatiques, très nombreux sur ces niveaux standards.
- **Comment je dois l'utiliser** — Comme filtre simple : plus bas de 20 périodes purgé, clôture au-dessus, entrée, stop sous la mèche, objectif au milieu du range.
- **Erreurs fréquentes** — L'appliquer en pleine tendance forte contre le sens du mouvement HTF ; ne pas attendre la clôture de confirmation.
- **Pièges** — En tendance baissière puissante, le plus bas de 20 périodes est cassé jour après jour : le modèle exige un contexte de range ou de fin de mouvement.
- **Exemple concret** — Plus bas de 20 jours à 1,0800 cassé à 1,0788, clôture à 1,0815 : achat, stop 1,0783, objectif 1,0880.

```schema
   ────────────── plus bas de 20 périodes
        ▼ 1,0788 (cassure)
         ╲__╱ clôture au-dessus ← entrée
   Stop sous la mèche · objectif au milieu du range
```

::: memo
➡ Faux cassage des 20 périodes ➡ Clôture au-dessus ➡ Entrée à contre-courant
:::

## U

### UNICORN
*Configuration ICT combinant un Breaker Block et un Fair Value Gap superposés.*

- **Définition simple** — Deux zones fortes exactement au même endroit.
- **Définition pro** — Superposition d'un *breaker block* et d'un FVG, précédée d'une prise de liquidité et d'un changement de structure : la confluence des deux mécanismes (positions piégées et déséquilibre) produit une zone de très haute probabilité.
- **Pourquoi c'est important** — C'est le type de configuration qui justifie une taille pleine : rare, précise, à invalidation courte.
- **Comment le reconnaître** — Après un MSS, repérer le breaker ; si un FVG couvre la même plage de prix, la zone est qualifiée.
- **Comment les institutions l'utilisent** — Les deux mécanismes se renforcent : les traders piégés sortent au même prix où le déséquilibre doit être comblé.
- **Comment je dois l'utiliser** — Entrée limite dans la zone commune, stop au-delà du breaker, objectif sur la liquidité opposée. Deux ou trois occasions par mois et par instrument, pas davantage.
- **Erreurs fréquentes** — Forcer la superposition en élargissant les zones jusqu'à ce qu'elles se recouvrent ; l'utiliser sans MSS préalable.
- **Pièges** — Sa rareté pousse à en voir partout ; si vous en trouvez trois par jour, votre marquage est trop permissif.
- **Exemple concret** — Après un MSS baissier H1, breaker à 2 352–2 356 et FVG à 2 353–2 357 : la zone 2 353–2 356 est l'entrée, stop à 2 359.

```schema
   Breaker  ▓▓▓▓▓▓
   FVG        ░░░░░░
   Zone commune ▓░▓░  ← entrée : les deux mécanismes se cumulent
   Stop juste au-dessus · objectif sur la liquidité opposée
```

::: memo
➡ Breaker + FVG superposés ➡ Après MSS ➡ Configuration de taille pleine
:::

### UPTHRUST
*Faux cassage au-dessus de la résistance d'un range : piège acheteur.*

- **Définition simple** — Le prix casse le plafond, prend les stops, et retombe aussitôt.
- **Définition pro** — Test wyckoffien de la demande au-dessus de la résistance : la pénétration déclenche les achats stop, absorbés par l'offre institutionnelle. C'est le symétrique exact du *spring*.
- **Pourquoi c'est important** — C'est le signal de vente le plus fiable en phase de distribution, avec une invalidation courte.
- **Comment le reconnaître** — Mèche au-dessus de la résistance, retour rapide dans le range, volume élevé sur la mèche, incapacité à clôturer au-dessus.
- **Comment les institutions l'utilisent** — C'est leur dernier écoulement avant la baisse : elles vendent dans les achats de cassure du public.
- **Comment je dois l'utiliser** — Vente au retour dans le range ou au test à volume faible, stop au-dessus de la mèche, objectif au bas du range puis au-delà.
- **Erreurs fréquentes** — Acheter la cassure de la résistance (l'erreur que l'upthrust est fait pour provoquer) ; vendre avant le retour dans le range.
- **Pièges** — Toutes les cassures de résistance ne sont pas des upthrusts : sans distribution préalable, c'est une cassure haussière ordinaire.
- **Exemple concret** — Range 16 000–16 200, mèche à 16 280 sur volume record, clôture à 16 050, puis chute sous 16 000 et baisse de 600 points.

```schema
        ▲ UPTHRUST (mèche + volume)
   ─────┼──────────────────────  résistance du range
        │╲ clôture dans le range
     ╱╲ │  ╲
   ─────┼────╲────────────────  support ──► puis cassure baissière
```

::: memo
➡ Faux cassage haut ➡ Piège acheteur ➡ Distribution ➡ Vente
:::

### UTAD — UPTHRUST AFTER DISTRIBUTION
*Dernier upthrust d'une phase de distribution, juste avant la baisse.*

- **Définition simple** — Le tout dernier faux sommet avant la chute.
- **Définition pro** — Upthrust terminal de la phase C wyckoffienne : nouveau plus haut apparent au-dessus du range de distribution, immédiatement rejeté, marquant la fin de l'écoulement institutionnel.
- **Pourquoi c'est important** — Il fournit le meilleur point de vente de tout le cycle, avec le stop le plus court et l'objectif le plus lointain.
- **Comment le reconnaître** — Nouveau plus haut qui ne tient pas, volume élevé sans suivi, retour sous l'ancienne résistance en une à trois bougies, puis *Sign of Weakness*.
- **Comment les institutions l'utilisent** — Le nouveau plus haut génère des titres de presse positifs et attire les derniers acheteurs : c'est la contrepartie finale.
- **Comment je dois l'utiliser** — Vente au retour sous la résistance, stop au-dessus de la mèche de l'UTAD, premier objectif au bas du range, second sur la liquidité inférieure.
- **Erreurs fréquentes** — Acheter le nouveau record ; vendre avant la confirmation du retour sous la résistance.
- **Pièges** — L'UTAD ressemble à une cassure haussière réussie pendant quelques heures : seule la vitesse du retour le distingue.
- **Exemple concret** — Un indice fait un record à 16 280, les médias titrent sur le plus haut historique, le prix retombe à 16 040 en deux séances, puis perd 5 % en trois semaines.

```schema
   Buying Climax        UTAD ▲ (nouveau record… rejeté)
        ▲   ╱╲         ╱╲
   ─────┼──╱──╲───────╱──╲──────  résistance
        │╱    ╲     ╱    ╲
   ─────┼──────╲───╱──────╲─────  support
                            ╲▼▼▼ Sign of Weakness
```

::: memo
➡ Dernier faux record ➡ Fin de distribution ➡ Meilleure vente du cycle
:::

## V

### VALUE AREA — VAH / VAL / POC
*Zone contenant 70 % du volume échangé, et son point de contrôle.*

- **Définition simple** — Le prix où l'on a le plus échangé, et la fourchette autour.
- **Définition pro** — Issue du *Market Profile* : POC (*Point of Control*) = niveau au volume maximal ; VAH et VAL = bornes haute et basse de la zone contenant environ 70 % du volume de la période. Hors de cette zone, le marché est en découverte de prix.
- **Pourquoi c'est important** — Ces niveaux sont des aimants et des seuils d'acceptation : la journée se joue largement entre eux.
- **Comment le reconnaître** — Indicateur de profil de volume (session, hebdomadaire) sur un instrument à volume réel (futures).
- **Comment les institutions l'utilisent** — Référence d'exécution et de valorisation : un prix hors de la value area est considéré comme cher ou bon marché par rapport à la période.
- **Comment je dois l'utiliser** — Ouverture hors value area = tendance possible vers le POC ; ouverture à l'intérieur = journée de range. Objectifs sur le POC et les bornes.
- **Erreurs fréquentes** — Utiliser un profil de volume sur des données Forex de détail (volume non centralisé, donc peu fiable) ; multiplier les périodes de profil.
- **Pièges** — Le POC se déplace en cours de séance : un objectif placé sur le POC du matin peut ne plus exister l'après-midi.
- **Exemple concret** — Ouverture 40 points sous le VAL du jour précédent, retour dans la value area en deux heures, puis dérive vers le POC : la séance entière est expliquée par trois lignes.

```schema
   VAH ────────────────  borne haute
        ████████
        ██████████████  POC ← volume maximal (aimant)
        ████████
   VAL ────────────────  borne basse
   Hors zone = découverte de prix · dans la zone = équilibre
```

::: memo
➡ POC = aimant ➡ Value area = équilibre ➡ Hors zone = tendance
:::

### VOLATILITÉ
*Amplitude des variations de prix.*

- **Définition simple** — À quel point ça bouge fort.
- **Définition pro** — Écart-type des rendements (réalisée) ou anticipation extraite des options (implicite, VIX). Elle est *cyclique* : les périodes calmes précèdent les périodes agitées, et inversement.
- **Pourquoi c'est important** — Elle détermine la taille de position, la largeur du stop et le réalisme des objectifs. C'est la variable de calibrage principale.
- **Comment le reconnaître** — ATR, écart-type, bandes de Bollinger, VIX pour les actions américaines.
- **Comment les institutions l'utilisent** — *Volatility targeting* : la taille est ajustée en continu pour maintenir un risque constant. Quand la volatilité double, l'exposition est divisée par deux.
- **Comment je dois l'utiliser** — Stop et taille recalculés à chaque changement de régime : mêmes euros de risque, pas mêmes points de stop.
- **Erreurs fréquentes** — Garder la même taille quand la volatilité double ; utiliser un stop fixe en points sur des mois entiers.
- **Pièges** — La compression de volatilité (calme prolongé) précède les cassures les plus violentes : le calme est un signal, pas une sécurité.
- **Exemple concret** — L'ATR journalier du DAX passe de 120 à 260 points en une semaine : à taille inchangée, le risque réel a doublé sans qu'aucune décision n'ait été prise.

```schema
   Volatilité ▁▁▁▂▁▁▁▂▃▅███▅▃▂▁▁▁   ← cyclique, jamais stable
              calme      choc     calme
   Taille de position : inversement proportionnelle
```

::: memo
➡ Elle est cyclique ➡ Le calme annonce le choc ➡ La taille s'adapte, pas le risque
:::

### VOLUME
*Quantité échangée sur une période.*

- **Définition simple** — Combien de contrats ou d'actions ont changé de mains.
- **Définition pro** — Mesure de participation. Croisé avec le résultat en prix, il donne la loi wyckoffienne d'*effort contre résultat* : beaucoup d'effort pour peu de résultat signale une absorption.
- **Pourquoi c'est important** — C'est la seule donnée qui indique si un mouvement est soutenu par des flux réels ou s'il n'est qu'un déplacement de prix sans participation.
- **Comment le reconnaître** — Histogramme sous le graphique ; fiable sur les marchés centralisés (futures, actions), approximatif sur le Forex de détail (volume tick).
- **Comment les institutions l'utilisent** — Les algorithmes d'exécution participent au volume (VWAP, POV) : le volume est simultanément leur contrainte et leur signature.
- **Comment je dois l'utiliser** — Trois lectures suffisent : volume élevé sur une mèche = purge ; volume élevé sans progression = absorption ; volume faible en correction = correction saine.
- **Erreurs fréquentes** — Interpréter le volume tick du Forex comme un volume réel ; conclure d'un volume élevé qu'il s'agit d'achats (chaque transaction a un acheteur *et* un vendeur).
- **Pièges** — Un volume record marque souvent une fin de mouvement, pas un début : c'est le moment du transfert entre mains faibles et mains fortes.
- **Exemple concret** — Bougie baissière au volume le plus élevé depuis six mois, mais clôture dans le haut de la bougie : les vendeurs ont été absorbés, le creux est proche.

```schema
   Effort (volume)  ████████
   Résultat (prix)  ▪         ← beaucoup d'effort, peu de résultat
   ➜ ABSORPTION : quelqu'un prend l'autre côté
```

::: memo
➡ Effort contre résultat ➡ Beaucoup de volume, peu de prix ➡ Absorption
:::

### VOLUME PROFILE
*Répartition du volume échangé par niveau de prix.*

- **Définition simple** — Un histogramme couché qui montre où l'on a le plus échangé.
- **Définition pro** — Distribution du volume sur l'axe des prix pour une période donnée, faisant apparaître les nœuds à fort volume (zones d'équilibre, aimants) et les nœuds à faible volume (zones de transit rapide).
- **Pourquoi c'est important** — Il donne des niveaux fondés sur l'activité réelle plutôt que sur des figures : les zones denses attirent, les zones creuses accélèrent.
- **Comment le reconnaître** — Indicateur de profil sur une période (séance, semaine, range visible).
- **Comment les institutions l'utilisent** — Les zones à fort volume sont celles où la valeur a été acceptée : elles y trouvent la contrepartie et y reviennent naturellement.
- **Comment je dois l'utiliser** — Je place mes objectifs sur les nœuds denses et je ne place jamais un stop dans une zone creuse (le prix la traverse trop vite).
- **Erreurs fréquentes** — L'utiliser sur le Forex de détail sans volume réel ; superposer trois profils de périodes différentes jusqu'à l'illisibilité.
- **Pièges** — Un nœud à fort volume peut aussi bloquer un mouvement : c'est un aimant à l'approche, un mur au contact.
- **Exemple concret** — Le prix quitte une zone creuse et accélère de 80 points en trois minutes jusqu'au nœud dense suivant, où il s'arrête net.

```schema
   Prix   Volume
   4 520  ██
   4 510  ▏        ← zone creuse : traversée rapide
   4 500  ████████ ← nœud dense : aimant, puis mur
   4 490  ███
   ➜ objectifs sur les nœuds · jamais de stop dans le creux
```

::: memo
➡ Zones denses = aimants ➡ Zones creuses = accélération ➡ Objectifs sur les nœuds
:::

### VWAP
*Prix moyen pondéré par les volumes.*

- **Définition simple** — Le prix moyen réellement payé depuis le début de la séance.
- **Définition pro** — `Σ(prix × volume) / Σ(volume)` sur une période (séance, semaine, mois). C'est la référence d'exécution institutionnelle : un gérant est jugé sur sa capacité à acheter sous le VWAP.
- **Pourquoi c'est important** — Contrairement aux moyennes mobiles, le VWAP est un niveau **réellement utilisé** comme critère de performance par des acteurs qui déplacent le marché.
- **Comment le reconnaître** — Indicateur VWAP journalier, souvent accompagné de bandes d'écart-type.
- **Comment les institutions l'utilisent** — Les algorithmes d'exécution VWAP achètent quand le prix est en dessous et ralentissent au-dessus, ce qui crée une force de rappel mécanique.
- **Comment je dois l'utiliser** — Comme repère intraday : au-dessus du VWAP, les acheteurs contrôlent la séance ; en dessous, les vendeurs. Le retour au VWAP est une zone d'entrée en tendance.
- **Erreurs fréquentes** — L'utiliser sur le Forex de détail (sans volume réel, il perd son sens) ; le traiter comme un signal d'achat/vente autonome.
- **Pièges** — En journée de forte tendance, le prix ne revient jamais au VWAP : l'attendre fait rater le mouvement entier.
- **Exemple concret** — Le S&P reste au-dessus du VWAP toute la séance : chaque retour dessus est acheté, avec quatre points bas successifs plus hauts.

```schema
   Prix > VWAP ─────────── acheteurs aux commandes
   ═══════ VWAP ═══════  ← zone de rappel, entrée en tendance
   Prix < VWAP ─────────── vendeurs aux commandes
```

::: memo
➡ Prix moyen payé ➡ Référence institutionnelle ➡ Au-dessus on achète, en dessous on vend
:::

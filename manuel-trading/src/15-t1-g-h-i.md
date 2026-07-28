## G — GAP → GESTION DU RISQUE

### GAP
*Trou de cotation entre la clôture d'une séance et l'ouverture de la suivante.*

- **Définition simple** — Le prix rouvre plus haut ou plus bas que là où il s'était arrêté.
- **Définition pro** — Discontinuité due à l'absence de cotation (week-end, nuit, suspension) ou à un choc d'information ; classée en *common*, *breakaway*, *runaway* et *exhaustion gap*.
- **Pourquoi c'est important** — Les gaps sont des déséquilibres majeurs, comblés dans une forte proportion des cas sur les indices, et servent de cibles naturelles.
- **Comment le reconnaître** — Espace vide entre deux bougies sur le graphique journalier ; sur le Forex, gap du dimanche soir.
- **Comment les institutions l'utilisent** — Les *market makers* d'options traitent le gap comme un déséquilibre à neutraliser ; le retour vers le prix de clôture précédent est un flux mécanique.
- **Comment je dois l'utiliser** — Cible privilégiée en début de séance (comblement du gap) et niveau de référence : un gap non comblé au-dessus est un aimant haussier.
- **Erreurs fréquentes** — Trader systématiquement le comblement sans regarder le contexte (un *breakaway gap* ne se comble pas) ; oublier que les gaps du Forex sont minuscules et peu exploitables.
- **Pièges** — Le gap d'accélération en pleine tendance donne l'illusion d'une exagération ; le trader contrarien s'y fait écraser.
- **Exemple concret** — Le S&P clôture à 4 480 vendredi, ouvre à 4 512 lundi : le gap 4 480–4 512 est comblé dans les deux séances suivantes, puis la hausse reprend.

```schema
   vendredi          lundi
      ┌─┐
      │█│  4 480 ──────  ▒▒▒▒ gap ▒▒▒▒
      └─┘                     ┌─┐  4 512
                              │█│
   ── le prix revient souvent combler la zone ▒ ──
```

::: memo
➡ Trou d'ouverture ➡ Aimant ➡ Cible, sauf en gap de rupture
:::

### GESTION DU RISQUE
*Ensemble des règles qui déterminent combien perdre, et jamais combien gagner.*

- **Définition simple** — Décider à l'avance ce que vous êtes prêt à perdre.
- **Définition pro** — Discipline englobant le dimensionnement de position, le risque par trade, l'exposition corrélée, les limites de drawdown quotidien et hebdomadaire, et la règle d'arrêt. C'est la seule composante entièrement sous contrôle du trader.
- **Pourquoi c'est important** — Une méthode médiocre avec une gestion excellente survit ; une méthode excellente avec une gestion médiocre meurt. L'ordre de priorité n'est pas négociable.
- **Comment le reconnaître** — Se vérifie dans le journal : la taille est-elle constante en risque ? Le stop est-il toujours placé avant l'entrée ?
- **Comment les institutions l'utilisent** — Le risk manager est indépendant du trader et a le pouvoir de fermer les positions. Personne ne s'auto-surveille.
- **Comment je dois l'utiliser** — 0,5 à 1 % par trade, 3 % d'exposition maximale, −3 R par jour et −6 R par semaine = arrêt. Ces chiffres sont écrits et ne se négocient jamais en séance.
- **Erreurs fréquentes** — Augmenter la taille pour se refaire ; élargir un stop ; « couvrir » une position perdante par une position inverse au lieu de couper.
- **Pièges** — La série de gains est plus dangereuse que la série de pertes : c'est après trois gains qu'on double la taille et qu'on rend tout.
- **Exemple concret** — Risquer 2 % par trade avec 40 % de réussite : une série de dix pertes (probable) coûte 18 % du capital. À 0,5 %, elle en coûte 5 %.

```schema
   Risque/trade   Série de 10 pertes   Retour nécessaire
      0,5 %             −4,9 %              +5,2 %
      1   %             −9,6 %             +10,6 %
      2   %            −18,3 %             +22,4 %
      5   %            −40,1 %             +67,0 %
```

::: memo
➡ Le risque d'abord ➡ Le gain ensuite ➡ Jamais l'inverse ➡ Chiffres écrits, jamais négociés
:::

## H — HEAD AND SHOULDERS → HIGHER HIGH / HIGHER LOW

### HEAD AND SHOULDERS (ÉPAULE-TÊTE-ÉPAULE)
*Figure de retournement en trois sommets, celui du milieu étant le plus haut.*

- **Définition simple** — Trois bosses : une petite, une grande, une petite. Puis ça retourne.
- **Définition pro** — Schéma de distribution classique : l'épaule gauche et la tête se forment sur volume décroissant, l'épaule droite échoue à faire un nouveau plus haut, et la cassure de la ligne de cou valide le retournement, avec objectif égal à la hauteur tête–cou reportée.
- **Pourquoi c'est important** — Derrière la figure se cache une vraie mécanique wyckoffienne : *Buying Climax* (tête), *Secondary Test* (épaule droite), *Sign of Weakness* (cassure du cou).
- **Comment le reconnaître** — Trois sommets, volume maximal sur l'épaule gauche/tête et faible sur l'épaule droite, ligne de cou reliant les deux creux.
- **Comment les institutions l'utilisent** — Elles ne tradent pas la figure, elles la produisent : l'épaule droite est le dernier moment d'écoulement avant la baisse.
- **Comment je dois l'utiliser** — Je l'utilise comme lecture de distribution, et j'entre au **retest de la ligne de cou cassée** (flip zone), jamais sur la cassure elle-même.
- **Erreurs fréquentes** — Voir des épaule-tête-épaule partout ; entrer sur la cassure au marché ; ignorer le volume, qui est le seul élément validant.
- **Pièges** — La figure la plus connue du monde est aussi la plus utilisée contre ses adeptes : la cassure de la ligne de cou est fréquemment purgée avant le vrai départ.
- **Exemple concret** — Ligne de cou à 15 800 sur le DAX, cassée à 15 760, remontée à 15 810 (purge des stops des vendeurs), puis chute de 400 points.

```schema
              TÊTE
              ╱╲
    épaule   ╱  ╲   épaule
      ╱╲   ╱      ╲  ╱╲
     ╱  ╲╱          ╲╱  ╲
   ─────●────────────●────  ligne de cou
                       ╲▼  objectif = hauteur tête → cou
```

::: memo
➡ Trois sommets ➡ Distribution ➡ Cassure du cou ➡ Entrer au retest, pas à la cassure
:::

### HEDGING (COUVERTURE)
*Prise d'une position destinée à compenser le risque d'une autre.*

- **Définition simple** — Se protéger avec une position inverse.
- **Définition pro** — Neutralisation partielle ou totale d'une exposition, par un instrument corrélé, un dérivé (options, futures) ou une position opposée. Le coût de la couverture est le prix de l'assurance.
- **Pourquoi c'est important** — Utile pour un portefeuille long terme (couvrir un portefeuille actions par des puts). Presque toujours nuisible pour un trader court terme.
- **Comment le reconnaître** — Deux positions de sens opposé sur le même actif ou sur des actifs fortement corrélés.
- **Comment les institutions l'utilisent** — De façon calculée, avec des instruments adaptés (options, futures) et un objectif chiffré de réduction de risque, pas pour éviter d'admettre une perte.
- **Comment je dois l'utiliser** — Presque jamais en intraday. Si je veux réduire le risque, je réduis la taille ou je coupe. Une couverture ne fait que payer deux spreads pour geler une perte.
- **Erreurs fréquentes** — « Hedger » un trade perdant pour ne pas couper : la perte est verrouillée et le problème psychologique reporté.
- **Pièges** — Deux positions inverses donnent l'illusion de neutralité alors que le coût de portage, les spreads et le stress continuent de courir.
- **Exemple concret** — Long DAX en perte de 40 points, ouverture d'un short de même taille : la perte est figée à 40 points plus deux spreads, et il faudra deux décisions justes pour s'en sortir au lieu d'une.

```schema
  Long  ██████  −40 pts
  Short ██████  gelé
  ───────────────────────
  Résultat : perte figée + 2 spreads + 1 décision impossible
  ➜ couper coûte moins cher que couvrir
```

::: memo
➡ Couvrir n'est pas couper ➡ Cela fige la perte ➡ En intraday, on coupe
:::

### HTF / LTF — UNITÉS DE TEMPS
*Haute unité de temps (contexte) et basse unité de temps (exécution).*

- **Définition simple** — Les grands graphiques donnent la direction, les petits donnent l'entrée.
- **Définition pro** — Hiérarchie d'analyse multi-échelle : l'unité supérieure fixe le biais et les objectifs, l'unité inférieure sert au timing et à la réduction du risque par un stop plus court.
- **Pourquoi c'est important** — 90 % des erreurs de débutant viennent d'un signal LTF pris contre la structure HTF.
- **Comment le reconnaître** — Convention usuelle : M (mensuel) et W (hebdo) pour le régime, D1 et H4 pour le biais, H1 et M15 pour la structure, M5 et M1 pour l'entrée.
- **Comment les institutions l'utilisent** — Le mandat vient du niveau supérieur (stratégie), l'exécution est déléguée au niveau inférieur (trading desk). L'organisation reproduit la hiérarchie des unités de temps.
- **Comment je dois l'utiliser** — Trois unités seulement, dans un rapport de 4 à 6 : D1 → H1 → M5, ou H4 → M15 → M1. Le stop appartient à l'unité d'exécution, l'objectif à l'unité de contexte.
- **Erreurs fréquentes** — Changer d'unité de temps jusqu'à trouver la confirmation souhaitée (*timeframe shopping*) ; prendre un objectif HTF avec un stop M1.
- **Pièges** — En LTF, il existe toujours une structure inverse : le retracement H4 est une tendance M5 parfaite. Cela justifie n'importe quoi si l'on n'a pas fixé la hiérarchie à l'avance.
- **Exemple concret** — D1 haussier, H1 en correction baissière, M5 qui donne un CHoCH haussier au contact d'un OB H1 : c'est l'entrée. Le M5 seul n'aurait rien voulu dire.

```schema
   D1   ►  BIAIS       « où je vais »        objectif
   H1   ►  STRUCTURE   « où j'entre »        zone
   M5   ►  EXÉCUTION   « quand j'entre »     stop
   ── jamais l'inverse ──
```

::: memo
➡ Haute = direction ➡ Basse = timing ➡ Trois unités, jamais plus
:::

### HIGHER HIGH / HIGHER LOW (HH / HL)
*Sommets et creux ascendants : la définition même d'une tendance haussière.*

- **Définition simple** — Chaque sommet est plus haut, chaque creux est plus haut : ça monte.
- **Définition pro** — Séquence de pivots croissants (et symétriquement LH/LL pour la baisse), critère objectif de tendance issu de la théorie de Dow et fondement de la lecture de structure en SMC.
- **Pourquoi c'est important** — C'est la seule définition non ambiguë d'une tendance. Elle remplace toute opinion par une observation.
- **Comment le reconnaître** — Marquage manuel des pivots : un sommet est validé quand le prix casse le creux qui le précède, et inversement.
- **Comment les institutions l'utilisent** — Ces pivots sont exactement les endroits où le public place ses stops : la structure visible est aussi la carte de la liquidité.
- **Comment je dois l'utiliser** — Je marque la structure avant toute analyse. Tant que les HL tiennent, je n'envisage que des achats.
- **Erreurs fréquentes** — Marquer chaque micro-oscillation comme un pivot ; changer le marquage après coup pour justifier une position.
- **Pièges** — Le dernier HL est le niveau que le marché ira purger avant de repartir : sa cassure en mèche n'est pas un CHoCH.
- **Exemple concret** — HH 1,0900, HL 1,0850, HH 1,0940 : tant que 1,0850 tient en clôture, tout achat en discount reste valide.

```schema
                     HH
              HH    ╱╲
         ╱╲  ╱╲   ╱   ╲
   ╱╲  ╱   ╲╱  ╲╱      HL ← invalidation du biais si cassé en clôture
  ╱  HL
```

::: memo
➡ Sommets plus hauts ➡ Creux plus hauts ➡ Tendance haussière ➡ Que des achats
:::

## I — ICEBERG → IPDA

### ICEBERG (ORDRE)
*Ordre de grande taille dont seule une petite fraction est visible dans le carnet.*

- **Définition simple** — Un ordre géant qui se cache derrière un petit ordre visible.
- **Définition pro** — Ordre à quantité affichée limitée, réalimenté automatiquement à chaque exécution, permettant d'absorber un flux important sans révéler la taille totale.
- **Pourquoi c'est important** — C'est le mécanisme concret de l'absorption : un prix qui refuse de bouger malgré un flux agressif signale un iceberg.
- **Comment le reconnaître** — Sur le carnet : le même niveau est frappé des dizaines de fois sans disparaître. Sur graphique : longues mèches répétées au même prix, volume élevé, prix immobile.
- **Comment les institutions l'utilisent** — C'est leur outil d'exécution standard sur les marchés listés, souvent combiné à des algorithmes de participation au volume.
- **Comment je dois l'utiliser** — Sans données de carnet, je le déduis : volume important + absence de progression = absorption. Je me place dans le sens de l'absorbeur.
- **Erreurs fréquentes** — Insister à contre-courant d'un niveau absorbé ; confondre absorption et simple manque de volume.
- **Pièges** — L'absorption peut être retirée : un iceberg qui disparaît laisse le prix traverser le niveau instantanément.
- **Exemple concret** — Le prix teste 4 500 sept fois en trente minutes, chaque test sur volume élevé sans dépasser : un vendeur absorbe. La cassure, quand elle vient, est violente.

```schema
  Carnet visible : 20 contrats à 4 500
  Réalité        : 4 000 contrats derrière
  Prix ──►──►──►──►  bloqué, volume énorme, aucune progression
  ➜ absorption : quelqu'un de gros est de l'autre côté
```

::: memo
➡ Gros ordre caché ➡ Volume fort, prix immobile ➡ Absorption ➡ Suivre l'absorbeur
:::

### IFVG — INVERSE FAIR VALUE GAP
*FVG traversé qui change de polarité et devient zone de réaction en sens inverse.*

- **Définition simple** — Un trou que le prix a franchi et qui devient une barrière de l'autre côté.
- **Définition pro** — Déséquilibre invalidé par une clôture au-delà : les ordres qui l'avaient créé sont en perte, et la zone se comporte alors comme support si elle était résistance, ou l'inverse. C'est le pendant du *breaker* pour les déséquilibres.
- **Pourquoi c'est important** — Il permet de trader les retournements sans attendre un Order Block, et fournit une entrée très précise après un changement de structure.
- **Comment le reconnaître** — Un FVG baissier est traversé à la hausse en clôture : au retour du prix, cette zone devient un support (IFVG haussier).
- **Comment les institutions l'utilisent** — L'invalidation d'un déséquilibre signale un changement de contrôle ; la zone conserve des ordres en attente qui servent au retest.
- **Comment je dois l'utiliser** — Après un CHoCH, je cherche le premier FVG contraire traversé : son retest est mon entrée, stop de l'autre côté de la zone.
- **Erreurs fréquentes** — Compter une simple mèche traversante comme une inversion (il faut une clôture) ; utiliser un IFVG sans changement de structure préalable.
- **Pièges** — Le IFVG traversé une seconde fois n'a plus aucune valeur : une zone ne se recycle pas indéfiniment.
- **Exemple concret** — FVG baissier 2 350–2 353 sur l'or, traversé en clôture H1 à 2 358 : le retour à 2 351 devient un achat, stop à 2 347.

```schema
   FVG baissier ▓▓▓▓  ──► traversé en clôture ──► devient support
                          ╱                        ▓▓▓▓
                        ╱                            ▲ on achète au retest
   ── un déséquilibre invalidé change de camp ──
```

::: memo
➡ FVG cassé ➡ Change de camp ➡ Retest = entrée ➡ Une seule fois
:::

### IMBALANCE (DÉSÉQUILIBRE)
*Zone où le prix n'a été négocié que dans un seul sens.*

- **Définition simple** — Un endroit où il n'y a eu que des acheteurs, ou que des vendeurs.
- **Définition pro** — Terme générique recouvrant le FVG, le *liquidity void* et les zones à volume très faible du profil de volume : là où l'échange n'a pas été « équitable », le marché tend à revenir compléter la négociation.
- **Pourquoi c'est important** — Les déséquilibres sont les cibles de retour les plus fiables et les meilleures zones d'entrée limite.
- **Comment le reconnaître** — Bougies à corps large sans chevauchement de mèches ; sur profil de volume, zones creuses (*low volume nodes*).
- **Comment les institutions l'utilisent** — Elles y complètent des exécutions inachevées ; un algorithme de prix moyen a intérêt à négocier dans la zone évitée.
- **Comment je dois l'utiliser** — Cible pour les prises de profit, zone d'entrée limite dans le sens du biais, et signal d'alerte : traverser un déséquilibre sans réaction montre une force réelle.
- **Erreurs fréquentes** — Croire que tout déséquilibre sera comblé (beaucoup ne le sont jamais) ; entrer à contre-tendance uniquement parce qu'il y a un trou.
- **Pièges** — Les déséquilibres s'empilent en tendance forte : attendre le comblement fait rater tout le mouvement.
- **Exemple concret** — Après le NFP, quatre bougies M5 sans chevauchement : la zone est reprise dans l'heure suivante à 80 %, puis la tendance reprend.

```schema
   Négociation équilibrée   ▓▓▓▓▓▓▓▓  (chevauchement)
   Déséquilibre             ▓    ▓    (aucun chevauchement)
                              ▲ le prix revient souvent ici
```

::: memo
➡ Échange à sens unique ➡ Zone à recompléter ➡ Cible et entrée
:::

### INDUCEMENT (INCITATION)
*Liquidité intermédiaire délibérément offerte pour attirer les traders avant la vraie zone.*

- **Définition simple** — Un faux point d'entrée évident, placé juste avant le vrai.
- **Définition pro** — Pivot mineur situé devant un Order Block ou une zone HTF, dont la prise fournit la liquidité nécessaire à l'exécution institutionnelle dans la zone réelle. Concept clé du SMC moderne.
- **Pourquoi c'est important** — Il explique pourquoi votre entrée « parfaite » est stoppée de trois points avant de partir sans vous.
- **Comment le reconnaître** — Petit creux (ou sommet) évident entre le prix et la zone visée ; souvent le sommet/creux le plus visible du dernier segment.
- **Comment les institutions l'utilisent** — L'inducement est le carburant : sans stops à prendre, la zone principale ne peut pas être remplie.
- **Comment je dois l'utiliser** — Je repère l'inducement avant d'entrer et j'attends qu'il soit pris. Mon entrée se fait après la purge, pas avant.
- **Erreurs fréquentes** — Entrer sur le premier retour évident ; placer son stop juste sous l'inducement (le pire endroit possible).
- **Pièges** — Plusieurs inducements peuvent s'enchaîner ; c'est la structure HTF qui dit lequel compte.
- **Exemple concret** — OB H4 à 1,0800. Un petit creux à 1,0815 attire les acheteurs ; le prix le balaie, descend à 1,0802, puis monte de 90 pips.

```schema
        ╱╲
      ╱   ╲    ● inducement (petit creux évident)
    ╱       ╲ ╱╲
             ╲  ╲
   ▓▓▓▓▓▓▓▓▓▓▓▓▓ ╲▼  Order Block HTF ← la vraie zone
   ── il faut prendre ● avant de remplir ▓ ──
```

::: memo
➡ Faux point d'entrée devant le vrai ➡ Il doit être pris ➡ On entre après
:::

### INFLATION
*Hausse générale et durable du niveau des prix.*

- **Définition simple** — L'argent perd du pouvoir d'achat.
- **Définition pro** — Variation de l'indice des prix ; distinguer inflation par la demande (surchauffe), par les coûts (énergie, salaires) et par les anticipations. C'est la variable qui commande la politique monétaire.
- **Pourquoi c'est important** — Elle détermine les taux, donc le prix de tous les actifs : une action, une obligation ou une once d'or ne sont que des flux futurs actualisés à un taux.
- **Comment le reconnaître** — CPI, PPI, PCE (mesure préférée de la FED), *breakeven* obligataires, prix des matières premières.
- **Comment les institutions l'utilisent** — Elles arbitrent entre actifs réels (or, matières premières, immobilier) et actifs nominaux (obligations) selon la trajectoire d'inflation anticipée, pas selon son niveau actuel.
- **Comment je dois l'utiliser** — Comme cadre : inflation en hausse et taux qui montent = pression sur les actions longues durations et sur l'or ; inflation qui ralentit = détente des taux, soutien des actifs risqués.
- **Erreurs fréquentes** — Confondre niveau et variation : une inflation à 4 % en baisse est haussière pour les actions ; à 2 % en hausse, elle est baissière.
- **Pièges** — L'or n'est pas une protection contre l'inflation à court terme : il réagit aux **taux réels**, pas à l'inflation nominale.
- **Exemple concret** — 2022 : inflation à 9 % et or en baisse, parce que les taux réels remontaient violemment.

```schema
   Inflation ↑ ──► taux nominaux ↑ ──► taux réels ↑ ──► Or ↓ Actions ↓
   Inflation ↓ ──► taux nominaux ↓ ──► taux réels ↓ ──► Or ↑ Actions ↑
   Taux réel = taux nominal − inflation anticipée  ← la vraie variable
```

::: memo
➡ Ce qui compte est la variation ➡ Et surtout le taux réel ➡ Pas le niveau brut
:::

### INTERNAL / EXTERNAL RANGE LIQUIDITY
*Liquidité située à l'intérieur d'un range (déséquilibres) ou à ses extrémités (stops).*

- **Définition simple** — À l'intérieur, il y a les trous à combler ; aux bords, il y a les stops à prendre.
- **Définition pro** — *Internal Range Liquidity* (IRL) : FVG, OB et déséquilibres à l'intérieur du dealing range. *External Range Liquidity* (ERL) : sommets et creux du range, où sont les ordres stop. Le marché alterne entre les deux.
- **Pourquoi c'est important** — Cette alternance donne une feuille de route : après avoir pris la liquidité externe, le prix va chercher la liquidité interne, et réciproquement.
- **Comment le reconnaître** — Marquer le dealing range, repérer les FVG/OB à l'intérieur et les EQH/EQL aux bords.
- **Comment les institutions l'utilisent** — Elles se remplissent en interne (bon prix) et prennent leurs profits en externe (liquidité disponible).
- **Comment je dois l'utiliser** — J'entre sur la liquidité interne, je sors sur la liquidité externe. C'est la règle de mise en place la plus simple du modèle ICT.
- **Erreurs fréquentes** — Viser un objectif au-delà de l'ERL sans raison ; entrer sur l'ERL (là où le prix va, pas là où il part).
- **Pièges** — Quand l'ERL est prise sans réaction, le range est en expansion : il faut redessiner le dealing range, sinon toutes les zones deviennent fausses.
- **Exemple concret** — Range 100–200. Le prix prend 200 (ERL), redescend dans le FVG à 160 (IRL), puis repart vers 200. Achat à 160, sortie à 198.

```schema
   200 ──▲── ERL (stops) ────────────  sortie
        │
        ▓▓▓ IRL : FVG / OB           ← entrée
        │
   100 ──▼── ERL (stops) ────────────  sortie
   Alternance : externe ──► interne ──► externe
```

::: memo
➡ Entrer en interne ➡ Sortir en externe ➡ Le prix fait l'aller-retour
:::

### IPDA
*Algorithme de distribution des prix : modèle ICT décrivant le marché comme un système d'exécution.*

- **Définition simple** — L'idée que le prix est piloté par un algorithme qui cherche la liquidité.
- **Définition pro** — *Interbank Price Delivery Algorithm* : cadre conceptuel selon lequel le prix se déplace pour distribuer les ordres entre déséquilibres et pools de liquidité, selon des plages de référence (20, 40, 60 jours) et des heures privilégiées.
- **Pourquoi c'est important** — Que le modèle soit littéral ou métaphorique, il produit une méthode cohérente : chercher la liquidité et les déséquilibres plutôt que des figures.
- **Comment le reconnaître** — Régularité des comportements aux mêmes heures et sur les mêmes types de niveaux, jour après jour.
- **Comment les institutions l'utilisent** — Il n'existe pas d'algorithme unique documenté ; il existe en revanche des algorithmes d'exécution bancaires dont le comportement agrégé ressemble à ce modèle.
- **Comment je dois l'utiliser** — Comme grille de lecture, pas comme dogme : où est la liquidité, où sont les déséquilibres, quelle heure est-il ?
- **Erreurs fréquentes** — Prendre le modèle pour une vérité littérale et refuser toute lecture contradictoire ; croire à une machine unique qui « vous vise ».
- **Pièges** — Le vocabulaire ésotérique donne un sentiment de maîtrise ; ce sentiment n'est pas une performance. Seul le journal tranche.
- **Exemple concret** — Le prix balaie le plus bas de la veille à 09 h 30, comble un FVG H1, puis monte vers les EQH de la semaine : la séquence est lisible sans aucun indicateur.

```schema
   Liquidité prise ──► déséquilibre comblé ──► liquidité opposée visée
        ERL                  IRL                      ERL
   ── c'est tout le modèle ──
```

::: memo
➡ Le prix cherche la liquidité ➡ Puis comble les trous ➡ Puis recommence
:::

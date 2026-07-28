## P

### PAPER TRADING (COMPTE DÉMO)
*Trading simulé, sans argent réel.*

- **Définition simple** — S'entraîner avec de l'argent fictif.
- **Définition pro** — Exécution en environnement simulé, utile pour valider une mécanique opérationnelle (plateforme, règles, journal) mais incapable de reproduire la charge émotionnelle et le slippage réel.
- **Pourquoi c'est important** — Indispensable pour les 100 premiers trades : il permet de valider une méthode sans détruire un capital.
- **Comment le reconnaître** — Compte marqué « demo » ; exécution parfaite, aucun rejet, spreads idéaux.
- **Comment les institutions l'utilisent** — Sous forme de simulation historique et de *shadow trading* avant d'accorder une limite de risque réelle à un nouvel opérateur.
- **Comment je dois l'utiliser** — 100 trades en démo avec journal complet, puis passage en réel à taille minimale pendant 100 trades supplémentaires, puis seulement montée en taille.
- **Erreurs fréquentes** — Rester en démo des années (l'apprentissage émotionnel n'y a pas lieu) ; trader la démo sans rigueur, ce qui n'apprend rien.
- **Pièges** — Le succès en démo crée une confiance injustifiée : la démo n'enseigne pas ce que l'on ressent avec un mois de salaire en risque.
- **Exemple concret** — 62 % de réussite en démo, 41 % en réel avec la même méthode : la différence est entièrement comportementale (sorties précoces, entrées anticipées).

```schema
   DÉMO           │ mécanique, règles, journal          100 trades
   RÉEL MINIMUM   │ émotion, exécution, slippage        100 trades
   RÉEL NORMAL    │ montée en taille progressive        ensuite
```

::: memo
➡ La démo apprend la méthode ➡ Le réel apprend le trader ➡ Les deux, dans cet ordre
:::

### PD ARRAY — PREMIUM/DISCOUNT ARRAY
*Ensemble des zones de réaction du modèle ICT, classées selon leur position dans le range.*

- **Définition simple** — La liste de toutes les zones où le prix réagit, rangée du plus cher au moins cher.
- **Définition pro** — Matrice regroupant Order Blocks, FVG, Breakers, Mitigation Blocks, Rejection Blocks, *liquidity voids* et *old highs/lows*, hiérarchisés selon qu'ils se situent en premium (zones de vente) ou en discount (zones d'achat).
- **Pourquoi c'est important** — Elle donne une méthode de balayage complète : au lieu de chercher un signal, on classe les zones et on attend que le prix vienne à la bonne.
- **Comment le reconnaître** — Se construit : tracer le dealing range, marquer l'équilibre, puis répertorier les zones de chaque côté.
- **Comment les institutions l'utilisent** — La logique est celle de l'exécution : vendre cher, acheter bon marché, à l'intérieur d'un range de référence.
- **Comment je dois l'utiliser** — Une seule règle : je n'utilise que les zones en discount pour acheter et en premium pour vendre. Toute zone du mauvais côté est ignorée, aussi belle soit-elle.
- **Erreurs fréquentes** — Trader un OB haussier situé en premium ; multiplier les zones jusqu'à couvrir tout le graphique.
- **Pièges** — Trop de zones tue la zone : au-delà de trois par unité de temps, la carte devient inutilisable.
- **Exemple concret** — Range 100–200. En premium : OB baissier à 180, FVG à 172, EQH à 200. En discount : FVG à 128, OB haussier à 112. Le prix à 175 → seules les ventes sont autorisées.

```schema
   200 ─── EQH (liquidité)          ┐
   180 ─── OB baissier              ├ PREMIUM : ventes uniquement
   172 ─── FVG baissier             ┘
   150 ═══ ÉQUILIBRE ═══
   128 ─── FVG haussier             ┐
   112 ─── OB haussier              ├ DISCOUNT : achats uniquement
   100 ─── EQL (liquidité)          ┘
```

::: memo
➡ Zones classées ➡ Premium = vendre ➡ Discount = acheter ➡ Jamais l'inverse
:::

### PIP / POINT / TICK
*Plus petite variation de prix cotée.*

- **Définition simple** — L'unité de mesure du mouvement.
- **Définition pro** — Pip : quatrième décimale sur la plupart des paires Forex (deuxième pour le yen). Tick : plus petite variation d'un contrat à terme, avec une valeur monétaire fixe. Point : unité de cotation d'un indice.
- **Pourquoi c'est important** — Sans conversion en valeur monétaire, aucun calcul de risque n'est possible : c'est le lien entre le graphique et le compte.
- **Comment le reconnaître** — Spécifié par le contrat : 1 tick sur l'ES vaut 12,50 $, 1 pip sur 1 lot EURUSD vaut environ 10 $.
- **Comment les institutions l'utilisent** — Toute la mesure de performance et de risque est exprimée en valeur monétaire par tick, jamais en « points » abstraits.
- **Comment je dois l'utiliser** — Je connais par cœur la valeur du point de mes deux ou trois instruments. Sans cela, le calcul de taille est impossible.
- **Erreurs fréquentes** — Confondre pip et pipette (cinquième décimale) ; ignorer que la valeur du pip varie selon la devise du compte.
- **Pièges** — Sur les paires en yen, la décimale change : une erreur d'un facteur 100 sur la taille est classique.
- **Exemple concret** — Stop de 30 pips sur 0,4 lot EURUSD = 30 × 10 × 0,4 = 120 € de risque.

```schema
   EURUSD  1 pip = 0,0001 = 10 $ par lot standard
   USDJPY  1 pip = 0,01   = ≈ 9 $ par lot (variable)
   ES      1 tick = 0,25 point = 12,50 $
   DAX     1 point = 25 € par contrat
```

::: memo
➡ Connaître la valeur du point ➡ Par cœur ➡ Sinon aucun calcul de risque n'est possible
:::

### PPI — PRODUCER PRICE INDEX
*Indice des prix à la production.*

- **Définition simple** — De combien les prix ont augmenté pour les entreprises, avant d'arriver aux consommateurs.
- **Définition pro** — Mesure de l'évolution des prix de vente perçus par les producteurs : indicateur avancé du CPI, car les coûts en amont finissent par se répercuter sur les prix de détail.
- **Pourquoi c'est important** — Il anticipe la trajectoire de l'inflation à la consommation et donc les décisions de banque centrale.
- **Comment le reconnaître** — Calendrier économique, généralement publié quelques jours avant ou après le CPI.
- **Comment les institutions l'utilisent** — Comme signal avancé pour ajuster les anticipations avant la publication du CPI, et pour anticiper les marges des entreprises.
- **Comment je dois l'utiliser** — Volatilité moindre que le CPI : je le traite comme un événement de second rang, avec une taille réduite mais sans interdiction totale.
- **Erreurs fréquentes** — Le traiter comme le CPI (impact moindre) ou l'ignorer complètement (il oriente les attentes du CPI).
- **Pièges** — Un PPI très différent du consensus modifie les attentes de CPI et peut provoquer une réaction plus forte que prévu.
- **Exemple concret** — PPI nettement au-dessus des attentes : le marché relève ses anticipations de CPI, le dollar s'apprécie deux jours avant la publication du CPI.

```schema
   PPI (producteurs) ──► marges ──► CPI (consommateurs) ──► taux ──► marchés
   ── indicateur avancé, deuxième rang de volatilité ──
```

::: memo
➡ Inflation en amont ➡ Annonce le CPI ➡ Impact moyen
:::

### PREMIUM / DISCOUNT
*Partie chère et partie bon marché d'un range de référence.*

- **Définition simple** — Au-dessus du milieu, c'est cher ; en dessous, c'est bon marché.
- **Définition pro** — Découpage du dealing range par son point médian : *premium* au-dessus (zone de vente institutionnelle), *discount* en dessous (zone d'achat). Fondement de la notion de prix « équitable » en SMC.
- **Pourquoi c'est important** — Cette seule règle élimine la majorité des mauvaises entrées : acheter en premium et vendre en discount est l'erreur la plus coûteuse et la plus répandue.
- **Comment le reconnaître** — Fibonacci 0,5 du dernier segment structurel, ou milieu du range.
- **Comment les institutions l'utilisent** — Leur mandat d'exécution est mécanique : améliorer le prix moyen. Elles ne peuvent donc pas acheter en haut du range sans dégrader leur performance.
- **Comment je dois l'utiliser** — Filtre binaire : au-dessus de 50 %, seules les ventes sont autorisées ; en dessous, seuls les achats. Aucune exception.
- **Erreurs fréquentes** — Mesurer le premium/discount sur un range mal choisi ; oublier de redéfinir le range après une expansion.
- **Pièges** — En tendance forte, le prix reste en premium pendant tout le mouvement : le filtre s'applique alors au range de l'impulsion en cours, pas au range global.
- **Exemple concret** — Range 1,0800–1,0900. Prix à 1,0875 : achat interdit, même avec un OB haussier apparent. Attendre 1,0840.

```schema
   1,0900 ┐
          │ ░░░░ PREMIUM ░░░░   ← ventes
   1,0850 ╪══════════════════
          │ ▓▓▓▓ DISCOUNT ▓▓▓▓   ← achats
   1,0800 ┘
```

::: memo
➡ Au-dessus du milieu on vend ➡ En dessous on achète ➡ Aucune exception
:::

### PRICE ACTION
*Lecture du marché à partir du seul prix, sans indicateur.*

- **Définition simple** — Lire ce que fait le prix, directement.
- **Définition pro** — Approche fondée sur la structure, les niveaux, les bougies et le contexte, sans transformation mathématique retardée. Les indicateurs sont dérivés du prix : le prix est donc l'information de premier rang.
- **Pourquoi c'est important** — C'est la seule information non retardée. Tout indicateur est une fonction du passé du prix.
- **Comment le reconnaître** — Graphique nu : structure, niveaux, mèches, volumes.
- **Comment les institutions l'utilisent** — Elles combinent flux, niveaux et macro. Le graphique nu est le vocabulaire commun de ces échanges.
- **Comment je dois l'utiliser** — Graphique propre : structure, deux ou trois niveaux HTF, zones de liquidité. Aucun indicateur autre qu'une moyenne de régime éventuelle.
- **Erreurs fréquentes** — Appeler « price action » une collection de figures de chandeliers mémorisées ; ajouter des indicateurs jusqu'à masquer le prix.
- **Pièges** — La price action laisse toute latitude d'interprétation : sans règles écrites, elle devient une justification a posteriori de n'importe quelle envie.
- **Exemple concret** — Un graphique avec structure marquée, plus haut/plus bas de la veille et une zone OB suffit à décider en dix secondes ; le même graphique avec cinq indicateurs demande cinq minutes et produit une conclusion contradictoire.

```schema
   PRIX ──► indicateurs (dérivés, retardés)
     ▲
     └── information de premier rang : structure · niveaux · liquidité
```

::: memo
➡ Le prix d'abord ➡ Les indicateurs sont dérivés ➡ Graphique propre, règles écrites
:::

### PROP FIRM (SOCIÉTÉ DE FINANCEMENT)
*Société qui confie un capital à un trader après une évaluation.*

- **Définition simple** — Une entreprise vous prête un compte si vous réussissez un test.
- **Définition pro** — Modèle d'évaluation payante assorti de contraintes : objectif de gain, perte journalière maximale, perte totale maximale, souvent en environnement simulé avec partage des profits.
- **Pourquoi c'est important** — Elle permet d'accéder à une taille supérieure, mais impose des règles de risque plus strictes que la plupart des méthodes personnelles.
- **Comment le reconnaître** — Règles chiffrées : par exemple 8 % d'objectif, 5 % de perte quotidienne, 10 % de perte totale.
- **Comment les institutions l'utilisent** — Le modèle du *prop trading* classique existe depuis longtemps ; la version en ligne à évaluation payante en est une variante commerciale, dont le revenu principal provient souvent des frais d'inscription.
- **Comment je dois l'utiliser** — J'adapte la gestion aux règles : risque de 0,25 à 0,5 % par trade, pas plus de deux trades par jour, arrêt immédiat à −2 % sur la journée. Les règles de la firme deviennent mes règles.
- **Erreurs fréquentes** — Trader une prop firm comme un compte personnel ; viser l'objectif en une semaine ; ignorer la règle de perte journalière calculée sur le solde ou sur l'équité selon les maisons.
- **Pièges** — La perte journalière se calcule souvent sur l'équité (positions ouvertes comprises) : une position perdante non clôturée peut violer la règle sans que le stop soit touché.
- **Exemple concret** — Objectif 8 %, perte quotidienne 5 %. À 0,5 % de risque et 1:2 de ratio moyen, il faut environ 25 trades gagnants nets : c'est un travail de deux mois, pas de deux semaines.

```schema
   Objectif  +8 %   ├────────────────────────►
   Perte/jour −5 %  ├──►  arrêt automatique
   Perte max −10 %  ├──►  compte fermé
   ➜ risque 0,25–0,5 % par trade, 2 trades/jour maximum
```

::: memo
➡ Leurs règles deviennent les miennes ➡ Risque divisé par deux ➡ Deux mois, pas deux semaines
:::

### PULLBACK (RETRACEMENT)
*Mouvement temporaire contraire à la tendance.*

- **Définition simple** — Une pause qui revient en arrière, avant que ça reparte.
- **Définition pro** — Correction d'une impulsion, généralement entre 38 % et 79 % du segment, à corps réduits et volumes décroissants, offrant une entrée dans le sens de la tendance à meilleur prix.
- **Pourquoi c'est important** — C'est le seul moment où l'on peut entrer dans une tendance avec un risque limité et un ratio élevé.
- **Comment le reconnaître** — Bougies plus petites et chevauchantes, volumes en baisse, pente moins forte que l'impulsion, absence de cassure du dernier pivot.
- **Comment les institutions l'utilisent** — Le retracement est le moment où elles complètent leurs positions : le manque de volume vendeur en correction haussière signale que personne ne distribue réellement.
- **Comment je dois l'utiliser** — J'attends le retracement en zone discount (OTE, OB, FVG), avec purge de l'inducement, puis j'entre dans le sens de la tendance.
- **Erreurs fréquentes** — Confondre retracement et retournement ; entrer trop tôt dans le retracement (à 0,382) par peur de rater.
- **Pièges** — Un retracement à volume croissant et corps larges n'est plus un retracement : c'est un retournement en formation.
- **Exemple concret** — Impulsion de 200 points, retracement de 130 points en huit bougies étroites, purge du dernier creux mineur, puis reprise de 300 points.

```schema
   IMPULSION ███████ (corps larges, volume ↑)
                    ▪▪▪▪ RETRACEMENT (corps étroits, volume ↓)
                        ███████ REPRISE
   ── entrer ici ─────────┘
```

::: memo
➡ Corps étroits ➡ Volume en baisse ➡ C'est une pause ➡ On entre dedans
:::

## Q

### QE / QT — ASSOUPLISSEMENT ET RESSERREMENT QUANTITATIFS
*Création ou destruction de liquidité par le bilan de la banque centrale.*

- **Définition simple** — La banque centrale achète des obligations pour injecter de l'argent (QE), ou les laisse arriver à échéance pour en retirer (QT).
- **Définition pro** — Politique non conventionnelle agissant sur la quantité de réserves bancaires et sur la prime de terme, quand le taux directeur ne suffit plus. Le QE comprime les rendements longs et pousse les investisseurs vers les actifs risqués.
- **Pourquoi c'est important** — La liquidité globale est le principal moteur des marchés d'actifs sur plusieurs années : les grandes hausses coïncident avec les expansions de bilan.
- **Comment le reconnaître** — Suivi de la taille du bilan de la FED, des réserves bancaires et du compte de trésorerie.
- **Comment les institutions l'utilisent** — Allocation stratégique : en QE, on privilégie la duration et le risque ; en QT, on réduit le levier et on privilégie la liquidité.
- **Comment je dois l'utiliser** — Comme toile de fond trimestrielle, pas comme signal : en QT, les phases de baisse sont plus violentes et les rebonds moins fiables.
- **Erreurs fréquentes** — Tirer un signal intraday de la liquidité globale ; ignorer que le QT est absorbé différemment selon l'état du marché monétaire.
- **Pièges** — La corrélation liquidité/actions est réelle mais irrégulière : elle explique les années, pas les semaines.
- **Exemple concret** — 2020–2021 : expansion massive du bilan, hausse générale des actifs. 2022 : resserrement et hausse des taux, baisse simultanée des actions et des obligations.

```schema
   QE  ──► liquidité ↑ ──► taux longs ↓ ──► actions ↑ · or ↑ · crypto ↑
   QT  ──► liquidité ↓ ──► taux longs ↑ ──► actions ↓ · volatilité ↑
   Échelle : trimestres et années, jamais la séance
```

::: memo
➡ QE = argent injecté = actifs en hausse ➡ QT = l'inverse ➡ Horizon long
:::

## R

### RANGE
*Zone horizontale bornée par un support et une résistance.*

- **Définition simple** — Un couloir dans lequel le prix fait des allers-retours.
- **Définition pro** — Phase d'équilibre où l'offre et la demande s'équilibrent entre deux bornes ; la structure interne (chevauchements, absence de BOS) confirme l'absence de tendance.
- **Pourquoi c'est important** — Le marché y passe la majorité de son temps, et les stratégies de tendance y perdent systématiquement.
- **Comment le reconnaître** — Deux touches minimum sur chaque borne, chevauchement des bougies, ATR en baisse.
- **Comment les institutions l'utilisent** — Elles construisent leur position dans le range et provoquent la sortie : le range est l'usine, la tendance est la livraison.
- **Comment je dois l'utiliser** — Deux stratégies possibles : vendre le haut / acheter le bas avec objectif au milieu, ou attendre la cassure et trader le retest. Jamais au milieu.
- **Erreurs fréquentes** — Trader chaque oscillation interne ; entrer sur les fausses sorties ; oublier que les bornes sont des pools de liquidité qui seront percés en mèche.
- **Pièges** — Le range se termine toujours par un faux cassage d'un côté avant la vraie sortie de l'autre.
- **Exemple concret** — Range 100 points sur trois jours, mèche de 25 points au-dessus (purge), puis chute de 300 points : la sortie s'est faite dans l'autre sens.

```schema
   ══════════════════ résistance (BSL) ══ ← purge probable avant la vraie sortie
     ╱╲    ╱╲   ╱╲
    ╱  ╲  ╱  ╲ ╱  ╲     ← zone morte au milieu
   ══════════════════ support (SSL) ═════
```

::: memo
➡ Deux bornes ➡ On trade les bords ➡ Faux cassage d'abord ➡ Vraie sortie ensuite
:::

### RATIO RISQUE / RENDEMENT (R:R)
*Rapport entre le gain visé et la perte acceptée.*

- **Définition simple** — Combien vous gagnez si vous avez raison, comparé à ce que vous perdez si vous avez tort.
- **Définition pro** — `R:R = distance à l'objectif / distance au stop`. Couplé au taux de réussite, il détermine l'espérance : `E = (p × R) − (1 − p)`.
- **Pourquoi c'est important** — Il permet d'être rentable en ayant tort la majorité du temps : à 1:3, 30 % de réussite suffisent à l'équilibre.
- **Comment le reconnaître** — Se calcule avant l'entrée, jamais après.
- **Comment les institutions l'utilisent** — Comme critère de sélection : un trade dont le ratio est insuffisant n'est pas pris, même si la direction paraît juste.
- **Comment je dois l'utiliser** — Minimum 1:2 sur le premier objectif, et je refuse tout trade sous ce seuil, même « évident ».
- **Erreurs fréquentes** — Déplacer l'objectif pour obtenir un beau ratio sur le papier ; élargir le stop après l'entrée, ce qui détruit le ratio réel.
- **Pièges** — Un ratio de 1:10 avec 5 % de réussite est perdant. Le ratio n'a de sens qu'avec un taux de réussite réaliste, mesuré dans le journal.
- **Exemple concret** — Entrée 100, stop 95, objectif 115 : ratio 1:3. Avec 40 % de réussite, l'espérance est `(0,4 × 3) − 0,6 = +0,6 R` par trade.

```schema
   Taux de réussite nécessaire pour être à l'équilibre
   R:R 1:1  ──► 50 %      R:R 1:3  ──► 25 %
   R:R 1:2  ──► 33 %      R:R 1:5  ──► 17 %
   ➜ on peut avoir tort 3 fois sur 4 et gagner
```

::: memo
➡ Minimum 1:2 ➡ Calculé avant ➡ Le ratio compense le taux de réussite
:::

### RÉCESSION
*Contraction durable de l'activité économique.*

- **Définition simple** — L'économie recule pendant plusieurs mois.
- **Définition pro** — Définie de façon technique par deux trimestres consécutifs de PIB négatif, et de façon officielle aux États-Unis par le NBER à partir d'un faisceau d'indicateurs (emploi, revenus, production, ventes).
- **Pourquoi c'est important** — Les récessions provoquent les plus fortes baisses d'actions et les plus fortes hausses d'obligations : c'est le régime qui change tout.
- **Comment le reconnaître** — Indicateurs avancés : inversion de la courbe des taux, PMI sous 50, hausse du chômage, resserrement du crédit.
- **Comment les institutions l'utilisent** — Rotation vers les obligations d'État, les secteurs défensifs et les liquidités ; réduction de l'exposition au risque bien avant la confirmation officielle.
- **Comment je dois l'utiliser** — Comme cadre : en approche de récession, les rebonds d'indices se vendent et les baisses de taux ne sont pas haussières pour les actions (elles signalent le problème).
- **Erreurs fréquentes** — Acheter les actions dès la première baisse de taux ; confondre le sommet des taux avec le creux des actions.
- **Pièges** — La courbe des taux s'inverse en moyenne 12 à 18 mois avant la récession : le signal est juste, le timing est inexploitable en intraday.
- **Exemple concret** — Inversion 2 ans/10 ans en 2022 ; les indices atteignent leur creux fin 2022, mais l'inversion continue de se dénouer pendant plus d'un an.

```schema
   Courbe inversée ──► 12-18 mois ──► récession ──► baisse de taux
   Actions : baissent AVANT la récession, montent AVANT la reprise
   ── le marché a toujours 6 mois d'avance sur l'économie ──
```

::: memo
➡ Le marché anticipe ➡ Six mois d'avance ➡ On trade l'anticipation, pas la nouvelle
:::

### REJECTION BLOCK
*Zone constituée par les mèches de rejet successives à un extrême.*

- **Définition simple** — L'endroit où le prix a été refusé plusieurs fois, mèche après mèche.
- **Définition pro** — Zone définie par les corps et les mèches d'un sommet ou d'un creux ayant produit un rejet marqué : elle matérialise une offre ou une demande institutionnelle plutôt qu'un simple niveau.
- **Pourquoi c'est important** — Elle offre une zone de vente ou d'achat là où il n'y a pas d'Order Block exploitable, notamment sur les extrêmes en mèche.
- **Comment le reconnaître** — Une ou plusieurs longues mèches au même niveau, avec des corps courts, à un extrême de structure.
- **Comment les institutions l'utilisent** — La mèche est la trace de leur absorption : le prix a été poussé puis renvoyé, ce qui indique une contrepartie de taille.
- **Comment je dois l'utiliser** — En zone premium pour vendre ou discount pour acheter, avec stop au-delà de l'extrême des mèches et objectif sur la liquidité opposée.
- **Erreurs fréquentes** — Utiliser un rejection block sans contexte de structure ; le confondre avec un Order Block classique (qui repose sur le corps de la dernière bougie opposée).
- **Pièges** — Une zone de rejet traversée sans réaction signale un changement de contrôle : elle ne se retente pas.
- **Exemple concret** — Trois mèches supérieures à 2 362–2 365 sur l'or en H1 : la zone devient une résistance de vente, stop à 2 368.

```schema
     │  │  │   ← mèches de rejet répétées
   ┌─┴┐┌┴┐┌┴┐
   │▓▓││▓││▓│  ← zone de rejet (offre institutionnelle)
   └──┘└─┘└─┘
   Vente au retour dans la zone, stop au-dessus des pointes
```

::: memo
➡ Mèches répétées ➡ Offre ou demande réelle ➡ Zone de retournement
:::

### RENDEMENT OBLIGATAIRE
*Taux de rendement d'une obligation, inverse de son prix.*

- **Définition simple** — Ce que rapporte une obligation ; quand son prix monte, son rendement baisse.
- **Définition pro** — Taux actuariel intégrant coupon et prix. Le rendement du 10 ans américain est le taux d'actualisation de référence mondial ; le 2 ans reflète les anticipations de politique monétaire.
- **Pourquoi c'est important** — Les rendements pilotent la valorisation de toutes les autres classes d'actifs : actions de croissance, or et immobilier y sont particulièrement sensibles.
- **Comment le reconnaître** — Graphiques US02Y, US10Y ; l'écart 10 ans − 2 ans donne la pente de la courbe.
- **Comment les institutions l'utilisent** — C'est le point de départ de toute valorisation : le taux sans risque est le dénominateur commun des modèles.
- **Comment je dois l'utiliser** — Comme confirmation macro : hausse rapide des rendements réels = pression sur l'or et sur les valeurs technologiques. Divergence rendement/dollar = alerte.
- **Erreurs fréquentes** — Confondre prix et rendement de l'obligation ; ignorer la distinction entre rendement nominal et rendement réel.
- **Pièges** — L'or ne suit pas l'inflation mais les taux réels : c'est la raison de nombreux contresens.
- **Exemple concret** — Le 10 ans réel passe de 1,4 % à 2,0 % en trois semaines : l'or perd 120 $ malgré une inflation toujours élevée.

```schema
   Prix de l'obligation ↑  ──► rendement ↓  ──► or ↑ · actions ↑
   Prix de l'obligation ↓  ──► rendement ↑  ──► or ↓ · actions ↓
   Courbe : 10 ans − 2 ans  ──► négative = récession anticipée
```

::: memo
➡ Prix et rendement en sens inverse ➡ Taux réels = clé de l'or ➡ Courbe = cycle
:::

### RISQUE DE RUINE
*Probabilité de perdre l'intégralité du capital.*

- **Définition simple** — La chance que vous ayez tout perdu avant que votre méthode ne paie.
- **Définition pro** — Fonction du taux de réussite, du ratio gain/perte et surtout de la fraction risquée par trade : le risque de ruine croît de manière non linéaire avec la taille.
- **Pourquoi c'est important** — Une stratégie à espérance positive peut ruiner si la taille est trop élevée. Survivre est une condition préalable à gagner.
- **Comment le reconnaître** — Se calcule à partir des statistiques du journal ; existe en simulateurs (Monte-Carlo).
- **Comment les institutions l'utilisent** — Limites de perte et réduction automatique de la taille : personne n'est autorisé à mettre la structure en danger.
- **Comment je dois l'utiliser** — Risque par trade limité à 1 % maximum, ce qui rend la ruine pratiquement impossible pour une méthode à espérance positive, même avec dix pertes consécutives.
- **Erreurs fréquentes** — Raisonner en moyenne (« je gagne 60 % du temps ») en oubliant la variance : dix pertes d'affilée surviennent régulièrement.
- **Pièges** — La probabilité d'une série de dix pertes avec 50 % de réussite sur 200 trades est loin d'être négligeable : la série longue n'est pas une anomalie.
- **Exemple concret** — À 55 % de réussite et 1:1, risquer 10 % par trade donne un risque de ruine élevé ; à 1 %, il devient négligeable. La méthode est pourtant identique.

```schema
   Risque/trade   Risque de ruine (méthode gagnante, 1:1, p = 55 %)
      1 %              ≈ 0 %
      2 %              faible
      5 %              significatif
     10 %              élevé
   ── la taille, pas la méthode, détermine la survie ──
```

::: memo
➡ Survivre d'abord ➡ 1 % maximum ➡ La ruine vient de la taille, pas de la méthode
:::

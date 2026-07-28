# Tome 4 — Checklists

Neuf checklists opérationnelles. Elles ne servent à rien si elles sont lues :
elles servent si elles sont **cochées**. Imprimez-les, ou gardez-les ouvertes à
côté de la plateforme.

::: astuce La règle d'usage
Une seule case non cochée = pas de trade. Il n'y a pas de « presque ». Une
checklist dont on négocie les cases n'est plus une checklist, c'est une
décoration.
:::

## Checklist 1 — Daily Bias

*À faire avant 09 h, en dix minutes, tous les jours.*

**Contexte**

- ☐ Quelle est la structure **hebdomadaire** ? (HH/HL, LH/LL, ou range)
- ☐ Quelle est la structure **journalière** ?
- ☐ Le prix est-il en premium ou en discount du dealing range journalier ?
- ☐ La bougie de la veille : quel type ? (impulsion, correction, indécision)

**Liquidité**

- ☐ Quelle liquidité a été prise hier ? (PDH, PDL, EQH, EQL)
- ☐ Quelle liquidité reste **non prise** au-dessus ?
- ☐ Quelle liquidité reste **non prise** en dessous ?
- ☐ Quelle est la plus proche, et laquelle est la plus « propre » ?

**Calendrier**

- ☐ Y a-t-il une publication majeure aujourd'hui ? À quelle heure ?
- ☐ Une banque centrale s'exprime-t-elle ?
- ☐ Est-ce un jour d'expiration ou de rééquilibrage ?

**Décision — les trois lignes à écrire**

```schema
   ┌───────────────────────────────────────────────┐
   │ DIRECTION    : ..............................  │
   │ CIBLE        : .............................. │
   │ INVALIDATION : .............................. │
   └───────────────────────────────────────────────┘
```

- ☐ Les trois lignes sont écrites (pas pensées : **écrites**).
- ☐ Si je ne peux pas les écrire → **journée d'observation**, pas de trade.

::: memo
➡ Une direction ➡ Une cible ➡ Une invalidation ➡ Écrites avant 09 h
:::

## Checklist 2 — Analyse HTF

*À faire le dimanche pour la semaine, et chaque matin en révision rapide.*

**Mensuel / hebdomadaire**

- ☐ Régime de fond : haussier, baissier, ou range ?
- ☐ Le prix est-il au-dessus ou en dessous de la MM200 journalière ?
- ☐ Quels sont les deux niveaux hebdomadaires les plus proches (au-dessus et en
  dessous) ?

**Journalier**

- ☐ Structure marquée : trois à cinq pivots majeurs, pas plus.
- ☐ Dealing range tracé, équilibre à 50 % visible.
- ☐ Zones HTF actives repérées : OB, FVG, breaker (maximum trois).
- ☐ Chaque zone est-elle du bon côté de l'équilibre ?

**H4**

- ☐ La structure H4 confirme-t-elle le journalier, ou est-elle en correction ?
- ☐ Y a-t-il un FVG H4 non comblé ? Où ?
- ☐ Quel est le dernier point d'invalidation H4 ?

**Cohérence**

- ☐ Mes trois unités de temps racontent-elles la même histoire ?
- ☐ Si elles se contredisent → je réduis la taille ou je ne trade pas.

::: memo
➡ Hebdo = régime ➡ Journalier = biais ➡ H4 = structure ➡ Trois zones maximum
:::

## Checklist 3 — Liquidité

*À faire avant chaque entrée, sans exception.*

- ☐ Quelle liquidité vient d'être **prise** ? (le carburant)
- ☐ Quelle liquidité est **visée** ? (l'objectif)
- ☐ La distance jusqu'à cette liquidité justifie-t-elle le risque ? (≥ 1:2)
- ☐ Y a-t-il un **inducement** entre le prix et ma zone ? A-t-il été consommé ?
- ☐ Mon stop est-il placé **au-delà** d'un pool, et non dedans ?
- ☐ Mon objectif est-il **juste avant** un pool, et non dessus ni au-delà ?
- ☐ Existe-t-il un second pool de liquidité juste au-delà du premier ? (risque
  de double purge)

```schema
   ▲▲▲ BSL   ← objectif si j'achète · stop si je vends (au-delà)
   ═════════════════════════
        entrée
   ═════════════════════════
   ▼▼▼ SSL   ← objectif si je vends · stop si j'achète (au-delà)
```

::: memo
➡ D'où vient le carburant ➡ Où va le prix ➡ Deux réponses ou pas de trade
:::

## Checklist 4 — Entrée

*La séquence, dans l'ordre. Aucune étape ne se saute.*

**1. Contexte**

- ☐ Le trade va-t-il dans le sens du biais du jour ?
- ☐ Suis-je du bon côté de l'équilibre (premium pour vendre, discount pour
  acheter) ?
- ☐ Suis-je dans une Kill Zone ?

**2. Déclencheur**

- ☐ Une liquidité a-t-elle été purgée ?
- ☐ Y a-t-il eu un CHoCH ou un MSS **avec déplacement** ?
- ☐ Le déplacement a-t-il laissé un FVG ?

**3. Zone**

- ☐ La zone d'entrée est-elle identifiée (OB, FVG, breaker, IFVG, BPR) ?
- ☐ Est-ce sa **première** mitigation ?
- ☐ L'inducement devant elle a-t-il été pris ?

**4. Mécanique**

- ☐ Stop placé au-delà de la structure + marge (spread et bruit).
- ☐ Taille **calculée** : `(capital × risque %) / (distance stop × valeur point)`.
- ☐ Objectif 1 à 1:2 minimum, objectif 2 sur la liquidité HTF.
- ☐ Ordre limite préparé (pas d'entrée au marché).

**5. Contrôle final**

- ☐ Aurais-je pris ce trade si je venais de perdre trois fois d'affilée ?
- ☐ Aurais-je pris ce trade si je venais de gagner trois fois d'affilée ?
- ☐ Si l'une des deux réponses est non → **je ne le prends pas**.

::: memo
➡ Contexte ➡ Déclencheur ➡ Zone ➡ Mécanique ➡ Contrôle ➡ Cinq étapes, jamais quatre
:::

## Checklist 5 — Sortie

*La sortie décide du résultat autant que l'entrée. Elle se planifie avant.*

**Avant l'entrée**

- ☐ Objectif 1 défini (1:2), avec la fraction de position à solder.
- ☐ Objectif 2 défini (liquidité HTF).
- ☐ Règle de passage à l'équilibre écrite : à quel moment exactement ?
- ☐ Règle de stop suiveur écrite : sous chaque nouveau pivot, ou à N × ATR ?

**Pendant le trade**

- ☐ L'objectif 1 est atteint → moitié soldée, stop à l'équilibre. Automatique.
- ☐ La structure s'est-elle retournée contre moi avant l'objectif ? (CHoCH
  contraire → sortie manuelle, sans attendre le stop)
- ☐ Le contexte a-t-il changé ? (news imprévue, volatilité anormale)
- ☐ Je n'ai **pas** déplacé mon stop dans le sens de la perte.

**Sorties anticipées légitimes** — les seules autorisées

| Motif | Légitime ? |
|---|---|
| CHoCH contre ma position sur mon unité de travail | ✔ |
| Publication imprévue ou volatilité anormale | ✔ |
| Absorption visible contre moi à un niveau clé | ✔ |
| Fin de session, position intraday | ✔ |
| « J'ai peur de rendre mon gain » | ✘ |
| « Ça stagne depuis vingt minutes » | ✘ |
| « J'ai besoin d'un trade gagnant aujourd'hui » | ✘ |

::: memo
➡ Deux objectifs ➡ Moitié à 1:2 ➡ Stop à l'équilibre ➡ Le reste suit la structure
:::

## Checklist 6 — Gestion du risque

*À vérifier une fois par semaine, et à chaque changement de compte.*

**Par trade**

- ☐ Risque fixé à 0,5 % ou 1 % du capital — écrit, jamais improvisé.
- ☐ La taille est **calculée**, pas choisie.
- ☐ Le stop est technique (issu du graphique), pas monétaire (issu du confort).
- ☐ Le spread est intégré à la distance de stop.

**Par jour**

- ☐ Limite de perte quotidienne : **−3 R** → plateforme fermée.
- ☐ Nombre maximal de trades : **3**.
- ☐ Deux stops consécutifs sur le même instrument → arrêt sur cet instrument.

**Par semaine**

- ☐ Limite de perte hebdomadaire : **−6 R** → semaine terminée.
- ☐ Exposition simultanée maximale : **3 %**, tous facteurs confondus.
- ☐ Une position par facteur de risque (dollar, indices, taux, matières
  premières).

**Après un drawdown**

- ☐ Taille divisée par deux jusqu'à trois trades gagnants consécutifs.
- ☐ Relecture du journal avant de reprendre.
- ☐ Aucune modification de méthode pendant le drawdown : on ne change pas de
  plan en pleine tempête.

```schema
   Risque/trade   Série de 10 pertes   Retour nécessaire
      0,5 %             −4,9 %              +5,2 %
      1   %             −9,6 %             +10,6 %
      2   %            −18,3 %             +22,4 %
      5   %            −40,1 %             +67,0 %
```

::: memo
➡ 1 % par trade ➡ −3 R par jour ➡ −6 R par semaine ➡ Chiffres écrits, jamais négociés
:::

## Checklist 7 — Avant d'appuyer sur BUY ou SELL

*Les dix secondes les plus rentables de votre journée. À lire à voix haute.*

```schema
   ╔═══════════════════════════════════════════════════════════╗
   ║  1. Mon biais du jour va-t-il dans ce sens ?         ☐    ║
   ║  2. Suis-je du bon côté de l'équilibre ?             ☐    ║
   ║  3. Quelle liquidité vient d'être prise ?            ☐    ║
   ║  4. Quelle liquidité est-ce que je vise ?            ☐    ║
   ║  5. Y a-t-il eu un CHoCH avec déplacement ?          ☐    ║
   ║  6. Où est mon stop, exactement ?                    ☐    ║
   ║  7. Ma taille est-elle calculée ?                    ☐    ║
   ║  8. Mon ratio est-il d'au moins 1:2 ?                ☐    ║
   ║  9. Suis-je dans une Kill Zone ?                     ☐    ║
   ║ 10. Est-ce que je prends ce trade par plan,          ☐    ║
   ║     ou parce que je m'ennuie / je veux me refaire ?       ║
   ╚═══════════════════════════════════════════════════════════╝
```

- ☐ Les dix réponses sont satisfaisantes → j'exécute.
- ☐ Une seule ne l'est pas → je n'exécute pas, et je note pourquoi.

::: danger
La question 10 est la plus importante des dix. C'est la seule à laquelle le
graphique ne peut pas répondre, et c'est celle qui explique la majorité des
pertes évitables.
:::

## Checklist 8 — Fin de journée

*Quinze minutes, tous les soirs. C'est ici que la progression se fabrique.*

**Résultat**

- ☐ Résultat du jour noté **en R**, pas en euros.
- ☐ Nombre de trades pris, et nombre de trades **prévus**.
- ☐ Combien étaient conformes au plan ? (le seul chiffre qui compte vraiment)

**Qualité**

- ☐ Ai-je respecté mon biais du matin ?
- ☐ Ai-je respecté mes limites de risque ?
- ☐ Ai-je pris un trade hors plan ? Lequel, et pourquoi ?
- ☐ Ai-je déplacé un stop ? Ai-je coupé un gain trop tôt ?

**Marché**

- ☐ Quelle liquidité a été prise aujourd'hui ?
- ☐ Quelle liquidité reste pour demain ?
- ☐ Les niveaux de demain sont-ils tracés ? (PDH, PDL, clôture, range asiatique
  à venir)

**Fermeture**

- ☐ Positions intraday clôturées ou consciemment conservées.
- ☐ Captures d'écran des trades du jour enregistrées.
- ☐ Plateforme fermée. **La journée est finie.**

::: memo
➡ Résultat en R ➡ Conformité au plan ➡ Niveaux de demain ➡ Plateforme fermée
:::

## Checklist 9 — Journal de trading

*Le modèle de fiche à remplir pour chaque trade. Deux minutes avant, deux
minutes après.*

**À remplir AVANT l'entrée**

| Champ | Exemple |
|---|---|
| Date et heure | 12/03, 09 h 47 |
| Instrument | EURUSD |
| Session | Londres |
| Biais du jour | Haussier |
| Setup | Purge PDL + CHoCH M15 + FVG |
| Zone | FVG M15 1,0842–1,0848 |
| Entrée | 1,0845 |
| Stop | 1,0832 (sous la mèche de purge) |
| Objectif 1 | 1,0871 (1:2) |
| Objectif 2 | 1,0898 (EQH) |
| Risque | 1 % — 0,4 lot |
| Pourquoi ce trade (une phrase) | « Discount, liquidité prise, structure retournée » |

**À remplir APRÈS la sortie**

| Champ | Exemple |
|---|---|
| Sortie | 1,0871 puis 1,0893 |
| Résultat | +2,6 R |
| Conforme au plan ? | Oui |
| Émotion pendant | Calme, aucune envie de sortir tôt |
| Erreur commise | Aucune / entrée 3 pips trop haut |
| Leçon | Attendre le milieu du FVG, pas le bord |
| Capture d'écran | ✔ |

**Revue hebdomadaire — le dimanche, 30 minutes**

- ☐ Espérance en R par setup (lequel gagne réellement de l'argent ?)
- ☐ Espérance par session et par heure (à quelle heure suis-je mauvais ?)
- ☐ Taux de conformité au plan (objectif : plus de 90 %)
- ☐ Les trois erreurs les plus fréquentes du mois
- ☐ **Une seule règle à corriger** pour la semaine suivante

::: retenir Le principe du journal
Un journal sans revue est une perte de temps. La valeur n'est pas dans
l'écriture, elle est dans la relecture : c'est en comparant cinquante fiches
qu'on découvre que tous les trades pris avant 09 h, ou après une perte, ont une
espérance négative. Une règle horaire, une règle de pause : le mois suivant est
transformé.
:::

::: erreur Les erreurs de checklist
- Cocher mentalement au lieu de cocher réellement.
- Adapter la checklist au trade au lieu d'adapter le trade à la checklist.
- Sauter la checklist « juste cette fois, parce que le setup est évident ».
- Remplir le journal une fois par semaine, de mémoire.
- Noter les résultats en euros : cela transforme l'analyse en émotion.
:::

::: resume Tome 4 — le résumé en une page
Neuf checklists, trois moments. **Avant la séance** : le biais du jour en trois
lignes écrites (direction, cible, invalidation) et l'analyse HTF. **Pendant** :
liquidité, entrée, sortie, risque, et surtout les dix questions avant de cliquer
— dont la dixième, la seule que le graphique ne peut pas trancher : est-ce que
je prends ce trade par plan, ou par ennui ? **Après** : le bilan du soir en R,
la conformité au plan, les niveaux de demain, et la fiche de journal remplie
pendant que le souvenir est frais. Aucune de ces listes ne demande de talent.
Elles demandent seulement d'être cochées vraiment — c'est la différence entre un
trader régulier et quelqu'un qui possède la même méthode sans les mêmes
résultats.
:::

# Les corrélations du Gold

L'or ne bouge jamais seul. Il fait partie d'un système. Savoir ce que font les
autres actifs, c'est avoir un temps d'avance sur le vôtre.

Deux chapitres : les cinq corrélations à connaître, puis comment réagir quand
elles se cassent.

## Les cinq corrélations à connaître

*Cinq graphiques, cinq questions, une lecture complète du marché.*

### 📌 Pourquoi ce chapitre compte

Un trader du Gold qui ne regarde que l'or est aveugle d'un œil. Les informations
arrivent souvent d'abord sur les obligations ou sur le dollar, et seulement
ensuite sur l'or.

### 💡 L'explication simple

```schema
   ┌─────────────┬──────────┬────────────────────────────────────────┐
   │ ACTIF       │ RELATION │ POURQUOI                               │
   ├─────────────┼──────────┼────────────────────────────────────────┤
   │ DXY         │ INVERSE  │ Cotation + signal macro                │
   │ Obligations │ INVERSE  │ Concurrent porteur d'intérêts          │
   │   (rendement)│         │                                        │
   │ S&P 500     │ VARIABLE │ Dépend du régime : liquidité ou peur   │
   │ Bitcoin     │ VARIABLE │ Même sensibilité à la liquidité        │
   │ Pétrole     │ FAIBLE + │ Canal inflation, pas relation directe  │
   └─────────────┴──────────┴────────────────────────────────────────┘
```

**1. Gold / DXY — inverse, forte.** Traitée au chapitre 5. C'est la corrélation
la plus fiable pour l'intraday. Règle : dollar en hausse = vent de face.

**2. Gold / rendements obligataires — inverse, très forte.** C'est la
corrélation la plus **fondamentale**. Attention : c'est le rendement **réel**
qui compte, pas le nominal. Le rendement réel est le meilleur prédicteur de la
tendance de fond de l'or.

**3. Gold / S&P 500 — variable.** C'est la plus mal comprise.

| Régime | Comportement | Explication |
|---|---|---|
| Liquidité abondante, taux bas | Les deux **montent ensemble** | Tout monte quand l'argent est gratuit |
| Panique, krach | L'or baisse d'abord, puis monte | Ventes forcées puis refuge |
| Stagflation | Or ↑, actions ↓ | L'or gagne, les actions souffrent |
| Croissance saine, taux stables | Actions ↑, or plat | L'argent va vers le rendement |

Il n'existe donc **pas** de corrélation stable entre l'or et les actions.
Cherchez le régime, pas la corrélation.

**4. Gold / Bitcoin — variable, souvent positive.** Les deux réagissent à la
liquidité mondiale et à la défiance monétaire. Mais le Bitcoin est un actif à
fort bêta : en cas de choc de liquidité, il est vendu **en premier**, alors que
l'or finit par jouer son rôle de refuge. Le Bitcoin n'est pas « l'or
numérique » à l'échelle d'une semaine de trading.

**5. Gold / pétrole — faible, indirecte.** Le pétrole agit sur l'or par
l'inflation : pétrole cher → inflation → réaction de la Fed → taux réels. Le
lien passe donc par deux intermédiaires, ce qui le rend lâche. Le pétrole est
en revanche un excellent **thermomètre géopolitique**.

### 📊 Exemple concret

```schema
   09 h 15   Le rendement du 10 ans commence à baisser sans nouvelle apparente
   09 h 22   Le DXY casse un support intraday
   09 h 26   L'or accélère à la hausse et casse son plus haut de la veille
   ➜ le signal était visible 10 minutes avant, sur un autre graphique
```

L'or est souvent le **dernier** à bouger, parce qu'il est la conséquence des
deux autres. C'est exactement ce qui vous donne un avantage.

::: astuce
Configurez un écran à quatre graphiques : **XAUUSD · DXY · US10Y · S&P 500**.
C'est le tableau de bord minimal du trader du Gold. Vous verrez arriver la
majorité des mouvements avant qu'ils n'atteignent l'or.
:::

### 🥇 Impact sur le Gold

| Combinaison observée | Lecture | Biais or |
|---|---|---|
| DXY ↓ + rendements ↓ | Alignement parfait | **Haussier fort** |
| DXY ↑ + rendements ↑ | Double vent de face | **Baissier fort** |
| DXY ↑ + rendements ↓ | Contradiction → suivre les rendements | Haussier prudent |
| DXY ↓ + rendements ↑ | Contradiction → prudence | Neutre |
| Actions ↓ + rendements ↓ + or ↑ | Fuite vers la qualité | **Haussier** |
| Actions ↓ + or ↓ + DXY ↑ | Panique de liquidité | Baissier court terme, haussier ensuite |

### 🏛️ Ce que regarde un professionnel

L'ordre de lecture, toujours le même :

```schema
   1. Rendements réels    ── le moteur
   2. Dollar              ── l'amplificateur
   3. Actions / VIX       ── le régime de risque
   4. Pétrole             ── le canal inflation et géopolitique
   5. OR                  ── la conséquence  ◄── on le regarde en DERNIER
```

::: pro
Le réflexe institutionnel : l'or n'est jamais le premier graphique ouvert le
matin. Il est le dernier. On construit d'abord la vue macro, on ouvre l'or
ensuite pour trouver le prix d'exécution.
:::

::: erreur
**L'erreur classique :** croire que l'or et les actions sont toujours inversés.
Dans un régime de liquidité abondante, ils montent ensemble pendant des mois.
:::

### ✅ À retenir absolument

- Cinq corrélations : DXY (inverse, forte), rendements (inverse, très forte),
  actions (variable), Bitcoin (variable), pétrole (faible et indirecte).
- La corrélation la plus fondamentale est celle des **rendements réels**.
- Il n'existe pas de relation stable entre l'or et les actions : cherchez le
  régime.
- Le Bitcoin n'est pas un refuge à court terme.
- L'or bouge souvent **en dernier** : les autres graphiques vous préviennent.

::: fiche Fiche pratique — Le tableau de bord à 4 écrans
- ☐ XAUUSD (l'instrument tradé)
- ☐ DXY (le filtre immédiat)
- ☐ US10Y (le moteur de fond)
- ☐ S&P 500 ou VIX (le régime de risque)
- ☐ Avant chaque entrée : les trois autres écrans confirment-ils mon sens ?
- ☐ Si deux sur trois disent non → pas de trade.
:::

## Quand les corrélations se cassent

*Une corrélation qui se rompt n'est pas un bug. C'est une information.*

### 📌 Pourquoi ce chapitre compte

Les périodes où « plus rien ne fonctionne » sont précisément celles où les
tendances les plus fortes démarrent. Savoir les lire est ce qui sépare un
trader qui subit d'un trader qui anticipe.

### 💡 L'explication simple

Une corrélation naît d'un mécanisme. Quand un mécanisme **plus puissant**
apparaît, la corrélation habituelle est écrasée.

```schema
   MÉCANISME HABITUEL              MÉCANISME PLUS FORT              RÉSULTAT
   dollar ↑ ──► or ↓        <      achats de banques centrales      les deux ↑
   rendements ↑ ──► or ↓    <      défiance sur la dette            les deux ↑
   actions ↓ ──► or ↑       <      panique de liquidité             les deux ↓
   inflation ↑ ──► or ↑     <      la Fed durcit plus vite          or ↓
```

La règle de résolution est toujours la même :

::: retenir La hiérarchie de décision
Quand deux signaux se contredisent, remontez d'un niveau :

**1. Taux réels** — le moteur.
**2. Dollar** — un résumé, imparfait.
**3. Flux** — ETF, banques centrales, positionnement.
**4. Technique** — le timing.

Le niveau 1 gagne toujours contre le niveau 2.
:::

### 📊 Exemple concret

| Situation observée | Réaction naïve | Lecture correcte |
|---|---|---|
| Or ↑ et dollar ↑ | « la corrélation est morte » | Défiance systémique : biais haussier renforcé |
| Or ↑ et rendements ↑ | « c'est illogique » | Prime de risque souverain : haussier |
| Or ↓ et actions ↓ | « l'or ne protège pas » | Panique de liquidité : phase 2 d'une crise |
| Or ↓ et inflation ↑ | « le marché est irrationnel » | La Fed durcit plus vite que l'inflation |

Dans les quatre cas, rien d'irrationnel. Simplement un mécanisme plus fort à
l'œuvre.

### 🥇 Impact sur le Gold

| Rupture | Ce qu'elle annonce | Ce qu'il faut faire |
|---|---|---|
| Or et dollar montent ensemble | Défiance systémique | Rester haussier, ignorer le DXY |
| Or monte avec les rendements | Doute sur la dette souveraine | Biais haussier de fond |
| Or baisse avec les actions | Crise de liquidité en cours | Réduire, attendre l'intervention |
| Or ignore une bonne nouvelle | Un acheteur structurel absorbe | Signal de force |
| Or ignore une mauvaise nouvelle | Un vendeur structurel absorbe | Signal de faiblesse |

Les deux dernières lignes sont précieuses : **la non-réaction est un signal**.
Un actif qui refuse de baisser sur une mauvaise nouvelle est un actif que
quelqu'un accumule.

### 🏛️ Ce que regarde un professionnel

- **Le rendement réel à 10 ans**, systématiquement, dès qu'une contradiction
  apparaît.
- **Les flux ETF et le positionnement**, pour savoir qui absorbe.
- **La non-réaction**, qu'un pro considère comme l'un des signaux les plus
  fiables du marché.

::: pro
La phrase entendue sur les desks : « il ne baisse pas alors qu'il devrait ».
C'est souvent le meilleur signal haussier disponible, et il ne figure sur aucun
indicateur.
:::

::: erreur
**L'erreur classique :** conclure que « le marché est manipulé » ou « plus rien
n'a de sens », et arrêter d'analyser. Une corrélation rompue est une invitation
à chercher le mécanisme dominant, pas à abandonner.
:::

### ✅ À retenir absolument

- Une corrélation qui se casse signale qu'un mécanisme plus puissant est
  apparu.
- Hiérarchie de résolution : taux réels > dollar > flux > technique.
- Or + dollar en hausse = défiance systémique = haussier.
- Or + rendements en hausse = risque souverain = haussier.
- La non-réaction à une nouvelle est l'un des signaux les plus fiables.

::: fiche Fiche pratique — Quand plus rien ne colle
- ☐ Ouvrir le rendement **réel** à 10 ans : que dit-il ?
- ☐ Identifier le mécanisme dominant parmi les quatre du tableau.
- ☐ Vérifier les flux : qui absorbe ? (ETF, positionnement)
- ☐ Observer les non-réactions : l'or ignore-t-il une nouvelle qui aurait dû le
  faire bouger ?
- ☐ En cas de doute persistant : réduire la taille, raccourcir les objectifs,
  attendre la clarification.
:::

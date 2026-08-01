# Le dollar

L'or est coté en dollars. Cette phrase paraît anodine : elle est en réalité la
clé de la moitié des mouvements du XAUUSD.

Deux chapitres. Le premier explique le mécanisme. Le second explique les
moments — nombreux — où il cesse de fonctionner.

## Le DXY, le miroir de l'or

*Quand le dollar monte, l'or baisse. Comprenez pourquoi, pas seulement que.*

### 📌 Pourquoi ce chapitre compte

Le DXY est l'indicateur le plus utile et le plus immédiat pour un trader du
Gold. Il se lit en trois secondes, il se met à jour en continu, et il explique
une large part des mouvements intraday.

Si vous ne devez ajouter qu'un seul graphique à votre écran, c'est celui-là.

### 💡 L'explication simple

Le DXY mesure la valeur du dollar face à un panier de six devises :

| Devise | Poids |
|---|---|
| Euro | 57,6 % |
| Yen japonais | 13,6 % |
| Livre sterling | 11,9 % |
| Dollar canadien | 9,1 % |
| Couronne suédoise | 4,2 % |
| Franc suisse | 3,6 % |

Retenez la première ligne : **le DXY est à 58 % un EURUSD inversé**. Quand
quelqu'un dit « le dollar monte », il dit surtout « l'euro baisse ».

Maintenant, le mécanisme avec l'or. Il y a deux couches.

**Couche 1 — l'effet mécanique de la cotation.** L'once d'or a une valeur
mondiale, mais elle est affichée en dollars. Si le dollar se renforce, il faut
moins de dollars pour acheter la même once. Le prix affiché baisse, alors même
que la valeur de l'or n'a pas changé pour un acheteur européen ou japonais.

```schema
   Une once vaut 2 000 $        et      1 € = 1,10 $   ──►  1 818 € l'once
   Le dollar se renforce                1 € = 1,00 $
   Pour que l'once vaille toujours 1 818 € ──► elle doit coter 1 818 $
   Le prix en dollars BAISSE sans que la valeur ait bougé.
```

**Couche 2 — l'effet du signal.** Un dollar qui monte traduit presque toujours
une même cause : des taux américains attractifs, une économie américaine
solide, ou une fuite vers la sécurité en dollars. Ces trois causes sont
*également* négatives pour l'or. Le dollar n'est donc pas seulement un taux de
conversion : c'est un résumé de la macro.

C'est pourquoi la relation est bien plus forte que le simple effet de change.

```svg
<svg viewBox="0 0 640 300" role="img" aria-label="Relation inverse entre le dollar et l'or">
  <text x="20" y="24" font-family="var(--sans)" font-size="13" font-weight="700" fill="var(--encre)">La relation type : deux courbes en miroir</text>
  <line x1="50" y1="60" x2="50" y2="250" stroke="var(--trait)" stroke-width="1"/>
  <line x1="50" y1="250" x2="620" y2="250" stroke="var(--trait)" stroke-width="1"/>
  <path d="M50 100 C 130 90, 180 130, 250 145 S 380 200, 460 185 S 570 130, 620 120"
        fill="none" stroke="var(--bleu)" stroke-width="2.6"/>
  <path d="M50 210 C 130 220, 180 180, 250 165 S 380 110, 460 125 S 570 180, 620 190"
        fill="none" stroke="var(--or)" stroke-width="2.6"/>
  <circle cx="250" cy="145" r="3.5" fill="var(--bleu)"/>
  <circle cx="250" cy="165" r="3.5" fill="var(--or)"/>
  <text x="70" y="88" font-family="var(--sans)" font-size="11.5" font-weight="700" fill="var(--bleu)">DXY (dollar)</text>
  <text x="70" y="232" font-family="var(--sans)" font-size="11.5" font-weight="700" fill="var(--or)">XAUUSD (or)</text>
  <text x="335" y="278" text-anchor="middle" font-family="var(--sans)" font-size="11" fill="var(--encre-3)">Quand l'un monte, l'autre baisse — la plupart du temps</text>
</svg>
```

### 📊 Exemple concret

Séance ordinaire, 14 h 30 heure de Paris. Les chiffres américains sortent
au-dessus des attentes.

```schema
   14 h 30   données meilleures que prévu
   14 h 30   les taux à 2 ans montent      ──► le dollar devient plus attractif
   14 h 31   DXY +0,4 %                    ──► XAUUSD −18 $
   14 h 45   DXY se stabilise              ──► l'or se stabilise aussi
   15 h 30   DXY rend la moitié            ──► l'or récupère la moitié
```

Vous n'avez pas eu besoin de comprendre le chiffre. Vous avez eu besoin de
regarder le dollar.

::: astuce
Placez le DXY en petit graphique à côté de votre XAUUSD, en H1 et en M15.
Règle simple : **si le DXY casse un niveau important à la hausse, votre achat
d'or attend.** Cette seule habitude évite une grande partie des entrées à
contretemps.
:::

### 🥇 Impact sur le Gold

| Situation du DXY | Effet attendu sur l'or | Fiabilité |
|---|---|---|
| DXY monte, taux montent | **Baisse** | Très élevée |
| DXY baisse, taux baissent | **Hausse** | Très élevée |
| DXY monte par fuite vers la sécurité | Baisse limitée, voire nulle | Moyenne |
| DXY plat | L'or suit alors les taux réels et les flux | — |
| DXY et or montent ensemble | Signal fort de stress ou de défiance | Rare, à prendre au sérieux |

**Quand l'effet est différent — le cas le plus important du livre.** Si le
dollar **et** l'or montent en même temps, ne concluez pas que la corrélation
est cassée : concluez qu'il se passe quelque chose de plus grave. Les deux
refuges montent ensemble lorsque le marché doute du système lui-même (crise
bancaire, crise de dette, guerre majeure). Ces périodes produisent les plus
fortes hausses de l'or.

### 🏛️ Ce que regarde un professionnel

Un pro ne regarde jamais le DXY seul. Il regarde **pourquoi** il bouge :

1. **Le dollar monte parce que les taux américains montent** → très négatif pour
   l'or (double effet : change + coût d'opportunité).
2. **Le dollar monte parce que l'euro s'effondre** (problème européen) → effet
   modéré sur l'or, la cause n'est pas américaine.
3. **Le dollar monte parce que le monde a peur** → effet ambigu : les deux
   refuges se disputent les flux.

Cette distinction est ce qui sépare une lecture de débutant d'une lecture
professionnelle.

::: pro
Sur un desk, la question n'est pas « où va le dollar ? » mais « quel moteur
pousse le dollar aujourd'hui ? ». Le même mouvement du DXY n'a pas les mêmes
conséquences selon qu'il vient des taux, d'un problème étranger ou d'une
panique.
:::

::: erreur
**L'erreur classique :** traiter la relation or/dollar comme une loi mécanique
à −100 %. Elle est forte, mais variable : sur certaines périodes elle est très
étroite, sur d'autres presque inexistante. Utilisez-la comme un **filtre**, pas
comme un signal d'entrée.
:::

### ✅ À retenir absolument

- Le DXY est à 58 % un EURUSD inversé.
- Deux effets se cumulent : la cotation en dollars, et le signal macro que le
  dollar transmet.
- Dollar en hausse = vent de face pour l'or. Dollar en baisse = vent arrière.
- Il faut toujours identifier **pourquoi** le dollar bouge : taux, problème
  étranger, ou panique.
- Dollar et or qui montent ensemble = signal de stress systémique, à prendre
  très au sérieux.

::: fiche Fiche pratique — Le contrôle DXY avant chaque trade
- ☐ Le DXY est-il en tendance haussière ou baissière sur H4 ?
- ☐ Vient-il de casser un niveau important ? Dans quel sens ?
- ☐ Quel moteur ? (taux américains / faiblesse étrangère / peur)
- ☐ Mon trade sur l'or va-t-il **contre** le DXY ? Si oui : taille réduite ou
  attente.
- ☐ Cas particulier : DXY et or montent ensemble → chercher la cause
  systémique, ne pas vendre l'or mécaniquement.
:::

## Quand la corrélation or / dollar se casse

*Elle se casse souvent. Savoir la reconnaître vaut mieux que d'y croire.*

### 📌 Pourquoi ce chapitre compte

Le trader qui applique « dollar haut = or bas » sans nuance finit par vendre de
l'or au pire moment : exactement quand la relation s'inverse, c'est-à-dire
quand la tendance de fond démarre.

### 💡 L'explication simple

La corrélation or/dollar n'est pas une loi physique. C'est une **régularité
statistique** née d'un mécanisme. Quand le mécanisme change, la régularité
disparaît.

Quatre situations la cassent :

```schema
   1. CRISE SYSTÉMIQUE     ── les deux refuges montent ensemble
   2. ACHATS DE BANQUES     ── un acheteur insensible au prix absorbe l'effet
      CENTRALES                 dollar
   3. CHOC ÉTRANGER         ── le dollar monte à cause de l'euro ou du yen,
                               pas des taux américains
   4. INFLATION ÉLEVÉE      ── les deux montent : le dollar face aux autres
      PARTOUT                   monnaies, l'or face à toutes
```

Le point commun de ces quatre cas : le dollar monte pour une raison **qui ne
concerne pas le coût d'opportunité de l'or**. Or c'est ce coût — le taux réel —
qui compte vraiment. Le dollar n'était qu'un raccourci.

### 📊 Exemple concret

::: histoire Le cas des grandes hausses simultanées
Il arrive régulièrement que l'or établisse de nouveaux records alors que le
dollar reste ferme, voire se renforce. Les commentateurs annoncent alors la
« fin de la corrélation ».

En réalité, il ne s'est rien passé d'anormal. Trois forces se sont
additionnées : des banques centrales qui achètent de l'or sans se soucier du
prix pour diversifier leurs réserves, une inquiétude sur la dette publique
américaine, et une demande de couverture contre le risque géopolitique. Ces
trois forces poussent l'or à la hausse indépendamment du niveau du dollar.

Le dollar, lui, montait parce que les États-Unis résistaient mieux que l'Europe
et le Japon. Un moteur **étranger**, pas un moteur de taux réels américains.

Résultat : les deux montent. La corrélation n'est pas morte, elle est
temporairement **dominée** par un facteur plus fort.
:::

### 🥇 Impact sur le Gold

| Cas de rupture | Ce qui se passe | Ce qu'il faut faire |
|---|---|---|
| Crise systémique | Or et dollar montent ensemble | Suivre l'or à la hausse, ignorer le DXY |
| Achats massifs de banques centrales | L'or absorbe la hausse du dollar | Biais haussier de fond, corrections achetées |
| Faiblesse étrangère (euro, yen) | DXY monte, or peu affecté | Ne pas vendre l'or sur le seul DXY |
| Inflation mondiale élevée | Les deux montent | Suivre les taux réels, pas le dollar |
| Retour à la normale | Corrélation inverse rétablie | Le filtre DXY redevient fiable |

**Le point décisif.** Quand la corrélation se casse, **remontez d'un cran** : le
dollar n'était qu'un intermédiaire, la vraie variable est le taux réel
américain. Un dollar qui monte avec des taux réels qui baissent est haussier
pour l'or. C'est le cas de figure que la plupart des traders ne voient pas.

### 🏛️ Ce que regarde un professionnel

Le pro utilise une hiérarchie stricte :

```schema
   NIVEAU 1  Taux réels américains       ◄── le vrai moteur
   NIVEAU 2  Dollar (DXY)                ◄── un résumé, utile mais imparfait
   NIVEAU 3  Flux (ETF, banques centrales, positionnement)
   NIVEAU 4  Sentiment et technique      ◄── le timing
```

Quand les niveaux 1 et 2 se contredisent, **le niveau 1 gagne**. Toujours.

::: pro
Le contrôle que fait un gérant quand or et dollar montent ensemble : ouvrir le
graphique du rendement réel à 10 ans (obligation indexée sur l'inflation, TIPS).
S'il baisse, tout est cohérent, l'or est simplement porté par son vrai moteur.
:::

::: erreur
**L'erreur classique :** conclure « la corrélation est cassée, donc plus rien
n'a de sens » et arrêter d'analyser. Une corrélation qui se casse est une
**information** : elle indique qu'une force plus puissante est à l'œuvre. C'est
souvent le début des plus grands mouvements.
:::

### ✅ À retenir absolument

- La corrélation or/dollar est une régularité, pas une loi.
- Quatre causes de rupture : crise systémique, achats de banques centrales,
  faiblesse étrangère, inflation mondiale.
- Quand elle se casse, remontez au **taux réel** : c'est lui, le vrai moteur.
- Or et dollar en hausse simultanée = signal de défiance envers le système, pas
  une anomalie à ignorer.
- Un DXY qui monte à cause d'un problème européen ne justifie pas de vendre
  l'or.

::: fiche Fiche pratique — Que faire quand la corrélation se casse
- ☐ Vérifier le rendement réel à 10 ans : monte-t-il ou baisse-t-il ?
- ☐ Identifier le moteur du dollar : taux américains, ou faiblesse étrangère ?
- ☐ Y a-t-il un stress visible ? (indice de volatilité, écarts de crédit,
  obligations d'État)
- ☐ Si taux réels en baisse + dollar en hausse → **rester haussier sur l'or**.
- ☐ Si taux réels en hausse + dollar en hausse → biais baissier confirmé,
  double vent de face.
:::

## Chapitre 24 — Les corrélations

### Le principe

Deux actifs corrélés ne sont pas deux positions : ce sont deux expressions du
même pari. Ignorer cela est la cause la plus fréquente de destruction rapide
d'un compte pourtant discipliné.

### La carte des corrélations utiles

| Couple | Sens | Raison |
|---|---|---|
| DXY ↔ EURUSD | Négatif fort | L'euro pèse 57,6 % de l'indice |
| DXY ↔ Or | Négatif | L'or est coté en dollars |
| Or ↔ Taux réels | Négatif fort | L'or ne rapporte aucun intérêt |
| Actions ↔ Rendements | Variable | Négatif en régime d'inflation, positif en régime de croissance |
| Pétrole ↔ CAD | Positif | Économie exportatrice |
| Or ↔ Argent | Positif | L'argent amplifie, avec plus de volatilité |
| S&P ↔ Nasdaq | Positif fort | Leur divergence est un signal (SMT) |
| USDJPY ↔ Rendement US 10 ans | Positif | Différentiel de taux |
| Bitcoin ↔ Nasdaq | Positif en régime de liquidité | Même sensibilité au risque |

### Le risque par facteur

```schema
   FACTEUR DOLLAR
   ├── long EURUSD    1 %  ┐
   ├── long GBPUSD    1 %  ├── exposition réelle : 3 % sur UN pari
   └── short USDCHF   1 %  ┘
   ➜ trois lignes, un seul risque, triplé
```

Règle pratique : **une position par facteur**. Si vous voulez doubler, doublez
la taille d'une ligne, ne multipliez pas les lignes.

### La divergence comme signal (SMT)

Quand deux actifs normalement corrélés cessent de se confirmer, l'un des deux
ment. C'est le principe 4 de Dow, appliqué au trading moderne.

```schema
   EURUSD  ╲╲╲▼  nouveau plus bas
   GBPUSD  ╲╲╲   pas de nouveau plus bas
   ➜ la baisse de l'EURUSD est une purge, pas une tendance
```

### Le piège des régimes

Les corrélations ne sont pas des lois : elles changent de régime. En crise, tout
se corrèle à 1 et la diversification disparaît exactement quand vous en avez
besoin.

::: retenir
- Compter le risque par **facteur**, pas par ligne.
- Une position par facteur, jamais trois.
- La divergence entre corrélés est un signal (SMT).
- Les corrélations se brisent en crise : ne jamais s'y fier aveuglément.
:::

::: erreur
- Croire diversifier en ouvrant cinq paires contenant toutes le dollar.
- Utiliser une corrélation historique sans vérifier sa valeur récente.
- Trader une divergence sans niveau ni prise de liquidité.
- Oublier que l'or suit les **taux réels**, pas l'inflation nominale.
:::

::: resume
**Corrélations en une page.** Les marchés sont un système : le dollar, les
taux, les matières premières et les indices bougent ensemble selon des
relations stables mais changeantes. Deux conséquences pratiques. D'abord, votre
risque se compte par facteur : trois positions dollar ne font qu'un seul pari,
triplé. Ensuite, la rupture d'une corrélation est une information — quand deux
actifs qui se suivent cessent de se confirmer, celui qui n'a pas fait le nouvel
extrême indique généralement la vraie direction. En crise, toutes ces relations
convergent vers 1 : la diversification s'évapore au pire moment.
:::

## Chapitre 25 — La macroéconomie

*Ce chapitre est le résumé opérationnel. Le détail complet — indicateur par
indicateur, actif par actif — se trouve au Tome 3.*

### Les deux variables qui commandent tout

```schema
                    INFLATION
                  ↑           ↓
   CROISSANCE ↑   matières    ACTIONS
                  premières   (idéal)
              ↓   stagflation OBLIGATIONS
                  (or, cash)  (défensives)
```

Toute la macroéconomie de marché tient dans ce carré : où en sont la croissance
et l'inflation, et surtout **dans quelle direction évoluent-elles**.

### La chaîne de transmission

```schema
   Inflation ──► anticipations de taux ──► taux réels ──► DOLLAR
        │                                       │
        │                                       ├──► OR (inverse)
        │                                       ├──► ACTIONS (inverse)
        └──► politique des banques centrales ───┴──► OBLIGATIONS (inverse)
```

Retenez la variable centrale : **le taux réel** (taux nominal moins inflation
anticipée). C'est lui qui explique l'or, les valeurs de croissance et le dollar
— pas l'inflation brute.

### Ce qui compte réellement : la surprise

Le marché valorise les anticipations. Un chiffre « mauvais » mais meilleur que
prévu fait monter les actifs risqués. Ne lisez jamais un chiffre sans son
consensus.

| Publication | Ce qu'il faut regarder |
|---|---|
| CPI | L'écart au consensus, surtout sur le *core* |
| NFP | Le salaire horaire autant que le nombre d'emplois |
| FOMC | Le ton de la conférence, pas la décision |
| PMI | Le franchissement du seuil de 50 |

### La règle d'or opérationnelle

**On ne trade pas l'annonce, on trade la structure qu'elle laisse.** Attendez 15
à 30 minutes, laissez le déséquilibre se former, entrez sur le retour.

::: retenir
- Deux variables : croissance et inflation, en **direction** plus qu'en niveau.
- Le taux réel est la variable pivot.
- Seule la surprise par rapport au consensus déplace le marché.
- On ne trade pas la publication, on trade le FVG qu'elle laisse.
:::

::: erreur
- Raisonner « inflation haute = marché baisse » sans regarder les attentes.
- Tenir une position à taille normale pendant une publication majeure.
- Croire que l'or protège de l'inflation à court terme (il suit les taux
  réels).
- Confondre baisse de taux et bonne nouvelle : en récession, c'est un signal
  d'alarme.
:::

::: resume
**Macro en une page.** Les marchés valorisent des flux futurs actualisés à un
taux. Ce taux dépend de l'inflation anticipée et de la politique de la banque
centrale. D'où la chaîne : inflation → anticipations de taux → taux réels →
dollar → tout le reste. Positionnez le moment du cycle dans le carré
croissance/inflation, suivez la direction plutôt que le niveau, et n'oubliez
jamais que seul l'écart au consensus fait bouger les prix. En pratique, la
macro sert à choisir le sens et à éviter les mauvaises heures ; l'exécution
reste technique.
:::

## Chapitre 26 — L'analyse fondamentale

### Ce qu'elle est, et ce qu'elle n'est pas

L'analyse fondamentale cherche la **valeur** ; l'analyse technique cherche le
**moment**. Elles ne sont pas concurrentes : elles répondent à des questions
différentes.

```schema
   FONDAMENTAL  ──►  QUOI et POURQUOI   (horizon : semaines/mois)
   TECHNIQUE    ──►  OÙ et QUAND        (horizon : heures/jours)
   RISQUE       ──►  COMBIEN            (horizon : toujours)
```

### Par classe d'actifs

| Actif | Ce qui le pilote réellement |
|---|---|
| **Forex** | Différentiel de taux, balance commerciale, flux de capitaux, politique monétaire relative |
| **Indices** | Bénéfices attendus, taux d'actualisation, primes de risque, rachats d'actions |
| **Or** | Taux réels, dollar, achats des banques centrales, demande refuge |
| **Pétrole** | Offre (OPEP+, stocks) et demande (croissance mondiale), géopolitique |
| **Bitcoin** | Liquidité globale, appétit pour le risque, flux ETF, cycle de halving |
| **Obligations** | Inflation anticipée, politique monétaire, offre de dette |

### La règle du consensus

Un fondamental connu est un fondamental **déjà dans le prix**. Ce qui déplace
les marchés, c'est la révision des anticipations, pas la donnée elle-même.

D'où l'adage : *buy the rumour, sell the news* — acheter l'anticipation, vendre
la confirmation.

### Comment l'intégrer sans se disperser

Une page par semaine suffit :

1. Que fait la FED ? (restrictive, neutre, accommodante)
2. Où va l'inflation ? (accélère, ralentit)
3. Que fait le dollar ? (tendance hebdomadaire)
4. Où sont les taux réels ? (montent, baissent)
5. Y a-t-il un événement majeur cette semaine ?

Ces cinq lignes cadrent l'ensemble de vos trades de la semaine.

::: retenir
- Le fondamental donne la direction, la technique donne le timing.
- Ce qui compte est la **révision** des anticipations, pas la donnée.
- Une page par semaine suffit : cinq questions, cinq réponses.
- Un biais technique contraire au fondamental est un biais fragile.
:::

::: erreur
- Trader une news parce qu'elle est « bonne » ou « mauvaise ».
- Chercher à comprendre le fondamental d'un actif en intraday.
- Confondre une opinion économique et un plan de trade.
- Garder une position perdante en invoquant le fondamental — c'est la
  rationalisation la plus coûteuse du métier.
:::

::: resume
**Analyse fondamentale en une page.** Elle explique pourquoi un actif devrait
s'apprécier ou se déprécier sur plusieurs semaines : différentiels de taux,
bénéfices, offre et demande physiques, liquidité globale. Elle ne dit jamais
quand entrer. Son usage correct est celui d'un filtre de direction, révisé une
fois par semaine en cinq questions, à l'intérieur duquel toute l'exécution reste
technique. Sa règle la plus importante est aussi la plus contre-intuitive : ce
qui est connu est déjà dans le prix, donc seul l'écart aux attentes fait bouger
le marché.
:::

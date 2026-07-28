# Tome 3 — Macroéconomie

Ce tome est une **fiche géante**. Seize entrées macro, puis l'impact détaillé sur
six actifs. Objectif : ouvrir la bonne fiche avant une publication et savoir en
trente secondes ce qui peut arriver.

## La chaîne de causalité — à mémoriser avant tout le reste

```schema
   ÉCONOMIE (croissance, emploi, prix)
        │
        ▼
   INFLATION  ─── mesurée par CPI · PPI · PCE
        │
        ▼
   ANTICIPATIONS DE TAUX  ─── lisibles dans les futures et la courbe
        │
        ▼
   BANQUE CENTRALE (FED, BCE)  ─── taux directeur + bilan (QE/QT)
        │
        ├──► TAUX NOMINAUX ──► OBLIGATIONS (prix inverse)
        │
        ▼
   TAUX RÉELS  =  taux nominal − inflation anticipée   ◄── LA variable pivot
        │
        ├──► DOLLAR (DXY)
        │         ├──► OR (inverse)
        │         ├──► MATIÈRES PREMIÈRES (inverse)
        │         └──► ÉMERGENTS (inverse)
        │
        └──► ACTIONS · BITCOIN (inverse en régime d'inflation)
```

::: retenir La seule phrase à retenir de tout le tome
Le marché ne réagit pas au **niveau** d'un chiffre, mais à son **écart avec ce
qui était anticipé**. Un chiffre catastrophique mais meilleur que prévu fait
monter les actifs risqués.
:::

## Les seize fiches

### 1. INFLATION

**Ce que c'est.** La hausse générale et durable des prix. Elle est mesurée par
plusieurs indices ; ce qui compte est sa **trajectoire**, pas son niveau.

**Les trois types.**

| Type | Origine | Réaction de la banque centrale |
|---|---|---|
| Par la demande | Surchauffe, relance | Hausse des taux |
| Par les coûts | Énergie, salaires, chaînes d'approvisionnement | Dilemme : hausse des taux au risque de la récession |
| Par les anticipations | Croyance auto-réalisatrice | Réaction très ferme, priorité absolue |

**Impact.**

| Inflation | Taux | DXY | Or | Indices | Obligations |
|---|---|---|---|---|---|
| Accélère | ↑ | ↑ | ↓ | ↓ | ↓ |
| Ralentit | ↓ | ↓ | ↑ | ↑ | ↑ |

::: piege
L'or n'est **pas** une protection contre l'inflation à court terme. Il suit les
taux réels. En 2022, l'inflation était à 9 % et l'or a baissé, parce que les
taux réels remontaient violemment.
:::

::: memo
➡ Ce qui compte est la direction ➡ Et surtout le taux réel ➡ Jamais le niveau brut
:::

### 2. CPI — Indice des prix à la consommation

**Publication.** Mensuelle, 14 h 30 heure de Paris pour les États-Unis.
**Ce qu'on regarde.** Le *core* (hors alimentation et énergie), en variation
mensuelle, et l'écart au consensus. Le *headline* fait les titres, le *core*
fait la politique monétaire.

**Volatilité.** ★★★ — l'un des trois événements majeurs du mois.

| Résultat | Taux | DXY | Or | Indices |
|---|---|---|---|---|
| CPI > attentes | ↑ | ↑ | ↓ | ↓ |
| CPI < attentes | ↓ | ↓ | ↑ | ↑ |
| CPI = attentes | — | volatilité sans direction | — | — |

**Comment je le trade.** Aucune position à 14 h 30. J'observe la première
demi-heure, je marque le range et le FVG créés par l'expansion, et j'entre au
retour à partir de 15 h, taille réduite.

::: piege
Réaction initiale fréquemment inversée en dix minutes. Les spreads sont
multipliés par cinq et les stops subissent un slippage garanti.
:::

### 3. PPI — Indice des prix à la production

**Publication.** Mensuelle, souvent à quelques jours du CPI.
**Ce qu'on regarde.** Les prix en amont, qui annoncent le CPI à venir.
**Volatilité.** ★★ — second rang.

**Impact.** Même sens que le CPI, avec une amplitude moindre. Son intérêt
principal est de faire bouger les **anticipations** de CPI avant sa publication.

```schema
   PPI (producteurs) ──► marges ──► CPI (consommateurs) ──► taux ──► marchés
```

### 4. NFP — Emplois non agricoles

**Publication.** Premier vendredi du mois, 14 h 30 heure de Paris.
**Ce qu'on regarde.** Trois chiffres : créations d'emplois, taux de chômage, et
surtout **salaire horaire moyen** — c'est lui qui alimente l'inflation.
**Volatilité.** ★★★

| Régime | Bon chiffre d'emploi | Interprétation |
|---|---|---|
| Surchauffe inflationniste | Mauvais pour les actions | La FED restera restrictive |
| Ralentissement / récession | Bon pour les actions | L'économie tient |

C'est la subtilité principale : **la même donnée change de signe selon le
régime**. Sachez toujours dans quel régime vous êtes avant de lire le chiffre.

::: piege
Les révisions des deux mois précédents sont parfois plus importantes que le
chiffre du mois. Le marché peut monter sur un mauvais chiffre si les révisions
sont bonnes.
:::

### 5. FOMC

**Publication.** Huit fois par an, communiqué à 20 h, conférence de presse à
20 h 30 (heure de Paris). *Dot plot* quatre fois par an, minutes trois semaines
plus tard.
**Ce qu'on regarde.** Non pas la décision (souvent anticipée à 95 %), mais le
**ton** et les projections.
**Volatilité.** ★★★★ — le plus fort du calendrier.

```schema
   20 h 00  communiqué   ──► première réaction, souvent algorithmique
   20 h 30  conférence   ──► inversion complète très fréquente
   21 h 30  vrai biais   ──► on observe, on trade le lendemain
```

**Comment je le trade.** Je ne trade pas. Je note le range de la journée FOMC :
ses bornes servent de référence pour les jours suivants.

### 6. FED

**Ce que c'est.** La banque centrale américaine, double mandat : plein emploi et
stabilité des prix (cible 2 %).
**Ses outils.** Taux directeur (*Fed Funds*), bilan (QE/QT), communication
(*forward guidance*).

| Ton | Signification | DXY | Or | Actions |
|---|---|---|---|---|
| *Hawkish* (restrictif) | Taux plus hauts, plus longtemps | ↑ | ↓ | ↓ |
| *Dovish* (accommodant) | Baisses de taux à venir | ↓ | ↑ | ↑ |

::: retenir
La FED est la variable la plus puissante des marchés mondiaux. Un mot du
président déplace plus de capitaux qu'une année d'analyse technique. D'où la
règle : on ne tient pas de position à taille normale pendant qu'il parle.
:::

### 7. BCE — Banque centrale européenne

**Ce que c'est.** Mandat unique : la stabilité des prix (cible 2 %).
**Publication.** Décision à 14 h 15, conférence de presse à 14 h 45 (heure de
Paris), huit fois par an.
**Volatilité.** ★★★ sur l'euro, ★★ sur le reste.

**La particularité.** La BCE arbitre entre des économies hétérogènes : ses
décisions sont plus lentes et plus prudentes que celles de la FED. C'est le
**différentiel** FED/BCE qui pilote l'EURUSD, pas la BCE seule.

```schema
   FED plus restrictive que la BCE  ──► EURUSD ↓
   BCE plus restrictive que la FED  ──► EURUSD ↑
```

### 8. TAUX DIRECTEURS

**Ce que c'est.** Le prix officiel de l'argent à court terme.
**Ce qu'on regarde.** Non pas le niveau, mais la **trajectoire anticipée**,
lisible dans les futures de taux.

```schema
   Taux ↑  ──► actualisation ↑ ──► toutes les valorisations ↓
   Taux ↓  ──► actualisation ↓ ──► toutes les valorisations ↑
   ⚠ exception : baisse de taux motivée par une récession = actions ↓ malgré tout
```

### 9. DXY — Indice du dollar

**Composition.** EUR 57,6 % · JPY 13,6 % · GBP 11,9 % · CAD 9,1 % · SEK 4,2 % ·
CHF 3,6 %. C'est donc, pour l'essentiel, un EURUSD inversé.

**Pourquoi il compte.** Le dollar est le dénominateur mondial : matières
premières, dette émergente et réserves y sont libellées.

| DXY | Or | Matières premières | Émergents | Indices US |
|---|---|---|---|---|
| ↑ | ↓ | ↓ | ↓ | ↓ (généralement) |
| ↓ | ↑ | ↑ | ↑ | ↑ (généralement) |

::: piege
En crise majeure, le dollar monte **avec** la peur (valeur refuge, besoin de
liquidité) : toutes les corrélations habituelles s'inversent en même temps.
:::

### 10. OBLIGATIONS

**Ce que c'est.** De la dette cotée. Son prix évolue **à l'inverse** de son
rendement.
**Ce qu'on regarde.** Le 10 ans américain (taux d'actualisation mondial) et le
2 ans (anticipations de politique monétaire).

```schema
   Prix de l'obligation ↑  ──► rendement ↓  ──► actions ↑ · or ↑
   Prix de l'obligation ↓  ──► rendement ↑  ──► actions ↓ · or ↓
```

**Le rôle de refuge.** En stress, les capitaux fuient vers les obligations
d'État : leur prix monte, les rendements baissent. Sauf en crise
inflationniste, où actions et obligations baissent ensemble — le scénario le
plus douloureux pour les portefeuilles classiques (2022).

### 11. RENDEMENTS ET COURBE DES TAUX

**La courbe.** Rendements par échéance : 3 mois, 2 ans, 10 ans, 30 ans.

```schema
   NORMALE     2a ▁▂▃▅ 30a   croissance attendue
   PLATE       2a ▄▄▄▄ 30a   ralentissement
   INVERSÉE    2a ▅▃▂▁ 30a   récession anticipée (12-18 mois de délai)
```

**Le taux réel.** `taux nominal − inflation anticipée`. C'est **la** variable
qui pilote l'or et les valeurs de croissance. Retenez-la : elle explique la
majorité des mouvements que l'inflation seule n'explique pas.

### 12. PIB

**Ce que c'est.** La production totale d'une économie sur un trimestre.
**Volatilité.** ★★ — donnée en retard, largement anticipée par les PMI.
**Ce qu'on regarde.** La deuxième et la troisième estimation créent parfois plus
de mouvement que la première.

**Les indicateurs avancés à préférer.**

| Indicateur | Ce qu'il annonce | Seuil clé |
|---|---|---|
| PMI manufacturier | Activité industrielle | 50 = expansion / contraction |
| PMI services | Le gros de l'économie développée | 50 |
| ISM | Version américaine, très suivie | 50 |
| Ventes au détail | Consommation | Variation mensuelle |
| Confiance des consommateurs | Demande future | Tendance |

### 13. CHÔMAGE

**Ce que c'est.** Part de la population active sans emploi.
**Le paradoxe.** Un chômage très bas peut être **mauvais** pour les marchés : il
alimente les salaires, donc l'inflation, donc les taux.

**La règle de Sahm.** Quand la moyenne sur trois mois du taux de chômage dépasse
de 0,5 point son minimum des douze derniers mois, une récession est
historiquement en cours. C'est l'un des indicateurs les plus fiables du
retournement de cycle.

```schema
   Chômage ↓↓ (surchauffe) ──► salaires ↑ ──► inflation ↑ ──► taux ↑ ──► actions ↓
   Chômage ↑↑ (récession)  ──► demande ↓ ──► inflation ↓ ──► taux ↓ ──► actions ↓ puis ↑
```

### 14. RÉCESSION

**Définition.** Deux trimestres consécutifs de PIB négatif (définition
technique) ; aux États-Unis, décision du NBER sur un faisceau d'indicateurs.

**Chronologie type.**

```schema
   1. Inversion de la courbe des taux        (12-18 mois avant)
   2. PMI sous 50, resserrement du crédit    (6-12 mois avant)
   3. Sommet des indices                     (6-9 mois avant)
   4. Hausse du chômage, règle de Sahm       (début)
   5. Baisses de taux d'urgence              (pendant)
   6. Creux des indices                      (AVANT la fin de la récession)
```

**Ce qui marche en récession.** Obligations d'État, or (une fois les taux réels
en baisse), secteurs défensifs, liquidités. **Ce qui souffre.** Cycliques,
petites capitalisations, crédit à haut rendement, matières premières
industrielles.

::: piege
Les indices atteignent leur creux **pendant** la récession, souvent six mois
avant la fin. Attendre « que ça aille mieux » pour acheter garantit d'acheter
au sommet du rebond.
:::

### 15. GUERRE ET GÉOPOLITIQUE

**Le schéma classique.**

```schema
   Choc initial     ──► or ↑ · pétrole ↑ · dollar ↑ · actions ↓   (jours)
   Absorption       ──► retour progressif aux niveaux d'avant     (semaines)
   Effet durable    ──► seulement si l'offre physique est touchée
```

**La règle contre-intuitive.** Les marchés absorbent les chocs géopolitiques
beaucoup plus vite qu'on ne l'imagine. Seuls comptent durablement les conflits
qui affectent réellement l'approvisionnement en énergie, en métaux ou en
denrées.

**Ce qui bouge en premier.** Pétrole et gaz (offre), or (refuge), devises refuge
(CHF, JPY, USD), puis les indices par contagion.

::: piege
Trader une nouvelle géopolitique, c'est arriver après les algorithmes et après
les gérants qui ont déjà couvert leurs portefeuilles. Le premier mouvement est
presque toujours excessif, et souvent effacé.
:::

### 16. CRISE FINANCIÈRE

**La signature.** Corrélations qui convergent vers 1, liquidité qui disparaît,
spreads qui explosent, mouvements de plusieurs ATR, mécanismes habituels
suspendus.

**Les phases.**

| Phase | Ce qui se passe | Ce qui marche |
|---|---|---|
| Déni | Première baisse « saine » | Rien : réduire |
| Panique | Ventes forcées, appels de marge | Liquidités, dollar |
| Capitulation | Volume record, mèches énormes | Attendre le test |
| Reconstruction | Range large, volatilité en baisse | Achats progressifs |

**Ce qu'il faut faire.** Réduire la taille, élargir les stops en proportion,
n'accepter que les configurations majeures. La volatilité multiplie les gains
comme les pertes — sauf que la ruine, elle, est définitive.

::: danger
En crise, la protection contre solde négatif et la qualité du courtier
comptent plus que votre analyse. Un gap de week-end peut dépasser votre stop de
plusieurs pourcents.
:::

::: retenir Le calendrier hebdomadaire à surveiller
| Jour | Événement récurrent |
|---|---|
| Lundi | Peu d'événements — journée de positionnement |
| Mardi | Souvent les données de confiance |
| Mercredi | Stocks pétroliers (16 h 30), FOMC les jours de réunion |
| Jeudi | Inscriptions au chômage (14 h 30), BCE |
| Vendredi | NFP (premier du mois), clôtures hebdomadaires |
:::

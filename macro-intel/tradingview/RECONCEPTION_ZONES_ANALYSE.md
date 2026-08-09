# Reconception de l'indicateur XAUUSD — Analyse (avant code)

Document de travail. Aucun `.pine` n'est modifié par ce document. Structure
imposée : A Diagnostic → B Architecture → C Logique → D Filtres → E Backtest
→ F Anti-repaint → G Design → H Diff.

---

## A — DIAGNOSTIC : pourquoi une SELL ZONE apparaît en pleine accélération haussière

Le mécanisme exact, retrouvé dans le module `Weekly Institutional Zones` :

1. **Les zones naissent une fois par semaine**, au lundi, à partir du profil
   de volume de la semaine ÉCOULÉE. Une fois créées, leur score est figé
   (choix délibéré anti-repaint) — mais ça veut dire qu'une zone née un lundi
   calme peut traverser toute la semaine sans être réévaluée, même si le
   marché change complètement de caractère entre-temps.

2. **Le seul mécanisme qui pourrait la faire disparaître à cause du contexte
   est trop grossier.** `f_ctxAllow(isBuy=false) = ctxCode != 2` — une zone
   SELL n'est bloquée que si le régime atteint `STRONG BULLISH` (le niveau le
   plus extrême des 5). Une accélération haussière rapide peut très bien
   rester classée `BULLISH` (pas encore `STRONG`) si l'EMA H1 ou le vote
   journalier MTF n'a pas encore rattrapé le mouvement — la classification de
   régime est construite sur des moyennes mobiles, donc elle **retarde
   structurellement sur le ressenti visuel d'un mouvement rapide**. Résultat :
   la zone reste légale au sens du code, absurde au sens visuel.

3. **L'invalidation par prix est réactive, pas anticipative.** Une zone SELL
   assise plus haut que le prix actuel n'est "cassée" que lorsque le prix la
   traverse en clôture. Tant que le rallye n'a pas encore atteint son niveau,
   elle reste affichée bien en avant du prix — visuellement, ça ressemble à
   "l'indicateur ignore la tendance", alors que techniquement la règle
   ("attendre que le prix atteigne ou casse la zone") n'a simplement pas
   encore eu l'occasion de s'appliquer.

**Diagnostic en une phrase** : le système a des règles de suppression
correctes mais réactives, et un seul verrou de contexte bien trop permissif
(un seul niveau sur cinq bloque), donc rien ne l'empêche d'afficher une zone
directionnellement absurde tant que le prix ne l'a pas physiquement démentie.

Ce n'est pas un bug de calcul — c'est un **trou de gouvernance entre
création et persistance** : la barre pour CRÉER une zone à contre-tendance
est déjà plus haute (malus +15 pts, section grpW), mais rien n'élève la barre
pour qu'une zone déjà créée RESTE affichée quand le contexte se dégrade sans
atteindre l'extrême.

---

## B — ARCHITECTURE : CALCUL → DÉCISION → AFFICHAGE

Constat important avant de proposer quoi que ce soit : **cette séparation
existe déjà dans le code actuel**, vérifiée ligne par ligne dans l'audit que
je viens de livrer. Elle n'est simplement pas nommée ainsi.

```
A — CALCUL (aucune n'écrit dans B ou C directement)
    atrV, pivots (ph/pl), trend, htfClose/htfEma, vwapV,
    biasD/biasW/ruban, POC/VAH/VAL veille, OB[], FVG[], EQH/EQL[],
    profil hebdo (wPoc/wVah/wVal/wHvn), MTF votes (dirD/H4/H1/M15/M5),
    ctxScore/ctxCode, gC1..gC5 (grade)

B — DECISION (8 lignes, jamais touchees sans preuve)
    alignLong/alignShort, trigLong/trigShort,
    rawLong/rawShort, buySignal/sellSignal
    -> AUCUNE variable de zone, OB, FVG, sweep, CHoCH, ctxCode
       n'y apparait. Verifie a nouveau ce jour.

C — AFFICHAGE (lit A et B, n'ecrit jamais dedans)
    panneau, zones hebdo (boxes/labels), OB/FVG (boxes),
    liquidite (lignes), BOS/CHoCH (lignes), grade (texte)
```

**Ce qui manque réellement** n'est pas la séparation — c'est une **quatrième
couche implicite** que ton cahier des charges nomme sans la nommer : un
**filtre de gouvernance des zones**, entre A et C, qui décide QUAND une zone
calculée a le droit de rester affichée. Aujourd'hui cette couche existe
(`f_ctxAllow`, `cassee`, `consommee`, `smcGone`) mais elle est **trop
clémente**, comme diagnostiqué en A. La reconception porte sur CETTE couche,
pas sur B — donc **zéro risque pour le backtest historique**, puisque B ne
bouge pas.

---

## C — LOGIQUE : BUY / SELL / ZONE / INVALIDATION / ENTRY / SL / TP

### ENTRY (= B, inchangé)
`buySignal`/`sellSignal` restent la seule source de vérité pour un trade
réel. Ta liste de 12 conditions "setup BUY idéal" (contexte, SSL, sweep,
réaction, CHoCH, BOS, FVG, OB, zone, SL, objectif, RR) décrit un idéal
narratif — mais **seules 5 des 12 ont un effet mesuré** (biais, HTF, VWAP,
POC, structure/déclencheur). Le reste (SSL, sweep, réaction, CHoCH, FVG, OB)
reste ce qu'il a toujours été dans ce projet : narratif et pédagogique, pas
un filtre — sauf preuve contraire, jamais obtenue en ~50 concepts testés.

### ZONE (nouvelle gouvernance proposée, affichage seulement)
Une zone n'est **créée** que si (inchangé) : ancrage Value Area/HVN valide,
bon côté du milieu de range, prix y a déjà réagi, contexte compatible, score
≥ seuil.

Une zone **reste affichée** seulement si, en plus des 4 causes de retrait
déjà codées (consommée, clôture au travers, OB/FVG cassé, contexte à
l'extrême) :
- **le contexte n'est plus seulement "pas extrême" mais "pas opposé"** — je
  propose de faire passer le verrou de `ctxCode != ±2` à `ctxCode != ±2 ET
  ±1` pour le côté opposé au sens de la zone (soit : `BULLISH` bloque déjà
  les zones SELL, pas seulement `STRONG BULLISH`). C'est un changement
  d'AFFICHAGE, zéro impact sur `buySignal/sellSignal`.
- **âge maximum** : une zone dont l'ancre (OB/FVG) date de plus de N bougies
  par rapport à la bougie courante est retirée même si techniquement encore
  "intacte" — répond à "le setup arrive trop tard après l'impulsion" (ta
  section 7).
- **distance maximum** : une zone à plus de K × ATR du prix courant devient
  discrète (pas supprimée, juste dé-priorisée visuellement) — répond à "elle
  est trop éloignée du prix".

Ces trois règles sont **déterministes, codables, et n'affectent que
l'affichage** — donc testables sans toucher au backtest de la stratégie
principale. Elles ont quand même besoin d'un seuil (combien de bougies,
combien d'ATR) : je les choisirai avec une valeur de départ raisonnable et on
observe, jamais optimisé sur le résultat.

### INVALIDATION (déjà couvert, ta liste correspond à ce qui existe)
Consommée · clôture au travers · OB cassé · FVG comblé · contexte
incompatible — déjà codé. "Structure invalidée" avait été codé puis retiré
cette session (bug trouvé : jugeait une zone sur une condition — alignement
de `trend` — jamais exigée à sa création). Je ne le réintroduis pas sans
revoir ce point.

### SL
`slAtr = 2.5 × ATR`, comparé à 1.5×ATR (négatif sur 2/4 sous-périodes) — une
comparaison, pas un balayage complet malgré le mot "mesuré". Ta demande de
comparer structure / sweep / invalidation comme méthodes alternatives de SL
est légitime et **n'a jamais été faite** dans ce projet — c'est un test à
ajouter, pas une conclusion à supposer.

### TP
Déjà exactement ce que tu demandes : `objPx` (POC/liquidité) est un repère de
LECTURE, jamais une sortie automatique ("AUCUN ORDRE NE SORT D'ICI", commenté
dans le code). La sortie réelle (trailing 1.5R/0.3R vs TP fixe 0.5R) est déjà
comparée sur 783 trades dont 200 hors échantillon. Rien à changer ici — c'est
la partie du fichier la mieux validée.

### R:R minimum
**N'existe pas aujourd'hui.** Le calculer pour affichage : trivial (déjà
fait, `rr`). En faire un GATE qui bloque l'entrée : c'est un changement de
ligne B, donc une modification des conditions de trading — je ne le fais pas
sans ton feu vert explicite et un backtest dédié, conformément à la règle du
projet.

---

## D — FILTRES : classement

| Filtre | Classement | Base |
|---|---|---|
| Biais D1+W1 | **ESSENTIEL** | Porte le système seul : +0.064→+0.130 R |
| Tendance H1 (HTF EMA) | **ESSENTIEL** | +0.016 / +0.096, stable |
| VWAP session | **UTILE** | +0.044 / +0.161, plus petit mais réel |
| POC veille | **UTILE, À RE-VÉRIFIER** | Mesuré utile, mais repose sur `volume` — proxy non garanti sur un CFD or (voir audit) |
| Structure/BOS (déclencheur) | **ESSENTIEL** | C'est le déclencheur lui-même |
| Structure comme filtre séparé | **DÉCORATIF** | Tautologique avec le déclencheur en mode BOS (démontré) |
| CHoCH | **DÉCORATIF comme filtre, UTILE comme narration** | Jamais gate, aide à lire le graphique |
| Sweep de liquidité | **INUTILE comme filtre** | Mesuré négatif : -0.087 / -0.178, inverse le signe |
| OB | **DÉCORATIF comme filtre, UTILE comme narration** | -0.188 / +0.378, signe instable |
| FVG | **DÉCORATIF comme filtre, UTILE comme narration** | +0.134 / -0.028, signe instable |
| Score de confluence hebdo (0-100) | **À TESTER** | Jamais validé comme filtre de trade — c'est un outil de planification, pas un score prédictif |
| MTF M5/M15/H4/D1 | **INUTILE comme filtre** | M5 rejeté 4 fois par 4 méthodes indépendantes |
| Displacement seul (`useImb`) | **INUTILE, déjà rejeté** | PF 1.13→1.08, désactivé par défaut |
| Régime de contexte (ctxCode) | **UTILE pour l'affichage des zones**, jamais testé comme filtre d'entrée | Actuellement ne gate que l'affichage |
| Filtre ADX/régime de volatilité | **INUTILE, déjà rejeté** | Testé, faux positif (p=0,0018 in-sample), inversé hors échantillon — leçon documentée, ne pas retenter sans nouvelle méthode |
| R:R minimum | **À TESTER** | N'existe pas, jamais mesuré |
| Cooldown (10 barres) | **UTILE mais NON DOCUMENTÉ** | Aucune mesure retrouvée dans le fichier malgré le groupe "ne pas modifier sans mesure" |
| SL 2.5×ATR | **ESSENTIEL** | Comparé (pas balayé) à 1.5×ATR |
| Sortie trailing (1.5R/0.3R) | **ESSENTIEL** | Le mieux validé du fichier entier |

---

## E — BACKTEST : tester chaque composant sans overfitting

C'est déjà le protocole utilisé sur ce projet (~50 concepts testés, 10
cycles, zéro retenu) — je le reprends tel quel plutôt que d'en inventer un
nouveau :

1. **Baseline** = les 8 lignes de décision actuelles, seules. Référence :
   1979 trades, 19,1 ans, PF 1,212, espérance +0,137 R.
2. **Un seul module ajouté à la fois**, jamais une combinaison de plusieurs
   nouveautés en même temps (sinon impossible d'attribuer l'effet).
3. **Split train/validation obligatoire** : la période déjà utilisée pour
   explorer (in-sample) vs une période jamais regardée (out-of-sample). Sur
   ce système, 2007-2019 a servi de out-of-sample tardif : PF 1,176, écart de
   -0,054 R non significatif (p=0,486) — c'est le niveau d'exigence attendu.
4. **Puissance statistique vérifiée AVANT de conclure** : avec ~2000 trades
   et un écart-type de 1,40 R, le seuil de détection (MDE) est d'environ
   0,176 R — un filtre qui vaut moins que ça est structurellement invisible.
   Un "ça n'a pas amélioré le PF" doit d'abord passer ce test avant d'être
   interprété comme "ce filtre ne sert à rien" — les deux conclusions ne sont
   pas la même chose.
5. **Test de permutation (placebo)** pour toute règle qui semble fonctionner :
   mélanger l'ordre des trades / dates et vérifier que l'effet mesuré dépasse
   le bruit. La leçon du filtre ADX (rejeté après avoir pourtant passé 4/4
   tests, puis inversé sur données fraîches) reste la référence de prudence.
6. **Corrélation partielle avec le temps** : tout filtre qui dérive dans le
   temps hérite d'une corrélation parasite avec le résultat (découvert sur
   l'ADX : 1/3 de son effet disparaissait une fois neutralisé).
7. **Rapporter "non significatif" explicitement** quand c'est le cas — jamais
   inventer une conclusion parce que le chiffre est proche.

---

## F — ANTI-REPAINT : garanties et un trou trouvé

**Déjà garanti dans le code actuel :**
- Pivots (`ta.pivothigh/low`) : ne se confirment qu'après `swingLen` bougies,
  valeur figée une fois imprimée.
- Tous les `request.security` : `lookahead=barmerge.lookahead_off` +
  décalage `[1]` explicite dans la fonction demandée elle-même (double
  garantie).
- Profil de volume (jour ou semaine) : construit sur la période ÉCOULÉE
  uniquement, publié à la bascule, jamais recalculé en arrière.
- Score de zone : figé à la création, ne se recalcule jamais (principe déjà
  au cœur du module hebdomadaire).

**Un trou réel, trouvé dans l'audit d'aujourd'hui, pertinent pour cette
reconception puisque item 25 l'exige explicitement :** `trend` (la variable
de structure) est mis à jour par `if bullBos: trend := 1` **sans garde de
confirmation**. Comme `bullBos` dépend du prix courant (pas figé), une mèche
intrabougie qui franchit le niveau puis repart avant la clôture peut forcer
`trend` à la mauvaise valeur en direct — et rien ne le corrige automatiquement
puisque c'est une variable persistante. Ça ne fausse pas le backtest
historique (simulation bougie par bougie, jamais tick par tick), mais ça
peut fausser un usage live ou le forward test que tu as prévu. Je le
corrige dans le lot de cette reconception si tu valides — c'est un
changement d'anti-repaint, pas un changement de règle de trading.

---

## G — DESIGN : rendu final (schéma ASCII)

```
┌─────────────────────────────────────────────────────┬──────────────────┐
│  HTF: BULLISH            W1 D1 H4 alignes            │  VERDICT         │
│ ─────────────────────────────────────────────────── │  ATTENDRE · A    │
│                                                       │  (manque VWAP)   │
│                              ┌───────────┐  TP2      │──────────────────│
│                              │  SELL     │┄┄┄┄┄┄┄┄   │  BIAS            │
│                       BOS    │  62/100   │           │  BULLISH         │
│                    ┄┄┄┄┄┄┄┄┄┄└───────────┘  TP1      │──────────────────│
│           CHoCH                                      │  CONFLUENCE      │
│         ┄┄┄┄┄                                        │  62/100          │
│    sweep  •                                          │──────────────────│
│   ─┄┄┄┄┄─                                             │  VALIDATION      │
│                  ┌──────────┐                        │  ✓ Sweep         │
│                  │  BUY     │← zone unique            │  ✓ CHoCH         │
│                  │  84/100  │  (FVG+OB+structure       │  ✓ BOS           │
│                  └──────────┘   fusionnes dedans)      │  ✗ FVG           │
│                  Entry ─ ─ ─ ─ ─ ─ ─ ─                │  ✓ OB            │
│                  SL    ───────────────                │  ✗ HTF           │
│                                                       │──────────────────│
│                                                       │  PLAN            │
│                                                       │  Entry  2382.20  │
│                                                       │  SL     2376.20  │
│                                                       │  TP1    2396.00  │
│                                                       │  TP2    2389.80  │
│                                                       │  RR     1:2.4    │
└─────────────────────────────────────────────────────┴──────────────────┘
```

Une seule zone par côté mise en avant visuellement (l'autre, si elle existe,
reste tracée mais en gris/discret — priorité 1 de ta hiérarchie). FVG et OB
ne sont plus des rectangles séparés à 100 pixels de distance : ils sont
dessinés À L'INTÉRIEUR des bornes de la zone quand ils la recoupent
réellement (déjà en partie le cas dans le score de confluence — il s'agit de
le rendre visuel, pas seulement numérique).

---

## H — DIFF : ce qui bouge, ce qui ne bouge pas

### CONSERVÉ (zéro changement)
- Les 8 lignes de décision : `alignLong`, `alignShort`, `trigLong`,
  `trigShort`, `rawLong`, `rawShort`, `buySignal`, `sellSignal`.
- SL (2.5×ATR), sortie (trailing 1.5R/0.3R par défaut, TP fixe en option).
- Biais D1+W1, HTF EMA, VWAP, POC comme filtres de décision.
- Le principe même de la séparation Calcul/Décision/Affichage (déjà en place).

### MODIFIÉ (affichage/gouvernance des zones — AUCUN impact sur le backtest
### de la stratégie principale, puisque les zones ne décident jamais d'un trade)
- Verrou de contexte pour la persistance d'une zone : `BULLISH`/`BEARISH`
  bloque désormais le côté opposé (pas seulement `STRONG`).
- Ajout d'un âge maximum et d'une distance maximum pour qu'une zone reste
  affichée en avant plutôt que dé-priorisée.
- Fusion visuelle FVG + OB + structure + liquidité en une seule zone
  narrative plutôt que des éléments séparés.
- Panneau réduit au format demandé : VERDICT / BIAS / CONFLUENCE / VALIDATION
  / PLAN — le tableau de validation (stats de trades) et le détail zones
  actives restent disponibles mais peuvent passer en option masquable.
- Correctif anti-repaint sur `trend` (garde de confirmation) — change
  potentiellement le comportement LIVE, pas le backtest historique.

### AJOUTÉ (nouveau, nécessite un test avant d'être une vraie règle)
- R:R minimum configurable comme gate d'entrée (n'existe pas aujourd'hui).
- Comparaison SL alternatif (structure / sweep / invalidation) vs ATR —
  jamais fait, tu le demandes explicitement.
- Détection "setup trop tard après l'impulsion" (âge de l'ancre OB/FVG).

### SUPPRIMÉ
- Rien dans la décision. Le seul candidat réel à la suppression est du code
  mort déjà identifié dans l'audit (`pdhPrev`/`pdlPrev`, jamais lu).

---

## Ce qui reste à trancher avant de coder

1. Valides-tu que le renforcement du verrou de contexte (zones seulement,
   pas les trades) se fasse sans nouveau backtest — puisqu'il ne touche
   jamais `buySignal/sellSignal` ?
2. Le correctif anti-repaint sur `trend` : je le fais dans ce lot, ou séparé ?
3. R:R minimum et comparaison de méthodes de SL : je lance les tests
   maintenant (résultats avant tout code), ou plus tard ?
4. Seuils d'âge/distance pour les zones : je pars sur une valeur de départ
   raisonnable (à ajuster après observation), ou tu as une préférence ?

Dis-moi lesquels de ces quatre points tu valides — je code seulement ce qui
est validé, dans l'ordre que tu choisis.

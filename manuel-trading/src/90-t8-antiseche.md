# Tome 8 — Mon antisèche

Dix pages. Aucune phrase inutile. Objectif : tout revoir en moins de cinq
minutes, chaque matin, avant d'ouvrir la plateforme.

## Page 1 — Les quinze mots essentiels

| Mot | Une ligne |
|---|---|
| **Liquidité** | Les ordres en attente au-delà des extrêmes ; la destination du prix |
| **BSL / SSL** | Stops au-dessus / en dessous ; cibles, jamais abris |
| **Sweep** | Purge de ces stops, suivie d'un retournement |
| **Inducement** | Faux point d'entrée placé devant la vraie zone |
| **BOS** | Cassure dans le sens de la tendance = continuation |
| **CHoCH** | Cassure du dernier pivot opposé = retournement possible |
| **MSS** | CHoCH + déplacement + FVG = changement de biais |
| **Déplacement** | Bougies larges laissant un déséquilibre = preuve d'intention |
| **Order Block** | Dernière bougie opposée avant le déplacement |
| **FVG** | Trou entre bougie 1 et bougie 3 ; le prix revient le combler |
| **Breaker** | Order Block cassé qui change de camp |
| **Mitigation** | Dernier bloc opposé, sans cassure de structure = continuation |
| **Premium / Discount** | Au-dessus / en dessous du 50 % du range |
| **OTE** | Retracement 62–79 % : la zone d'entrée optimale |
| **Kill Zone** | 09 h–11 h et 14 h 30–17 h : les seules heures qui comptent |

## Page 2 — La séquence, dans l'ordre

```schema
   1  BIAIS       D1/H4 : direction · cible · invalidation (écrit)
   2  HEURE       suis-je dans une Kill Zone ?
   3  LIQUIDITÉ   quelle liquidité vient d'être prise ?
   4  STRUCTURE   CHoCH ou MSS, avec déplacement ?
   5  ZONE        OB ou FVG, du bon côté de l'équilibre ?
   6  INDUCEMENT  le faux point d'entrée a-t-il été purgé ?
   7  ENTRÉE      ordre limite, jamais au marché
   8  STOP        au-delà de la mèche + marge (spread + bruit)
   9  TAILLE      (capital × 1 %) / (distance stop × valeur point)
  10  OBJECTIFS   1:2 (moitié) puis liquidité HTF (stop suiveur)
```

**Une case manquante = pas de trade.**

## Page 3 — Structure

| | BOS | CHoCH | MSS |
|---|---|---|---|
| Sens de la cassure | Tendance | Opposé | Opposé |
| Signification | Continuation | Retournement possible | Changement de biais |
| Déplacement requis | Souhaitable | Souhaitable | **Obligatoire** |
| FVG laissé | Fréquent | Fréquent | **Obligatoire** |
| Purge préalable | Parfois | Presque toujours | Presque toujours |

```schema
   HAUSSIÈRE   HH ─ HL ─ HH ─ HL      → achats uniquement
   BAISSIÈRE   LH ─ LL ─ LH ─ LL      → ventes uniquement
   NEUTRE      chevauchements          → bords de range ou rien
```

- Une **mèche** ne casse rien : seule une **clôture** casse.
- La structure **interne** ne change jamais le biais.
- La structure **externe** donne le biais et les objectifs.

## Page 4 — Zones

| Zone | Condition | Type de trade |
|---|---|---|
| **Order Block** | Liquidité + déplacement + cassure de structure | Continuation ou retournement |
| **FVG** | 3 bougies sans chevauchement | Entrée limite au milieu |
| **IFVG** | FVG traversé **en clôture** | Retournement, un seul retest |
| **Breaker** | OB cassé **avec** cassure de structure | Retournement |
| **Mitigation** | Dernier bloc opposé, **sans** cassure | Continuation |
| **BPR** | Deux FVG opposés superposés | Sens du dernier déplacement |
| **Rejection block** | Mèches répétées au même niveau | Retournement |
| **Unicorn** | Breaker + FVG superposés, après MSS | Taille pleine |

**Règles communes :** une seule mitigation par zone · stop au-delà, jamais
dedans · toujours dans le sens du biais HTF · toujours du bon côté de
l'équilibre.

## Page 5 — Liquidité et premium/discount

```schema
   ▲▲▲ BSL — equal highs, PDH, chiffres ronds  ──► cible haussière
   ─────────────────────────────────────────
        ░░░░ PREMIUM ░░░░   → ventes uniquement
   ══════ ÉQUILIBRE 50 % ══════  → zone morte
        ▓▓▓▓ DISCOUNT ▓▓▓▓  → achats uniquement
   ─────────────────────────────────────────
   ▼▼▼ SSL — equal lows, PDL, chiffres ronds   ──► cible baissière
```

**Les deux questions obligatoires avant chaque entrée :**
1. Quelle liquidité vient d'être **prise** ?
2. Quelle liquidité est **visée** ?

**Trois règles de placement :** objectif *juste avant* un pool · stop *au-delà*
d'un pool · jamais rien *dedans*.

## Page 6 — Temps

```schema
   00 h ─ 09 h   ASIE          range étroit · réservoir de liquidité
   09 h ─ 11 h   LONDRES       ██ purge puis direction du jour
   11 h ─ 14 h 30 MI-JOURNÉE   ░░ interdit
   14 h 30 ─ 17 h NEW YORK     ██ publications · extension ou retournement
   17 h ─ 19 h   LONDON CLOSE  ▓ retournements fréquents
```

**Les quatre lignes à tracer chaque matin :** plus haut de la veille (PDH),
plus bas de la veille (PDL), clôture de la veille, ouverture du jour.
**Plus deux :** haut et bas du range asiatique.

**Heures interdites :** les 15 premières minutes d'une session · 11 h–14 h 30 ·
les deux minutes entourant une publication majeure.

## Page 7 — Risque

```schema
   TAILLE = (capital × risque %) / (distance au stop × valeur du point)
   Exemple : (10 000 × 1 %) / (25 pips × 10 €) = 100 / 250 = 0,40 lot
```

| Risque / trade | 10 pertes d'affilée | Retour nécessaire |
|---|---|---|
| 0,5 % | −4,9 % | +5,2 % |
| 1 % | −9,6 % | +10,6 % |
| 2 % | −18,3 % | +22,4 % |
| 5 % | −40,1 % | +67,0 % |

| R:R | Taux de réussite pour l'équilibre |
|---|---|
| 1:1 | 50 % |
| 1:2 | 33 % |
| 1:3 | 25 % |
| 1:5 | 17 % |

**Limites non négociables :** 1 % par trade · 3 % d'exposition totale · −3 R par
jour · −6 R par semaine · 3 trades par jour · 2 stops sur un instrument = fini
pour la journée.

## Page 8 — Macro

```schema
   Inflation ──► anticipations de taux ──► TAUX RÉELS ──► DOLLAR ──► tout le reste
```

```tableau
                     │ Taux ↑ │ DXY ↑ │ Récession │ Risk-off
─────────────────────┼────────┼───────┼───────────┼──────────
 OR                  │   ↓    │   ↓   │     ↑     │    ↑
 ARGENT              │   ↓    │   ↓   │    ↓↓     │    ↓
 BITCOIN             │  ↓↓    │   ↓   │    ↓↓     │   ↓↓
 INDICES             │   ↓    │   ↓   │  ↓ puis ↑ │   ↓↓
 PÉTROLE             │   ↓    │   ↓   │    ↓↓     │    ↓
 OBLIGATIONS         │  ↓↓    │   —   │    ↑↑     │    ↑
 JPY / CHF           │   ↓    │   ↓   │     ↑     │   ↑↑
```

| Événement | Heure (Paris) | Volatilité |
|---|---|---|
| CPI | 14 h 30 | ★★★ |
| NFP | 14 h 30, 1er vendredi | ★★★ |
| FOMC | 20 h + 20 h 30 | ★★★★ |
| BCE | 14 h 15 + 14 h 45 | ★★★ |
| Stocks pétroliers | Mercredi 16 h 30 | ★★ |

**Trois réflexes :** seule la surprise compte · la même donnée change de signe
selon le régime · on trade le FVG laissé, jamais l'annonce.

## Page 9 — Erreurs et psychologie

**Les dix erreurs les plus coûteuses**

| # | Erreur |
|---|---|
| 1 | Déplacer son stop dans le sens de la perte |
| 2 | Revenge trading après une perte |
| 3 | Risquer plus de 1 % par trade |
| 4 | Multiplier les positions corrélées |
| 5 | Entrer sur la bougie de cassure |
| 6 | Couper ses gains trop tôt |
| 7 | Acheter en premium, vendre en discount |
| 8 | Trader hors des fenêtres horaires |
| 9 | Ne pas tenir de journal |
| 10 | Changer de méthode en permanence |

**Les trois racines de toutes les erreurs :** l'impatience · le refus d'acter
une perte · le besoin de certitude.

**Les quatre signaux d'arrêt immédiat**

```schema
   ☐ −3 R sur la journée
   ☐ Deux stops consécutifs sur le même instrument
   ☐ Envie de « me refaire »
   ☐ Je ne peux pas expliquer mon trade en une phrase
```

## Page 10 — Routine de cinq minutes

```schema
   ┌─ 1 min ─ CONTEXTE ────────────────────────────────────┐
   │ Structure W1 / D1 ? Premium ou discount ?             │
   │ Prix au-dessus ou en dessous de la MM200 D1 ?         │
   ├─ 1 min ─ LIQUIDITÉ ───────────────────────────────────┤
   │ Prise hier ? Restante au-dessus ? En dessous ?        │
   ├─ 1 min ─ NIVEAUX ─────────────────────────────────────┤
   │ Tracer : PDH · PDL · clôture veille · ouverture jour  │
   ├─ 1 min ─ CALENDRIER ──────────────────────────────────┤
   │ Publication aujourd'hui ? À quelle heure ?            │
   ├─ 1 min ─ DÉCISION ────────────────────────────────────┤
   │ DIRECTION    : ..................                     │
   │ CIBLE        : ..................                     │
   │ INVALIDATION : ..................                     │
   └───────────────────────────────────────────────────────┘
        Si je ne peux pas écrire les trois lignes → observation.
```

**Les dix règles d'or, version courte**

1. Le prix va chercher les ordres, pas la valeur.
2. Quelle liquidité prise, quelle liquidité visée.
3. Jamais au milieu du range.
4. Jamais sur la bougie de cassure.
5. Discount = achats, premium = ventes.
6. Décider de sa sortie avant son entrée.
7. 1 % maximum par trade.
8. −3 R sur la journée : on ferme.
9. Ne rien faire est une position.
10. Survivre est la condition préalable à gagner.

::: retenir Le mot de la fin
Ce manuel ne vous rendra pas rentable. Il vous évite seulement de perdre du
temps à chercher ce que vous savez déjà, et de perdre de l'argent à réapprendre
ce que vous avez déjà appris. Le reste — la patience, la répétition, le journal
relu chaque dimanche — ne s'écrit pas dans un livre. Il se pratique.

Bon trading, et surtout : bonne survie.
:::

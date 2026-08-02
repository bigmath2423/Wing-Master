# GOLD MACRO — le manuel de référence du trader XAUUSD

Manuel professionnel de macroéconomie appliquée au trading de l'or. Conçu comme
un **outil de travail quotidien**, pas comme un livre à lire une fois : fiches,
tableaux de réaction, checklists, scénarios et routine de séance.

Pour un trader qui maîtrise déjà l'analyse technique, la structure de marché, la
liquidité et l'exécution.

## Les deux formats

| Fichier | Usage |
|---|---|
| **`gold-macro.pdf`** | 106 pages A4, grande police, très aéré — à imprimer ou à lire sur tablette |
| **`gold-macro.html`** | Version interactive : recherche instantanée, thème clair/sombre, reprise de lecture, adapté au téléphone |

Le HTML est **autonome** : aucune police distante, aucune image externe, aucun
script tiers. Il fonctionne hors ligne.

| Action | Comment |
|---|---|
| Chercher | Touche `/` — accents et majuscules ignorés |
| Naviguer | Sommaire de gauche, ou sommaire imprimé au début |
| Clair / sombre | Bouton **◐ Thème** (mémorisé) |
| Exporter en PDF | `Ctrl+P` → A4, marges par défaut, **arrière-plans activés** |

## Structure — 8 parties

| Partie | Contenu |
|---|---|
| 1 | **La carte d'identité du Gold** — pourquoi il monte ou baisse, qui fait le prix, les 10 moteurs |
| 2 | **Les indicateurs macro** — 11 fiches : CPI, Core CPI, PCE, PPI, NFP, chômage, JOLTS, PIB, PMI, ISM, ventes au détail |
| 3 | **La Fed** — hawkish/dovish, lire un discours, décision de taux, minutes, checklist avant réunion |
| 4 | **Les graphiques indispensables** — DXY, 10 ans, taux réels, courbe des taux, VIX |
| 5 | **La routine quotidienne** — avant Londres, avant New York, avant une entrée |
| 6 | **Les scénarios de marché** — 6 configurations, de la conviction maximale à l'abstention |
| 7 | **Les erreurs des traders** — pourquoi une bonne news fait l'inverse, pourquoi ne pas trader l'annonce, pourquoi le marché anticipe |
| 8 | **Les fiches rapides** — Daily Checklist, tableau d'impact des news, corrélations, analyse macro en 5 minutes |

### Le format d'une fiche indicateur

Toujours le même, pour une lecture en trente secondes :

```
À quoi ça sert  ·  Pourquoi le marché le regarde
Réaction sur le Gold (supérieur / inférieur aux attentes, force)
Quand la réaction est différente  ·  Mémo
```

### Les trois niveaux d'explication

Chaque notion importante est expliquée en **simple**, en **professionnel**, puis
en **application directe sur XAUUSD**.

## Modifier le manuel

Sources en Markdown dans `src/`, lues dans l'ordre alphabétique.

```bash
pip install markdown          # une seule fois
python3 livre-gold/build.py   # régénère gold-macro.html
```

### Conventions d'écriture

```markdown
# Titre                 PARTIE   (page pleine à l'impression)
## Titre                CHAPITRE (numéroté, nouvelle page)
## Titre {: .fiche }    FICHE    (numérotation séparée)
## Titre {: .libre }    page spéciale, sans numéro
### Titre               section

::: retenir Titre facultatif
contenu markdown
:::
```

Encadrés disponibles :

| Classe | Rendu |
|---|---|
| `retenir` | À retenir absolument (or) |
| `erreur` | Erreur des débutants (rouge) |
| `institutions` | Ce que font les institutions (cyan) |
| `detail` | Le détail que 90 % des traders ignorent (violet) |
| `xau` | Application directe sur XAUUSD (or) |
| `fiche` | Fiche pratique (vert) |
| `cas`, `histoire`, `astuce`, `danger`, `memo`, `resume` | variantes |
| `niveaux` | les trois niveaux d'explication (liste de 3 puces) |
| `cartes` | grille de cartes (liste à puces) |
| `cle` | phrase forte, en grand |
| `respiration` | page de respiration (saut de page avant, à l'impression) |

Blocs de code balisés : `schema` (schéma ASCII), `svg` (graphique vectoriel
adapté au thème), `tableau` (tableau ASCII large).

## Avertissement

Ouvrage pédagogique. Ne constitue pas un conseil en investissement et ne promet
aucun résultat.

Les chiffres et niveaux cités en exemple illustrent des **mécanismes** : ce sont
des séquences typiques du marché, pas un relevé historique exact. Vérifiez les
données réelles auprès des sources officielles listées en fin de manuel (BLS,
BEA, Réserve fédérale, FRED, ISM, CFTC, World Gold Council, LBMA).

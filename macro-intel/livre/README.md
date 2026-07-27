# 📕 Maîtriser la Macroéconomie, l'Analyse Fondamentale et le Trading Institutionnel

### De Débutant à Trader Macro-SMC

Manuel de formation complet en français : **15 parties**, ~40 000 mots,
159 tableaux, exercices corrigés et études de cas.

> ⚠️ **Ouvrage pédagogique.** Ne constitue pas un conseil en investissement.
> Le trading comporte un risque réel de perte en capital.

---

## Générer le PDF

```bash
python build_livre.py
```

Puis ouvrez `livre.html` dans un navigateur et faites
**Imprimer → Enregistrer au format PDF**.

Le fichier HTML est **autonome** (aucune ressource externe) et contient une
feuille de style d'impression : format A4, sauts de page aux bons endroits,
tableaux et encadrés jamais coupés.

## Sommaire

| Partie | Titre | Ce que vous saurez faire ensuite |
|:-----:|-------|----------------------------------|
| **1** | Les bases de l'économie | Situer un pays dans le cycle économique |
| **2** | Les indicateurs économiques | Lire PIB, inflation, emploi, PMI et anticiper leur effet |
| **3** | Les banques centrales | Décoder une décision de taux et un discours |
| **4** | Les taux et les obligations | Lire la courbe des taux comme un signal de cycle |
| **5** | Le dollar et le Forex | Comprendre ce qui fait monter ou baisser une devise |
| **6** | Les matières premières | Analyser l'or avec une méthode en 7 étapes |
| **7** | Géopolitique et marchés | Évaluer un choc en 5 questions |
| **8** | Le calendrier économique | Anticiper et lire une publication |
| **9** | Construire un biais macro | Produire un biais chiffré en 8 étapes |
| **10** | Fondamental + technique | Articuler contexte et timing |
| **11** | Smart Money Concepts | Liquidité, structure, zones institutionnelles |
| **12** | Méthode Macro-SMC complète | Exécuter une stratégie de bout en bout |
| **13** | Psychologie du trader | Tenir son plan sous pression |
| **14** | Glossaire complet | Maîtriser le vocabulaire professionnel |
| **15** | Annexes | Checklists, exercices, études de cas |

## Structure de chaque partie

Chaque chapitre suit le même schéma pédagogique :

1. Le contenu, du simple vers l'avancé, avec exemples appliqués aux marchés
2. **📌 Résumé**
3. **🎯 Points essentiels à retenir**
4. **⚠️ Erreurs fréquentes**
5. **🗂 Fiche de révision**
6. **✍️ Questions d'entraînement** — avec corrigé

## Trois parcours de lecture

| Profil | Parcours conseillé |
|--------|--------------------|
| **Débutant complet** | 1 → 15 dans l'ordre |
| **Trader technique** | 2, 3, 8, 9 puis 10 → 12 |
| **Trader SMC / ICT** | 9 puis 10 → 12, puis 2 et 3 pour approfondir |

Un **plan de progression sur 90 jours** figure en Partie 15, section F.

## Fichiers

```
livre/
├── README.md                       ce fichier
├── build_livre.py                  générateur HTML → PDF
├── livre.html                      livre complet (généré)
├── 00-introduction.md
├── 01-bases-economie.md
├── … (15 parties)
└── 15-annexes.md
```

Les chapitres sont en Markdown : lisibles sur GitHub, modifiables, versionnés.
Le script les assemble en un document unique.

## Le principe directeur

> **La macro donne la direction probable. La technique donne le point d'entrée.
> Aucune des deux ne donne de certitude.**

---

## Lien avec la plateforme MacroLens

Ce livre est le **support théorique** de la plateforme d'analyse macro située
dans le dossier parent. Les concepts enseignés y sont implémentés :

| Notion du livre | Où elle vit dans le code |
|-----------------|--------------------------|
| Taux réels, courbe des taux (Parties 4, 6) | `app/analysis/yield_curve.py` |
| Régimes de marché (Partie 1) | `app/analysis/regime.py` |
| Mécanismes de transmission (Parties 2, 3, 7) | `app/ai/knowledge.py` |
| Biais macro en 8 étapes (Partie 9) | `app/engine/scoring.py`, `bias.py` |
| Matrice de convergence (Parties 10, 12) | `app/engine/fusion.py` |
| Calendrier économique (Partie 8) | `app/providers/economic_calendar.py` |

Lire le livre, puis utiliser la plateforme : la seconde applique ce que le
premier explique.

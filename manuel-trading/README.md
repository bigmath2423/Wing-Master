# Manuel de Trading Personnel

Manuel de référence en huit tomes, destiné à être consulté avant chaque séance :
dictionnaire complet, concepts expliqués, macroéconomie, checklists, règles d'or,
erreurs à éviter, aide-mémoire et antisèche.

## Ouvrir le manuel

Double-cliquez sur **`manuel-de-trading.html`**. Le fichier est autonome :
aucune police, aucune image, aucun script externe, aucune connexion. Il
fonctionne hors ligne, sur ordinateur comme sur téléphone.

| Action | Comment |
|---|---|
| Chercher un terme | Touche `/`, ou le champ de recherche. Accents ignorés. |
| Naviguer | Sommaire de gauche, ou sommaire imprimé en début de livre |
| Basculer clair / sombre | Bouton **◐ Thème** (le choix est mémorisé) |
| Masquer le sommaire | Bouton **☰ Sommaire** |
| Reprendre la lecture | La position est mémorisée automatiquement |
| Exporter en PDF | `Ctrl+P` → « Enregistrer au format PDF », marges par défaut |

Une version imprimée est également fournie : **`manuel-de-trading.pdf`**
(223 pages A4). Elle est produite depuis le HTML — pour la régénérer après une
modification, ouvrez le HTML et faites `Ctrl+P` → « Enregistrer au format PDF »,
format A4, marges par défaut, sans arrière-plans.

## Contenu

| Tome | Titre | Volume |
|---|---|---|
| 1 | Dictionnaire du trading | ~140 entrées, de A à Z |
| 2 | Les concepts expliqués | 26 chapitres (Dow, Wyckoff, ICT, SMC, volume, liquidité…) |
| 3 | Macroéconomie | 16 fiches + impact détaillé sur 6 actifs |
| 4 | Checklists | 9 checklists opérationnelles |
| 5 | Les 100 règles d'or | 100 règles, une phrase chacune |
| 6 | Les erreurs à éviter | 65 erreurs : cause, prévention, correction |
| 7 | Mon aide-mémoire | Fiches ultra-rapides en tableaux |
| 8 | Mon antisèche | 10 pages, révision complète en 5 minutes |

## Modifier le manuel

Les sources sont dans `src/`, en Markdown, lues dans l'ordre alphabétique des
noms de fichiers. Après toute modification :

```bash
pip install markdown          # une seule fois
python3 manuel-trading/build.py
```

Le script régénère `manuel-de-trading.html` et affiche un décompte
(tomes, chapitres, entrées, mots).

### Conventions d'écriture

```markdown
# Titre              ouverture de tome (nouvelle page à l'impression)
## Titre             chapitre (apparaît dans le sommaire)
### Titre            entrée de dictionnaire / sous-section (indexée par la recherche)

::: retenir À retenir absolument
contenu markdown
:::
```

Classes d'encadrés disponibles : `retenir` (vert), `erreur` (rouge),
`piege` (orange), `memo` (violet), `astuce` (bleu), `pro` (cyan),
`resume` (or), `danger` (rouge appuyé). Le titre après le nom de classe est
facultatif : un libellé par défaut est appliqué.

Les schémas ASCII s'écrivent dans un bloc de code balisé `schema` (ou
`tableau` pour les grands tableaux en largeur) :

````markdown
```schema
   ▲ mèche de purge
 ──┼──── niveau
```
````

## Avertissement

Ce manuel décrit des méthodes de lecture de marché et des règles de gestion du
risque. Il ne constitue pas un conseil en investissement et ne promet aucun
résultat. Le trading à effet de levier fait perdre de l'argent à la majorité des
participants.

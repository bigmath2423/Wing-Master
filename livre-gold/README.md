# L'Or et la Macro — comprendre les forces qui font bouger le XAUUSD

Livre de macroéconomie appliquée au trading de l'or, en 10 parties et
31 chapitres. Écrit pour un trader qui maîtrise déjà l'analyse technique, la
structure de marché, la liquidité et l'exécution — et à qui il manque la lecture
macro.

## Les deux formats

| Fichier | Usage |
|---|---|
| **`or-et-macro.pdf`** | 128 pages A4, prêt à imprimer ou à lire sur tablette |
| **`or-et-macro.html`** | Version interactive : recherche instantanée, thème clair/sombre, reprise de lecture |

Le HTML est **autonome** : aucune police distante, aucune image externe, aucun
script tiers. Il fonctionne hors ligne, sur téléphone comme sur ordinateur.

| Action | Comment |
|---|---|
| Chercher un sujet | Touche `/` — accents et majuscules ignorés |
| Naviguer | Sommaire de gauche, ou sommaire imprimé au début |
| Clair / sombre | Bouton **◐ Thème** (mémorisé) |
| Exporter en PDF | `Ctrl+P` → « Enregistrer au format PDF », A4, marges par défaut |

## Structure

Chaque chapitre suit exactement le même plan :

```
📌 Pourquoi ce chapitre compte     l'enjeu pour un trader du Gold
💡 L'explication simple            le concept en mots accessibles
📊 Exemple concret                 une situation réelle de marché
🥇 Impact sur le Gold              ça monte / ça baisse / les exceptions
🏛️ Ce que regarde un pro            la lecture institutionnelle
✅ À retenir absolument            la page à relire avant de trader
📋 Fiche pratique                  la checklist utilisable en séance
```

### Les dix parties

| Partie | Contenu | Chapitres |
|---|---|---|
| 1 | Comprendre l'or | 1–4 |
| 2 | Le dollar (DXY) | 5–6 |
| 3 | Les taux d'intérêt (Fed, obligations, **taux réels**) | 7–9 |
| 4 | L'inflation (CPI, Core CPI, PCE, PPI) | 10–13 |
| 5 | L'emploi américain (NFP, chômage, JOLTS, ADP) | 14–15 |
| 6 | La croissance (PIB, PMI/ISM, consommation) | 16–18 |
| 7 | Les banques centrales (Fed, FOMC, hawkish/dovish) | 19–21 |
| 8 | Crises et événements mondiaux | 22–24 |
| 9 | Les corrélations du Gold | 25–26 |
| 10 | **La méthode** (8 étapes, semaine type, macro + SMC, études de cas, erreurs) | 27–31 |

Plus cinq annexes : tableau de réaction universel, calendrier permanent,
glossaire, fiche d'une page, sources de données officielles.

## Modifier le livre

Sources en Markdown dans `src/`, lues dans l'ordre alphabétique des noms de
fichiers.

```bash
pip install markdown          # une seule fois
python3 livre-gold/build.py   # régénère or-et-macro.html
```

Pour régénérer le PDF : ouvrir le HTML, `Ctrl+P`, format A4, marges par défaut,
arrière-plans activés.

### Conventions d'écriture

```markdown
# Titre        ouverture de PARTIE  (page pleine à l'impression)
## Titre       CHAPITRE             (nouvelle page à l'impression)
### Titre      section du chapitre  (indexée par la recherche)

::: retenir Titre facultatif
contenu markdown
:::
```

Classes d'encadrés : `retenir` (or), `erreur` (rouge), `astuce` (bleu),
`pro` (cyan), `histoire` (violet), `cas` (vert), `fiche` (vert clair),
`danger` (rouge appuyé), `memo`, `chiffre`.

Blocs de code balisés : `schema` (schéma ASCII encadré), `svg` (graphique
vectoriel inséré tel quel, adapté automatiquement au thème clair/sombre),
`tableau` (tableau ASCII large).

## Avertissement

Ouvrage pédagogique. Ne constitue pas un conseil en investissement et ne promet
aucun résultat. Les chiffres et niveaux cités dans les exemples illustrent des
**mécanismes** : ce sont des séquences typiques, pas un relevé historique exact.
Vérifiez les données réelles auprès des sources officielles listées en annexe E
(BLS, BEA, Réserve fédérale, FRED, LBMA, World Gold Council) avant toute
décision.

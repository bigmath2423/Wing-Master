# Tome 7 — Frontend & Design system

> **Statut : ✅ Rédigé & implémenté** · Code : `dashboard/app.html` (+ `index.html`, simulateur).

---

## 1. Décision : application autoportante d'abord — ADR-009

Le Tome 1 prévoyait Next.js. **Révision assumée** pour la V1 :

| Critère | HTML/JS autoportant (retenu V1) | Next.js (prévu V2) |
|---------|--------------------------------|--------------------|
| Déploiement | Servi par le backend, zéro build | Chaîne Node + build |
| Ouverture hors serveur | **Oui** (mode démonstration) | Non |
| Temps de mise en service | Immédiat | Jours |
| Écosystème composants | Limité | Riche |
| Adapté à 1 utilisateur | **Oui** | Sur-dimensionné |

**Justification** : livrer une application **réellement utilisable et
partageable en un fichier** prime sur l'outillage. La surface API `/v1` étant
stable, une migration Next.js ultérieure ne casse rien (le contrat ne change pas).

## 2. Identité visuelle
Thème **sombre unique**, choix délibéré (poste d'analyse), conforme au cahier
des charges. Palette « instrument de mesure » :

| Rôle | Valeur |
|------|--------|
| Fond / panneaux | `#0a0e14` / `#111826` |
| Texte / secondaire | `#e3e9f2` / `#9aa6b8` |
| Accent (bleu acier) | `#5aa9d6` |
| Sémantique | hausse `#3fb98a` · baisse `#e4635a` · alerte `#dda03c` |

Typographie : interface système + **monospace tabulaire** pour tous les chiffres
(alignement en colonnes, lecture d'instrument). Étiquettes en capitales espacées.
La couleur sémantique est réservée à l'**état**, jamais à la décoration.

## 3. Architecture de l'interface
Sept onglets : **Synthèse** (régime, briefing, indicateurs clés, contexte par
actif, risque événementiel, sujets prioritaires) · **Indicateurs** (panorama,
courbe, énergie, COT) · **Calendrier** (prochain rendez-vous majeur, agenda
groupé par jour, filtres d'impact) · **Marchés** (cours groupés) ·
**Événements** (analyses dépliables + analyse à la demande) ·
**Corrélations** (barres divergentes multi-fenêtres) · **Simulateur**.

Le calendrier distingue visuellement les **dates confirmées** (source externe)
des **dates reconstruites** (règles de publication) — l'utilisateur sait toujours
ce qu'il regarde.

Principes d'information : **synthèse avant détail**, état encodé dans la forme
(pastilles, liseré de priorité, barres divergentes) autant que dans le chiffre.

## 4. Accessibilité & robustesse
Contraste AA, navigation clavier (`tabindex`, `Enter`/`Espace` sur les cartes),
`:focus-visible` visible, `prefers-reduced-motion` respecté, tableaux dans un
conteneur `overflow-x` (le corps de page ne défile jamais horizontalement),
échappement HTML systématique des contenus dynamiques.

**Vérifié** : rendu Chromium 1280 px et 390 px, `scrollWidth` mobile = 390
(aucun débordement), zéro erreur JavaScript.

## 5. Deux modes de fonctionnement
- **Live** : servi par le backend → `/v1/dashboard` puis flux SSE.
- **Démonstration** : ouvert seul → jeu de données réaliste, **bandeau explicite**
  « aucun backend joignable ». L'utilisateur sait toujours ce qu'il regarde.

## 6. Avertissement permanent
Pied de page présent sur tous les écrans : outil d'aide à l'analyse, **aucun
signal d'achat ou de vente**, ne remplace pas le jugement, ne constitue pas un
conseil en investissement, technique = ressort de l'indicateur externe.

## 7. Definition of Done
- [x] Sombre, minimaliste, professionnel, responsive.
- [x] Tous les domaines du Tome 0 représentés.
- [x] Fonctionne avec et sans backend, sans jamais tromper l'utilisateur.
- [x] Accessibilité et absence de débordement vérifiées par rendu réel.

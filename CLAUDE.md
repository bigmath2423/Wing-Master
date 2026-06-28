# Wing Master — Règles de travail (Skills)

Jeu : **Wing Master** (Flappy-like premium). Un seul fichier principal : `index.html`
(jeu sur `<canvas>` + interface du menu en vrai **HTML/CSS** posée par-dessus, calée
dans un repère 400×640 mis à l'échelle par `transform:scale`).

Objectif global : rendu **jeu mobile premium** (style Clash Royale / Supercell) sur tout
le jeu : ligues, oiseaux, œufs, boutique, classement.

## Règles permanentes (résumé — à respecter à CHAQUE modification)
1. Rendu **premium 4K réaliste**, **jamais** arcade / cartoon cheap.
2. Style **jeu mobile haut de gamme** type **Supercell / Clash Royale** (profondeur,
   lumière, textures, ombres, reflets, contours dorés, contraste).
3. **Ne jamais superposer** d'éléments par-dessus l'ancien design.
4. **Modifier le système complet**, pas seulement une ligue.
5. **Garder toutes les fonctionnalités existantes** (aucune régression).
6. **Vérifier** que HTML/CSS/JS ne cassent pas (node --check + rendu headless + erreurs).
7. **Appliquer le style premium partout** : toutes les ligues, menus, boutique, œufs,
   oiseaux et classement.
8. **Toute modification va DIRECTEMENT dans `index.html`** (fichier de jeu unique et
   autonome). Les assets (images) sont **embarqués en base64** dans `index.html` pour
   qu'il fonctionne ouvert seul, sans dépendance externe.


## Skill 1 — UI premium mobile game
- Viser un rendu **premium** : profondeur, lumière, ombres réalistes, textures, reflets,
  contours dorés, contraste. **Pas** d'aspect plat / arcade / cartoon cheap.
- Limite technique honnête : **aucun générateur d'images IA** n'est disponible dans cet
  environnement. Le « 4K peint à la main » exige de **vraies images d'assets** fournies
  par l'utilisateur. À défaut, livrer le meilleur rendu **vectoriel (canvas/SVG) + CSS**
  possible, et **intégrer** toute image HD fournie.

## Skill 2 — Ne pas superposer
- Ne jamais coller un effet/une image **par-dessus** l'ancien design.
- Modifier le **système complet** : un seul style premium **appliqué automatiquement aux
  9 ligues**. Chaque ligue garde uniquement **son fond, son blason et sa couleur**
  (variable CSS `--accent`, `LEAGUE_COLORS`), l'interface étant **identique partout**.

## Skill 3 — Code propre
À chaque modification :
- **Ne pas casser** le jeu existant ; **garder** les fonctions déjà présentes.
- **Ne pas toucher** au gameplay, aux collisions/hitbox, à la physique, aux récompenses,
  à la progression ni à la sauvegarde (changements **visuels uniquement**, sauf demande
  explicite).
- **Ne pas changer les positions** des composants sauf demande explicite.
- **Vérifier les erreurs** HTML/CSS/JS avant de livrer (`node --check` sur le JS extrait,
  rendu réel via navigateur headless, capture des erreurs console).
- **Faire une sauvegarde** avant gros changement (dossier `backup/`).
- **Expliquer** les fichiers modifiés et ce qui a changé.

## Skill 4 — Pipeline d'assets (découpe de planches)
*Adapté de « visual-asset-generator » : pas de génération IA ici → on extrait depuis les planches fournies.*
- Méthode éprouvée pour découper une planche en pièces/frames propres :
  1. Détourer le fond (flood-fill / seuil de luminance), garder la **plus grosse
     composante connexe** (supprime confettis, lignes de vitesse, parasites).
  2. **Autocrop** sur l'alpha, puis **recadrage**.
  3. Pour une **animation** (strip de frames) : aligner toutes les frames d'un même état
     par **centroïde + échelle uniforme** (corps stable, ailes/tête bougent → pas de jitter).
  4. Exporter en PNG transparent, taille raisonnable (≈256px), puis **embarquer en base64**
     dans `index.html`.
- Toujours **vérifier par un montage** (planche-contact) avant d'intégrer.

## Skill 5 — Animation vivante (modèle officiel + moteur générique)
*Adapté de « game-developer » : discipline d'états d'animation.*
- Le **moineau** est le **modèle officiel** (frames découpées de sa planche, embarquées
  `EMBED_MOINEAU`). Modèle **frame-based** : chaque état est un jeu d'images dessinées
  (les pièces corps/tête/ailes/queue/œil/bec/pattes y sont déjà animées et alignées par
  construction — pas de rig à os, on garde la qualité « peinte »).
- **Moteur générique réutilisable** (zéro modif pour les 54 autres) :
  1. `registerBirdAnim('<id>', EMBED_<ID>)` → charge les frames dans `BIRD_ANIM['<id>']`.
  2. `anim:'<id>'` sur le skin.
  `birdAnimState()` choisit l'état, `birdAnimFrame()` rend la frame. État stocké **par skin**
  (`skin._anim`) → aucun mélange entre oiseaux.
- États : `idle` · `vol` · `montee`/`descente` (selon `bird.v`) · `blink` aléatoire au repos
  · `victoire`/`défaite` au game over · `spawn` (apparition au début de partie) · `eclosion`.
- **Surcouche procédurale** dans `drawBird()` (branche `isAnim`) : flottement du corps,
  squash & stretch léger sur l'impulsion, micro-balancement, ombre portée, plumes discrètes
  au battement (menu). **Aucune** distorsion parasite ni fantôme : oiseau **net et 100% opaque**.
- Repli `drawBird()` sprite/vecteur inchangé pour les oiseaux non encore riggés (zéro régression).

## Skill 6 — Revue visuelle avant livraison
*Adapté de « ui-designer » : checklist de design review.*
- Avant de livrer, passer l'écran au crible : **hiérarchie** (titre > stats > actions),
  **alignement / espacements** réguliers, **contraste** lisible, **cohérence** des boutons,
  ombres et contours dorés, **pas de débordement** hors du repère 400×640.
- Comparer **avant/après** par capture headless ; vérifier que rien n'est **superposé**
  ni régressé sur les **9 ligues**.

## Skill 7 — Générateur d'oiseaux procédural (code, sans IA d'image)
*Réalité technique : aucun générateur d'images IA dans cet environnement. On « génère »
les oiseaux et leurs animations DIRECTEMENT en code (canvas vectoriel), 0 dépendance.*
- `drawBird()` est le **générateur** : corps/ventre/aile/queue/œil/bec paramétriques,
  recolorables par skin (`body/belly/wing/beak`) + accessoires (`horns/crown/bigwings/
  sparkle/rainbow/ghost/cosmic`). Variété = couleurs + accessoires + features.
- Animations générées en code : respiration, battement (`flapT`), balancement de queue,
  clignement périodique, inclinaison selon la vélocité en jeu (`bird.rot`).
- **Expressions d'humeur** (`mood`) pilotées par l'état : `happy` (yeux plissés joyeux)
  au record/victoire, `sad` (œil mi-clos + larme) à la défaite, sinon neutre. Forçable
  via `opts.mood`. S'applique à **tous** les oiseaux vectoriels.
- Le moineau garde ses **vraies frames** (planche) ; les autres utilisent le générateur.
  Pour passer un oiseau en frames : fournir sa planche → pipeline Skill 4 + `anim:'<id>'`.

## Skill 8 — Pratiques AAA « façon Unity », adaptées HTML/CSS/JS (auto)
*À appliquer AUTOMATIQUEMENT à chaque modif, sans demander. Le projet reste 100% HTML/CSS/JS :
on s'inspire des techniques Unity, on ne convertit jamais vers Unity.*

Correspondances Unity → Web (à utiliser quand pertinent) :
- **Tweening / DOTween / easing curves** → `transition`/`@keyframes` avec `cubic-bezier`,
  ou Web Animations API. Courbes maison : `--ease-out-back`(overshoot), `--ease-spring`,
  `--ease-out-quint`. Jamais de mouvement linéaire pour de l'UI.
- **Coroutines / Update()** → `requestAnimationFrame` (boucle `loop()` existante) ;
  timers d'état via compteurs de `frame`. Pas de `setInterval` pour l'animation.
- **Object pooling** (particules) → pools/limites strictes : `fxParts` plafonné, peu de
  nœuds GPU (cf. `.hb-air` = 6). Réutiliser, ne pas spammer.
- **Canvas Scaler / anchors** → repère fixe 400×640 mis à l'échelle (`#home` + `transform:scale`).
- **Game feel / juice** : squash & stretch sur impulsion, anticipation, rebond (overshoot),
  micro-décalages, hit-stop léger, parallax du fond, ombre dynamique. Toujours subtil.
- **Feedback / micro-interactions** : chaque bouton = état `:hover` (lift+glow) + `:active`
  (rebond/scale) ; halo lumineux ; retour « haptique » simulé (bounce). 
- **Polish UI/UX** : hiérarchie (titre > stats > actions), espacements réguliers, contraste,
  cohérence des contours dorés, profondeur (ombres réalistes + reflets + glassmorphism léger).
- **Transitions d'écran** : entrées animées (`hbIn*`), jamais d'apparition brutale.

Performance (priorité mobile, non négociable) :
- Animer **uniquement** `transform` et `opacity` (compositeur GPU). Éviter d'animer
  `width/height/top/left/box-shadow` en boucle sur beaucoup d'éléments.
- `will-change` ciblé sur les éléments réellement animés ; pas partout.
- Ne pas recréer de gradients/objets lourds **par frame** (les mettre en cache).
- Respecter `prefers-reduced-motion`.
- Désactiver les effets lourds hors écran ou en `performanceMode` (cf. `lite`/`homeLite`).

## Architecture à connaître (pour ne rien casser)
- `EMBED_WORLDS` (fonds de jeu, propres), `EMBED_LEAGUES` (blasons PNG),
  `EMBED_SKINS` (anciennes images d'accueil avec UI cuite — **plus utilisées** pour le menu).
- Menu : `renderMenuClean()` (canvas : fond propre de la ligue + oiseau animé) +
  `#home` (HTML/CSS) synchronisé par `updateHomeDOM()` / affiché par `setHomeVisible()`.
- Oiseau : `drawBird()` **paramétrique** (51 skins recolorables) — ne pas le remplacer par
  un sprite unique.
- Œufs : `drawEgg()` / `drawEggShape()`. Tuyaux : `drawColumn()` / `drawPipeMotif()`.
- Helpers partagés (tous les écrans canvas) : `premBtn`, `premPanel`, `glossPill`,
  `roundRect`, `ct`, `txt`, `shade`, `cLin`, `cRad`, `goldGrad`.
- Clics du menu HTML branchés sur les fonctions existantes (`action`, `openShop`,
  `openPass`, `openEvents`, `state='...'`) — ne pas modifier la logique d'interaction.

## Vérification rapide (avant chaque livraison)
1. Extraire le JS et `node --check`.
2. Rendre via Playwright (Chromium dispo dans l'env) les 9 ligues + écrans modifiés,
   capturer `pageerror`/console → **NO_ERRORS**.
3. Commit clair + push sur la branche de travail, puis expliquer les fichiers modifiés.

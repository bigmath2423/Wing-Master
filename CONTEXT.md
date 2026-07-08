# CONTEXT.md — reprise dev Wing Master (état au commit `4eb7d70`)

## Repo / branche
- Branche de travail : `claude/new-session-ypz3kj` (fusion de `claude/new-session-6pqp8x` + `main`).
- Fichier unique : `index.html` (~27,7 Mo, autonome, tout en base64). Zéro dépendance externe.
- Assets sources : uploadés par l'utilisateur sur `main` (`accueil-N-*.webp`, `fond-N-*.webp`, `tuyau-N-*-haut/bas.webp`).
- Sauvegardes locales : `backup/` (gitignoré).

## Structure index.html
- 3 `<script>` inline : ① PipeSkins (tuyaux 9 ligues) ② assets EMBED_* ③ logique jeu.
- Canvas `#game` 400×640 logique, backing store ×devicePixelRatio (`resize()`).
- `#home` = HUD HTML/CSS scalé (repère 400×640, `transform:scale`).
- Ligues (index 0-8) ↔ thèmes : debut, berlin, sydney, newyork, paris, tokyo, moscou, islande, fuji.
- Seuils ligues : 500·1000·1500·2000·2500·3000·3500·4000 (test : `flappy_trophies` 50→4050).

## Systèmes clés (ajoutés cette session)
### Accueil FULL-BAKED (ligues 1-8)
- `EMBED_HOMES[theme]` : image accueil nid-vide, pleine résolution 1024×1536, WebP q90.
- Actif si `homeImg[theme]` existe → `#home.baked` + `data-bkth=theme` (dans `updateHomeDOM`).
- Rendu : `drawHomeBg(th)` = cache offscreen ×DPR, `imageSmoothingQuality='high'`, blit/frame.
- UI vectorielle masquée, hitboxes invisibles recalées (CSS `#home.baked ...`, mesures cover 400×640) :
  MISSIONS(0,185,100×70) CADEAU(2,256,95×95) PASS(2,354,92×92) ŒUF/nids(308,183,92×80)
  CLASSEMENT(308,266,92×95) ÉVÉNEMENTS(306,364,94×92) ROUE(310,458,90×74)
  PANNEAU(118,75,167×255) VOLER(104,518,192×68) NAV(0,585,h55).
- Valeurs réelles par-dessus zones cuites : `.hb-bkval` (trophées), `.hb-bkonl` (en ligne),
  `.hb-bkbar` (barre progression réelle, ligues 2-9), `.hb-bkbadge` (badge cadeau conditionnel).
  Positions/couleurs PAR THÈME (CSS `#home.baked[data-bkth=...]`, échantillonnées sur chaque image).
- Ligue 9 (fuji) : FAIT — image PNG source nettoyée (badge inpainté+miroir de coin, hibou retiré :
  haie de cerisiers par patchs propres, cuvette tressée, liseré bas du panneau reconstruit
  par étirement d'échantillon fin — JAMAIS de tuilage de bandes larges, ça répète le décor).

### Oiseau équipé vivant dans le nid
- `NEST[ligue]={cx,cy,scale,rimCy,rimRx,rimRy}` (mesures par fond, coords jeu).
- Ordre par frame : fond (`drawHomeBg`, blit de `_hbgCv`) → oiseau dessiné **DIRECT** par
  `drawBird(..., {homeLite:true, nest:true})` (nest = SANS glow/FxBack ni ombre portée) →
  **calque rebord** `_rimLayer(cur)` blitté 1:1 pixels device.
- `_rimLayer` : offscreen taille canvas, clip elliptique de la crête (NEST) puis copie de
  `_hbgCv` (le FOND SOURCE). Construit 1 fois par (ligue, thème, DPR). **AUCUNE lecture du
  canvas principal nulle part** (l'ex-`nestBirdCache` + zone brouillon a été SUPPRIMÉ).
- Idle : bob ±2px/2.4s, respiration scaleY ±0.015, squash 0.94/120ms toutes les 3-6s, rot ±1.5°, pivot bas-centre.
- `drawBird` unités : x −35..+20 (centre visuel −7.5), y −21..+17 ; équivalence ancien blit :
  translate(cx,cy)·scale(s) puis translate(7.5,−17) en unités oiseau.
- Les 8 accueils 1-8 ont été RE-NETTOYÉS (la « colonne floue » vue à l'écran était de la
  bouillie d'inpainting CUITE dans EMBED_HOMES, pas un bug de rendu) : fond re-synthétisé
  par patchs 2D depuis des rectangles PROPRES de la source (jamais de rangées tuilées),
  cuvette retissée, houppette/serres retirées (script `repair_homes2.py`, scratchpad).

### Tuyaux (PipeSkins, script ① inline)
- `SKINS[skin].top/bottom = {r,c,b64}` ; `LEAGUE_SKINS=['foret','glace','ocean','usine','chateau','temple','deco','cristal','fuji']`.
- Calibration validée : `r = 1.28·iw/bbox_alpha_w`, `c = centre bbox` (reproduit foret ±2 %).
- `cropAlpha()` au décodage (marges transparentes) + `OVER=2` (bouts collés hors écran).
- Collision lit UNIQUEMENT `p.x/PIPE_W/gapY/GAP` — jamais l'image.

### Fonds de jeu
- `EMBED_WORLDS[theme]` : 900×600 WebP q80 (gameplay + écrans canvas).

## Pièges connus (ne pas répéter)
- JAMAIS l'outil Edit sur gros blobs base64 → scripts Python + `assert count==1`.
- `<script>` et `var EMBED_X=` sur MÊME ligne → insérer après la balise, pas en début de ligne.
- Valider chaque b64 modifié : décodage + signature (RIFF/WEBP, PNG magic).
- `owned` (peaux) indexé par **id de skin**, pas index. Équiper : `equipBird(i)`.
- 1er clic parfois avalé à ~4s (décodage images) → tests : attendre 5,5s + retry.
- Clic synthétique `dispatchEvent` peu fiable en mode baked → `page.mouse.click(x,y)`.
- Inpainting grosses zones = bouillie → multi-échelle + greffes latérales + cuvette peinte ; zone tête à remplir depuis le LISERÉ du panneau (l'oiseau cuit dépasse à côté de la pointe).
- `renderMenuUI()` = code mort. Menu réel = `renderMenuClean()`.

## Vérif standard avant livraison
1. Extraire les 3 scripts inline → `node --check` chacun.
2. Playwright (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, `--no-sandbox`) :
   9 ligues (menus baked + parties), clics par coordonnées, valeurs via localStorage
   (`TestReel/7/4321/87/123/55`), zéro erreur console, fps.
3. Commit français détaillé + push `-u origin claude/new-session-ypz3kj` + SendUserFile index.html.
- Scripts prêts (scratchpad session précédente) : `all_menus.js`, `all_games2.js`, `bird_test.js`,
  `realvalues.js`, `screens.js`, `baked_test.js`, `pipes_test.js`, `probe9.js`.

## Historique commits session (ordre)
`5843690` fix barre haut cuite → `139ad47` tuyaux M1 pleine qualité → `7ebb4c2` PipeSkins inline
→ `08908a1` bords tuyaux collés → `4580af9`/`46a4656`/`25ffe51`/`e5734fa`/`c35583a` itérations nid
→ `cbfcf5f` full-baked L1 → `68d9b64` mondes 2-9 complets → `332804b` HD + oiseau vivant
→ `4eb7d70` patch rebord courbe + sprite net.

## TODO
- [x] `accueil-9` (fuji) : intégré (EMBED_HOMES.fuji, NEST[8]={cx:206,cy:460,scale:2.10,rimCy:433,rimRx:86,rimRy:16}, CSS fuji : bkval top271 #000f16, bkonl top317 h19 #01111a, bkbar top294 #011017).
- [ ] Badge visible seulement si cadeau dispo : OK (synchro `#h-bg`) — revérifier après tout changement de la logique cadeau.
- [ ] Si pixelisation signalée sur mobile réel : vérifier `devicePixelRatio` >2 (cap frames ×2.2).

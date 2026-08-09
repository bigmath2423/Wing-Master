# Audit v13 — code contre la stratégie formalisée (SETUP_GRADING.md)

Document d'audit. **Aucun fichier `.pine` n'a été modifié.** Classement par
composant, 8 catégories :

1. Correct et utile · 2. Correct mais mal implémenté · 3. Redondant ·
4. Trop permissif · 5. Trop restrictif · 6. Susceptible de repaint ·
7. Risque d'overfitting · 8. Impossible à mesurer correctement

## Structure (pivots, BOS, CHoCH, `trend`)

| Élément | Catégorie | Constat |
|---|---|---|
| `ta.pivothigh/pivotlow(swingLen=10)` | **1**, mais cause n°1 des entrées tardives | Non-repeinte (valeur figée une fois confirmée) mais **retardée de 10 bougies par construction** — c'est le prix mécanique du non-repaint. Aucun correctif ne peut réduire ce délai sans réintroduire du repaint. |
| `var int trend` mis à jour par `if bullBos: trend := 1` | **6 — repaint, PRIORITAIRE** | Aucun garde `barstate.isconfirmed`. `bullBos` dépend de `close` (prix courant, pas figé). En direct (graphique temps réel, donc le fichier indicateur ET tout usage du fichier stratégie hors Strategy Tester), une mèche intra-bougie qui franchit `swingHigh` PUIS repart avant la clôture peut forcer `trend := 1` sur un tick intermédiaire — et rien ne le corrige si `bullBos` redevient faux à la clôture, car `trend` est un `var` qui ne revient jamais en arrière tout seul. Un `trend` corrompu peut fausser `alignLong/alignShort` sur les bougies suivantes. **Concerne directement le forward test prévu.** |
| `crossUp = ... and swingHigh == swingHigh[1]` | **3 — redondant** | Presque toujours vrai (`swingHigh` ne change que sur la bougie de mise à jour du pivot). Le rôle réel de cette clause n'est pas clair dans le code actuel — à documenter ou simplifier. |
| CHoCH (`bullChoch/bearChoch`) | **1** techniquement, **8** en tant que concept | Sous-produit correct du calcul de BOS. Déjà su : effet non significatif isolé, affichage seul. |

## Filtres de contexte (HTF EMA, VWAP, Biais, POC)

| Élément | Catégorie | Constat |
|---|---|---|
| `htfBull/htfBear` (EMA de l'unité supérieure) | **1** | `request.security` avec `close[1]`/EMA `[1]` + `lookahead_off` : non-repeinte, correctement implémenté, mesuré (+0.016 / +0.096). |
| `htfTf`, `htfEmaLen`, `swingLen`, `atrLen`, `cooldown` | **8** | Ces 5 paramètres sont dans le groupe *"① Moteur (ne pas modifier sans mesure)"* mais **aucun n'a de tooltip de mesure** — contrairement à `useHtf`, `useVwap`, `useBias`, `slAtr`, `exitMode`, qui citent tous un chiffre. Ironie du nom du groupe : ce sont justement les seuls paramètres du moteur dont l'audit ne trouve aucune preuve de validation individuelle documentée dans le fichier. |
| VWAP (`ta.vwap(hlc3)`) | **1** logique, **8** portée | Correctement gaté par `barstate.isconfirmed` avant décision. Mais `ta.vwap()` sans ancre explicite dépend de la notion de "session" que TradingView attribue au symbole — **non vérifié** que ce comportement soit cohérent entre XAUUSD (CFD, quasi 24/5), BTCUSD (24/7, pas de session), et le forex (sessions calendaires classiques). Risque direct pour la validation multi-actifs prévue. |
| Biais D1+W1 | **1** | Module qui porte le système, mesuré, bien implémenté, sans repaint. |
| POC / Value Area veille (`abovePoc/belowPoc`, `vUsePoc`) | **1** logique, **8 — PRIORITAIRE** | Calcul correct (aucune donnée future). Mais repose entièrement sur `volume`, qui **n'a pas de définition universelle sur un instrument spot/CFD comme l'or** (pas de volume centralisé — le champ est un proxy broker, souvent un compte de ticks). `vUsePoc` est décrit comme *"le seul concept de liquidité qui améliore le système"* : si cette amélioration mesurée est un artefact du proxy de volume de TVC:GOLD spécifiquement, elle ne se transportera pas telle quelle vers un symbole broker réel — ni vers les autres actifs du plan de validation. À vérifier explicitement : que représente `volume` sur le symbole utilisé pour le forward test ? |
| `pdhPrev` / `pdlPrev` | **3 — mort** | Calculés (lignes 210-253) mais jamais lus ensuite — ni dans la décision, ni dans l'affichage. |

## Déclencheur (BOS / Donchian / displacement)

| Élément | Catégorie | Constat |
|---|---|---|
| `trigMode` (BOS vs Donchian) | **1** | Deux formulations mesurées équivalentes (+0.011 R, p=0.89), implémentation correcte. |
| `useImb` (displacement seul) | **1** (correctement désactivé) | Mesuré dégradant (PF 1.13→1.08), désactivé par défaut avec avertissement explicite dans le tooltip. Reste exposé dans l'UI — acceptable puisque le risque est documenté, mais un utilisateur pressé pourrait l'activer sans lire. |

## Exécution — la découverte la plus importante de cet audit

| Élément | Catégorie | Constat |
|---|---|---|
| `process_orders_on_close=true` + `commission_value=0.0` + `slippage=0` | **7/8 — PRIORITAIRE** | Le backtest remplit chaque ordre **exactement à la clôture de la bougie de signal**, sans coût, sans slippage. C'est **impossible à reproduire en réel** : un trader ne peut agir qu'APRÈS la clôture qu'il vient d'observer, donc au mieux à l'ouverture de la bougie suivante, avec un spread et un slip non nuls sur l'or. Cet écart entre l'hypothèse du backtest et l'exécution réelle est probablement la explication la plus concrète et la plus actionnable à *"pourquoi mes entrées en direct arrivent plus tard / à un prix différent de ce que montre le backtest"*. Ce n'est pas un bug — c'est un choix de simulation qui n'a encore jamais été confronté à son coût réel. |
| `f_qty` + `maxLev` | **1** | Garde-fou ajouté après un incident réel documenté (TVC:GOLD, levier ×20 à ×128). Bon exemple d'ingénierie défensive. |

## Sortie (stop, trailing, TP fixe)

| Élément | Catégorie | Constat |
|---|---|---|
| `slAtr = 2.5` | **1**, partiellement mesuré | Comparé à 1.5×ATR (negatif sur 2/4 sous-périodes) — deux valeurs testées, pas un balayage complet. Acceptable, mais ce n'est pas la preuve exhaustive que le libellé "mesuré" pourrait laisser croire. |
| Trailing (1.5R arm / 0.3R suivi) vs TP fixe (0.5R) | **1** | Le plus rigoureusement documenté du fichier : 783 trades, 200 hors échantillon (2020-2022), compromis chiffré explicitement des deux côtés. Référence de ce qu'une mesure correcte doit ressembler. |

## Affichage seul (OB, FVG, liquidité, zones hebdo, MTF, contexte)

| Élément | Catégorie | Constat |
|---|---|---|
| OB / FVG / sweep / CHoCH | **8**, déjà correctement étiqueté "affichage seul" | Vérifié à nouveau : aucune de ces variables n'apparaît dans `alignLong/alignShort/trigLong/trigShort/buySignal/sellSignal`. La séparation A (calcul) / B (décision) / C (affichage) que tu demandes dans ton nouveau message est, dans les faits, **déjà appliquée** ici — elle n'est simplement pas nommée ainsi dans le code. |
| Zones institutionnelles hebdomadaires | **1** | Score figé à la création, invalidation événementielle (corrigée cette session), ne génère aucun trade. Hérite du même risque **8** que la POC (repose en partie sur le même profil de volume). |
| Contexte régime (`ctxCode`) | **1** | Ne contrôle que l'affichage des zones, jamais `buySignal/sellSignal` — correctement isolé. |
| Panneau MTF (M5/M15/H4/D1) | **1** | Explicitement lecture seule, le rejet du M5 comme filtre est documenté (4 méthodes). |
| Grade A+/A/B/INVALID | **1** par construction | Reprend terme à terme `alignLong/alignShort`, y compris les interrupteurs — ne peut pas diverger de `buySignal/sellSignal` par construction. A/B restent catégorie **8** (jamais validées isolément), et le code l'affiche littéralement à l'écran. |

## Corrections prioritaires (par ordre d'impact)

1. **Repaint de `trend` en direct** — ajouter une garde de confirmation avant d'écrire `trend := 1/-1`, ou ne lire `bullBos/bearBos` qu'à `barstate.isconfirmed`. Impact direct sur le forward test et tout usage live de l'indicateur.
2. **Hypothèse d'exécution du backtest** — tester une version avec `process_orders_on_close=false` (remplissage à l'ouverture suivante) et un spread/slippage réaliste pour XAUUSD, pour savoir si l'espérance mesurée (+0.137 R) survit au coût réel d'exécution.
3. **Nature du champ `volume`** — vérifier ce qu'il représente sur le symbole broker qui servira au forward test ; documenter si `vUsePoc` (le seul filtre de liquidité qui gate un trade) reste valide avec ce proxy.
4. **Ancrage de session du VWAP** — vérifier la cohérence du comportement entre XAUUSD, crypto (24/7) et forex avant la validation multi-actifs.
5. **Paramètres moteur non documentés** (`swingLen`, `atrLen`, `htfTf`, `htfEmaLen`, `cooldown`) — soit retrouver/ajouter la mesure qui les justifie, soit l'écrire explicitement : "valeur historique, jamais balayée".
6. **Nettoyage mineur** — supprimer `pdhPrev/pdlPrev` (code mort) ; clarifier ou simplifier `swingHigh == swingHigh[1]`.

Rien ci-dessus ne touche `alignLong/alignShort/trigLong/trigShort/buySignal/
sellSignal` : ces lignes restent, comme toujours, la référence à ne pas
modifier sans preuve.

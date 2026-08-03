# XAUUSD SMC — Document de référence du projet

*Résumé compact de la conversation. Remplace le besoin de relire l'historique complet.*

---

## 🎯 Objectif du projet

Transformer un indicateur TradingView Pine Script v6 (SMC/ICT sur XAUUSD) en outil
**rentable et utilisable en réel**, via une méthode de développeur quant :
- Une amélioration à la fois, chacune derrière un interrupteur indépendant
- Mesurer avant de décider (A/B, jamais d'intuition)
- Ne jamais casser ce qui fonctionne ; réversible à tout moment

## 👤 Contraintes de l'utilisateur

- **Broker** : FXCess, compte Classic. **Spread réel mesuré sur XAUUSD = 0,95** (le
  site annonce 0,42, valeur vitrine à ignorer).
- **Rentable en manuel** avec les zones (Order Block / FVG / Premium-Discount) — le
  problème n'est pas l'analyse, c'est que le déclencheur automatique tire sur des
  configurations qu'il ne prendrait pas à la main.
- Veut **peu de signaux mais fiables**, puis a demandé l'inverse (minimum 3
  trades/jour) après avoir constaté que le sur-filtrage donnait ~5 trades/an.
- Ne compile pas Pine lui-même dans un IDE tiers : tout se teste directement dans
  TradingView (Éditeur Pine + Strategy Tester).
- Aucun accès à un compilateur Pine côté assistant → toute validation de syntaxe se
  fait par revue statique, jamais par exécution réelle.

---

## 📂 Fichiers du projet (`/home/user/Wing-Master/indicator/`)

| Fichier | Rôle |
|---|---|
| `xauusd_smc_v14_baseline.pine` | **Référence gelée**, jamais modifiée. Indicateur d'origine (2632 lignes, 146 inputs). |
| `xauusd_smc_working.pine` | **Fichier principal actif.** Ancien indicateur complet + tous les correctifs/améliorations. |
| `xauusd_smc_STRATEGY.pine` | Copie stricte de `working.pine` convertie en `strategy()` pour le Strategy Tester. Le corps ne diffère de l'indicateur QUE sur la ligne 2 (déclaration) — vérifié à chaque régénération. |
| `xauusd_smc_PRO.pine` | Version alternative **allégée** (944→912+ lignes) : Wyckoff/RSI/DXY/volume/sessions retirés du calcul (pas juste masqués), moteur reconstruit autour de Biais→Premium/Discount→Liquidité→Sweep→CHoCH/BOS→FVG/OB→Fibonacci→Risque. Utilisée en parallèle, pas la voie principale retenue par l'utilisateur. |
| `xauusd_smc_PRO_STRATEGY.pine` | Version strategy() de PRO. |
| `ABLATION.md` | Journal détaillé de toutes les modifications, protocole de backtest, résultats mesurés. |
| `BACKTEST_RESULTS.md`, `backtest-app.html` | Gabarit et mini-app HTML pour consigner des résultats A/B (winrate, PF, expectancy). |
| `journal-app.html` | App HTML autonome : journal de trading (R:R, win rate, calendrier P&L, courbe de capital, filtres, objectif mensuel). Risque saisi en **lot** (auto-calcul via lot × valeur × distance SL), pas en argent brut. |

**Décision de l'utilisateur** : `xauusd_smc_working.pine` est le fichier de référence
à faire évoluer (« l'ancien est bon, juste moins de faux signaux, plus précis »).

---

## 🐛 Bugs corrigés (tous dans `working.pine`, chacun avec son toggle)

| ID | Toggle | Défaut | Problème corrigé |
|---|---|---|---|
| **B1** | `fixBreakOn` | ON | Faux BOS/CHoCH : `ta.crossover` se déclenchait quand un pivot faisait bouger le niveau de swing lui-même, pas une vraie cassure. Fix : garde de stabilité (niveau doit être identique à la barre précédente). |
| **B2** | `fixSweepGateOn` | ON | Le toggle d'affichage `showLiq` désactivait aussi la détection de sweep utilisée par le score — un réglage visuel ne doit jamais changer la logique. |
| **B1b** | `fixBreakMtfOn` | OFF | Même bug que B1 mais dans `f_msStructure()` (structure multi-timeframe), qui alimente le score HTF. |
| **C1** | `sigConfirmOn` | ON | Repaint intrabar : la flèche de signal pouvait apparaître/disparaître avant la clôture de la bougie. Neutre en backtest (barres historiques toujours confirmées), utile en réel. |
| **B3** | `fixTpSnapOn` | OFF | Le buffer d'exécution repoussait les TP au-delà de leur niveau structurel pour préserver le R:R nominal — arbitrage non tranché (hit-rate vs R:R affiché). |
| **S1** | `scoreRealistOn` | OFF | La « Probabilité » affichée = score brut, qui contient un plancher structurel garanti (~25 pts) — recalibrage d'affichage uniquement, aucun impact sur les trades. |
| **P1** | `obBodyOnly`, `obNeedDisp`, `entryCE` | ON | **Le plus impactant** : l'Order Block était pris mèche-à-mèche (au lieu du corps de bougie), sans exiger de displacement, et l'entrée se plaçait au bord de la zone au lieu du Consequent Encroachment (50%). Zone 2-3× plus étroite et plus précise après correction. |

---

## 🎛️ Améliorations structurelles ajoutées

### A1 — Mode « Alignement Total » → devenu un **quorum réglable**
- Départ : exiger les 6 critères de qualité simultanément (biais, pas d'entrée
  tardive, ADX directionnel, bon côté Premium/Discount, zone OB/FVG touchée, sweep
  adossé à la cassure) → ne laissait **que ~6 trades/an**. Diagnostic : sur-filtrage.
- Solution : `saMinCount` = nombre de critères exigés parmi les 6 activés (au lieu
  de tous). Affichage du score `X/Y crit.` sur chaque signal pour calibrer.
- Historique des réglages : 4/6 → (utilisateur veut plus de fréquence) → **2/6**.

### Calibrage spread broker (0,95 $, FXCess)
- `slExecBufSpread` = 1.10 (spread + marge slippage) — le stop n'est jamais placé
  plus près que le coût d'exécution réel.
- `slMinAtr` = 1.2 ATR (au lieu de 0.5) — un stop trop serré se fait balayer par le
  spread + une mèche sur l'or.
- Stratégie (`STRATEGY.pine`) : `slippage = 950` ticks (⚠️ attention à la taille du
  tick du symbole : TVC:GOLD cote en 3 décimales → tick=0.001 → 0,95$=950 ticks ;
  un symbole 2 décimales donnerait 95 ticks — à vérifier selon le flux utilisé).
- Formule de seuil de rentabilité dérivée : `W_équilibre = (1 + spread/SL) / (R:R+1)`.
  Conclusion : augmenter le R:R (viser plus loin) réduit l'exigence de win rate bien
  plus efficacement que d'essayer d'augmenter le taux de réussite.

### Réglages desserrés pour plus de fréquence (dernière étape)
Suite à la demande « minimum 3 trades/jour » (⚠️ objectif non garantissable par
réglage — dépend du marché) :

| Réglage | Avant | Après |
|---|---|---|
| `saMinCount` | 4/6 | **2/6** |
| `deScoreMin` | 80 | **70** |
| `signalCooldown` | 10 | **3** |
| `structLookback` | 30 | **45** |
| `deSweepWindow` | 20 | **30** |
| `wyUseFilter` | ON | **OFF** |
| `pfUseVolFilter` | ON | **OFF** |

**Risque explicite documenté** : ce desserrage peut faire retomber le profit factor
sous 1.0 (zone vue tout au début du projet). À confirmer par re-backtest.

### Version PRO — nettoyage complet du moteur de décision
Sur demande explicite (« pas juste masquer, retirer du calcul ») : Wyckoff,
Accumulation/Distribution, RSI/Stochastique, DXY, rendements 10Y-2Y, news, sessions,
filtre volume, Breakers, Imbalances, ADX, entrée tardive, zones potentielles/
anticipation, panneau MTF, labels de swing — **supprimés du code**, vérifié à
zéro occurrence hors commentaires. Score /100 rééquilibré (Liquidité 25 + Structure
25 + OB/FVG 20 + Biais 15 + Prem/Disc 10 + VWAP 5). Ajouts : cycle AMD (Accumulation/
Manipulation/Distribution, dérivé de l'état existant, zéro calcul supplémentaire),
zones Buy/Sell Limit anticipées notées /100 avec resserrage par confluence (mécanisme
porté depuis l'ancien Module 10) et clip sur la bande OTE Fibonacci (0.618-0.786).

---

## 📊 Résultats de backtest mesurés (par l'utilisateur, XAUUSD M15, TVC:GOLD)

| Test | Trades réels | Win rate | Profit Factor | Note |
|---|---|---|---|---|
| Tout premier run | 65 | — | **0.59** | Slippage mal réglé (95 au lieu de 950 ticks — 10× trop optimiste) |
| Après B1/B2/B1b + P1 + A1 (quorum 4) | ~29 | 53% | **1.337** (ADX off) | ADX (`chopFilterOn`) testé ON → dégrade à 0.90 : **confirmé, rester OFF** |
| Export CSV réel 6 ans (2020-2026) | **29 signaux réels** (79 "trades" comptés par TradingView = légs de sortie partielle TP1/TP2/TP3) | 51.7% | **1.215** | Profit net 6 ans = seulement +260$ (+2.6%) sur 10 000$ — PF positif mais rendement absolu faible, fréquence trop basse (~5/an) pour un usage pratique |

**Point méthodologique important découvert** : le Strategy Tester TradingView compte
chaque sortie partielle (TP1/TP2/TP3) comme un "trade" séparé → le nombre affiché est
gonflé ~2,7× par rapport au nombre réel de signaux/positions. Toujours diviser par 3
(ou compter les entrées distinctes) pour le vrai chiffre.

---

## 🧭 État actuel (dernier point avant ce résumé)

- Réglages desserrés poussés (`working.pine` + `STRATEGY.pine` régénérée, diff
  corps = ligne 2 uniquement, vérifié).
- **En attente** : nouveau backtest 6 ans par l'utilisateur avec les réglages
  desserrés, à comparer au run précédent (29 trades / WR 51.7% / PF 1.215).
- Critère de décision : si PF reste > 1.1 avec beaucoup plus de trades → garder ;
  si PF < 1.0 → remonter `saMinCount` à 3 ou `deScoreMin` à 75.

## ▶️ Prochaines étapes possibles (non commencées)

- Recevoir et analyser le nouveau CSV de backtest (réglages desserrés).
- Si fréquence toujours insuffisante : tester **M5** au lieu de M15 (plus de barres
  = plus d'occasions structurelles, indépendamment du desserrage des filtres).
- Nettoyage code mort documenté mais non appliqué par précaution (chaîne
  Stochastique liée à un input UI, `request.security` redondants) — voir
  `ABLATION.md` section P1.
- Reconnexion possible du journal de trading (`journal-app.html`) aux résultats
  de backtest pour suivi manuel continu.

## ⚠️ Règles à ne jamais oublier

1. **Une modification = un commit = un toggle indépendant.** Ne jamais empiler
   plusieurs changements non mesurés.
2. **Toujours régénérer `STRATEGY.pine` depuis `working.pine`** après une
   modification, et vérifier que le diff du corps reste `2c2` (ligne de
   déclaration uniquement) — preuve que la logique de trading n'a pas dévié.
3. **Aucune exécution Pine réelle côté assistant** : toute vérification est une
   revue statique (fonctions au niveau global, pas de virgules multiples,
   ordre de déclaration, types). La compilation réelle se fait dans TradingView.
4. **Ne jamais garantir un nombre de trades fixe** — un réglage change la
   probabilité, jamais une fréquence certaine.
5. Avant toute conclusion statistique, exiger un échantillon ~30 trades minimum
   (et se rappeler que TradingView compte les sorties partielles, pas les
   signaux réels).

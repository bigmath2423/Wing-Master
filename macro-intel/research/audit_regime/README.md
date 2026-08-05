# Audit de régime — août 2026

Recherche systématique d'une amélioration du système v11, sur les axes qui
n'avaient jamais été mesurés : contexte d'entrée (session, heure, jour,
volatilité, régime de tendance) et sorties (TP fixe, partiels, break-even,
stop, trailing).

## Ordre d'exécution

| Script | Rôle |
|---|---|
| `ctx_build.py` | Reconstruit le contexte M15 complet à l'instant exact des 589 trades exportés. Alignement horaire retrouvé empiriquement (DST européenne), erreur de prix médiane 0,085 $. |
| `ctx_desc.py` | Étape 2 — profil gagnants vs perdants, par session, jour, régime. |
| `ctx_test.py` | Étape 5 — 12 filtres de contexte pré-enregistrés + correction Benjamini-Hochberg. |
| `v11sim.py` | Reproduction de la logique d'entrée v11 en Python (615 trades contre 589 en Pine sur la même fenêtre, soit 4 % d'écart). Sert de second moteur, indépendant du Pine. |
| `exits.py` | Étape 4 — 13 politiques de sortie en face-à-face, mêmes signaux. |
| `grid.py` | Gradients des paramètres de sortie + walk-forward + reproduction du filtre ADX sur le moteur Python. |
| `robust.py` | Sensibilité du filtre ADX à ses réglages, version à seuil fixe, contrôle des confusions. |
| `f09.py` / `final.py` / `final_pct.py` | Batterie de validation complète, versions percentile et seuil fixe. |

## Ce qui est ressorti

**Un seul résultat sur 25 hypothèses testées : le régime de tendance à l'entrée.**

Un BOS qui sort d'un marché calme se paie ; un BOS qui arrive dans une tendance
déjà établie ne se paie pas. Mesuré sur les deux moteurs :

| | avant | après (ADX sous sa médiane glissante) |
|---|---|---|
| Trades | 615 | 364 (59 %) |
| Win rate | 45,4 % | 50,8 % |
| Profit Factor | 1,329 | 1,654 |
| Espérance | +0,185 R | +0,332 R |
| Drawdown | −17,4 R | −13,1 R |
| t-stat | +3,28 | +4,45 |

Réponse en dose monotone sur 5 quintiles, insensible aux réglages (longueur
10/14/20, fenêtre 250 à 2000), non corrélé aux modules existants (|r| ≤ 0,17),
présent dans chaque sous-groupe (session, volatilité, sens), 4/4 sous-périodes,
plus fort en validation qu'en apprentissage.

### Ce que les tests de falsification ont donné (`crosstf.py`, `mech.py`, `perm.py`)

**Le test de placebo confirme la significativité.** Décalage circulaire de la
série ADX, 5000 tirages : la distribution nulle est centrée (moyenne −0,001,
écart-type 0,111) et l'effet observé (+0,360 R) en est à 3,2 écarts-types,
p = 0,0018. Le résultat n'est donc pas un artefact d'autocorrélation — le test
de Student ne le surestimait pas.

**Mais le mécanisme proposé est RÉFUTÉ.** L'explication avancée était : « un BOS
dans une tendance déjà établie est une continuation tardive ». Trois mesures de
l'avancement du mouvement construites sans aucun ADX (barres depuis le dernier
changement de tendance, amplitude déjà parcourue, étendue des 24 h) confirment
bien que l'ADX haut correspond à un mouvement plus avancé (p = 0,011) — mais
**aucune des trois ne prédit le résultat** (écarts −0,119 / −0,040 / +0,054 R,
tous non significatifs). Et l'effet ADX survit intact dans chaque sous-groupe
d'avancement. L'ADX capte donc quelque chose de réel, mais pas ce qui avait été
annoncé. Le mécanisme reste inconnu.

**La réplication croisée n'apporte rien.** M5 : −0,042 R (p = 0,75), mais la
stratégie de base n'y a aucun edge. M30 : +0,181 R (p = 0,22). H1 : +0,061 R
(p = 0,76). Ces deux dernières sont trop peu puissantes pour trancher (effet
minimum détectable 0,46 et 0,59 R). Ni confirmation ni réfutation.

### VERDICT FINAL — RÉFUTÉ, RETIRÉ DU CODE (`newrun.py`, `oos_final.py`)

Un export TradingView remontant à **avril 2020** a fourni 200 trades jamais
utilisés pour construire le filtre. Le percentile ADX y était déjà inscrit dans
le commentaire de chaque entrée, ce qui permet une partition directe, sans
aucune reconstruction.

**L'effet s'inverse.**

| Période | Ce que le filtre garde | Ce qu'il jette | Écart |
|---|---|---|---|
| **2020-04 → 2022-04 (inédit)** | PF 0,874 · **−0,010 R** | PF 1,415 · **+0,271 R** | **−0,281 R** |
| 2022-04 → 2026-07 (déjà utilisé) | PF 1,468 · +0,257 R | PF 1,002 · +0,009 R | +0,248 R |
| **Ensemble 2020-2026** | PF 1,331 · +0,188 R | PF 1,070 · +0,074 R | **+0,114 R, p = 0,33** |

Le gradient par quintile s'inverse lui aussi, et de façon monotone : hors
échantillon, Q1 (ADX le plus bas) rend **−0,443 R** et Q5 **+0,341 R** — l'exact
opposé du gradient qui avait servi d'argument.

Par année : −0,497 · −0,065 · +0,005 · −0,003 · +0,475 · +0,196 · +0,324. L'effet
n'existait que sur 2024-2026, c'est-à-dire sur la moitié récente de la fenêtre
où il a été cherché. Sur l'ensemble, l'IC95 couvre zéro.

**Le filtre a été retiré du Pine.** Le percentile ADX reste inscrit dans le
commentaire des entrées : utile à mesurer, inutile à filtrer.

### La leçon

Ce filtre avait passé : gradient monotone sur 5 quintiles, insensibilité aux
réglages (12 combinaisons), absence de corrélation aux modules existants,
survie dans chaque sous-groupe, 4/4 sous-périodes, effet plus fort en
validation qu'en apprentissage, et un placebo par décalage circulaire à
p = 0,0018. Tout cela n'a pas suffi. Seules des données réellement inédites
ont tranché.

## Ce qui a été rejeté

- Sessions, heures, jour de la semaine, régime de volatilité, distance au POC,
  premium/discount : aucun ne survit à la correction Benjamini-Hochberg.
- TP fixes : le win rate monte (45 → 55 %) mais le Profit Factor tombe
  (1,33 → 1,15) et l'espérance est divisée par deux. Confirme la mesure des
  sorties partielles.
- Break-even : strictement inerte, le trailing armé à 1,5 R passe le point mort
  avant que le break-even n'ait un effet.
- Stop : gradient NON monotone (2,25 et 3,0 meilleurs que 2,5, 2,75 moins bon) —
  signature du bruit paramétrique. 2,5 ATR conservé.
- Trailing plus serré : gradient monotone, mais le simulateur suppose que le
  plus haut d'une bougie précède son repli, ce qui avantage mécaniquement les
  trailings serrés. Artefact non exploitable. 0,3 R conservé.

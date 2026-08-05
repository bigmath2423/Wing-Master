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

**Ce qui manque, et qui interdit de l'activer :** trouvé en testant 12
hypothèses sur des données déjà utilisées, jamais confronté à une période
inédite, et sans mécanisme compris. Le filtre est implémenté dans le Pine mais
**désactivé par défaut** — décoché, le terme est court-circuité et le backtest
de référence est identique bit à bit.

Le percentile ADX est en revanche inscrit dans le commentaire de chaque entrée
(suffixe `A`). Le test en avant des six prochains mois produit donc, sans rien
activer et sans rien risquer, un échantillon hors données pour trancher.

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

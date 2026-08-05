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

**Ce qui manque, et qui interdit de l'activer :** il a été trouvé en testant 12
hypothèses sur des données déjà utilisées, et n'a jamais rencontré une période
inédite. Le filtre est donc implémenté dans le Pine mais **désactivé par
défaut** — décoché, le terme est court-circuité et le backtest de référence est
identique bit à bit.

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

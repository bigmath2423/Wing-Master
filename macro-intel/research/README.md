# Moteur de recherche quantitative — XAUUSD

Objectif : établir **par la preuve statistique** quels concepts créent un
avantage, et supprimer les autres. Ce dossier ne contient aucune stratégie : il
contient l'instrument de mesure.

## Pourquoi ce moteur, et pas une série de backtests TradingView

Une ablation sur stratégie donne **un chiffre par module**, mesuré sur ~2 000
trades, et confondu avec toutes les interactions entre modules. C'est un
instrument peu puissant : avec 2 000 trades, un module doit apporter un effet
énorme pour sortir du bruit.

Ce moteur mesure d'abord chaque concept **comme une feature évaluée à chaque
bougie** : plusieurs centaines de milliers d'observations au lieu de 2 000, et
une taille d'effet avec son intervalle de confiance. On prouve (ou on réfute)
l'existence de l'edge **avant** de construire une machine à trader dessus.
L'ablation reste disponible (Phase 2) pour vérifier que ce qui a été retenu tient
aussi au niveau du système complet.

## Ce qui est traité, et que 90 % des backtests ignorent

| Piège | Conséquence si ignoré | Traitement ici |
|---|---|---|
| Rendements futurs qui se chevauchent | t-stat gonflé d'un facteur ~√horizon : du bruit passe pour un edge | bootstrap par blocs + t de Newey-West |
| Tests multiples | 30 features testées à 5 % ⇒ ~1,5 faux positif garanti | correction Benjamini-Hochberg (FDR) |
| Sélection in-sample | tout paraît fonctionner sur les données ayant servi à choisir | apprentissage / validation séparés, écart mesuré |
| Taux de base extrêmes | une feature vraie 99,9 % du temps produit un effet fantôme | groupes ≥ 2 % et ≥ 300 points chacun |
| Division par un ATR quasi nul | quelques points aberrants dominent la moyenne | winsorisation à ±10 ATR |
| Coûts d'exécution | l'edge mesuré est souvent inférieur au spread | coût prélevé à l'entrée **et** à chaque sortie partielle |
| Bougie ambiguë (SL et TP touchés) | résultat optimiste | le **stop** l'emporte toujours |

## Le garde-fou : `selftest.py`

Avant toute utilisation sur données réelles, le moteur est passé sur une
**marche aléatoire**, où aucun edge n'existe par construction. Il doit n'y
trouver rien.

```
python3 selftest.py
```

Résultat de calibration actuel (120 000 bougies synthétiques, 27 modules) :

```
t-stat moyen          : -0.01   (attendu ~0)
Part des |t| > 1.96   : 3.7 %   (attendu ~5 %)
Modules retenus (FDR) : 1 / 27  (= le taux de fausses découvertes accepté)
Backtest sur bruit    : espérance +0.067 R sans coût (t = +1.17, indiscernable de zéro)
                        espérance -0.170 R avec coût 0.30  ⇒ le système ne perd QUE les frais
```

Ce test a déjà servi : il a attrapé un générateur de faux positifs
(`atr_ok`, effet +0,77 ATR avec t = +19,7 **sur du bruit pur**) causé par un
taux de base de 99,9 % combiné à une division par un ATR minuscule. Sans ce
test, ce module aurait été déclaré « Excellent » sur données réelles.

## Utilisation

```
python3 run.py --data XAUUSD_M5.csv --horizon 20 --cost 0.30 --sl-atr 1.5 --out out/
```

Produit `out/phase1_modules.csv` (classement Excellent / Utile / Neutre / À
supprimer, rendu séparément en apprentissage et en validation),
`out/phase2_ablation.csv` et `out/rapport.md`.

## Données attendues

N'importe quel CSV de bougies ; le format est détecté automatiquement
(TradingView, MetaTrader 5, ou générique `time,open,high,low,close,volume`).

**Le plus simple : MetaTrader 5** — *Affichage → Symboles → Barres → XAUUSD →
Exporter*. Gratuit, historique complet, une seule manipulation.
Alternative : TradingView, *clic droit sur le graphique → Exporter les données
du graphique* (limité au nombre de bougies chargées selon l'abonnement).

Volume de données recommandé : **≥ 200 000 bougies**, soit environ 3 ans en M5
ou 6 ans en M15. En dessous de ~50 000 bougies, la validation out-of-sample
n'a plus assez de points pour trancher quoi que ce soit.

## Note sur l'objectif Win Rate 70-80 % avec Profit Factor > 2

Ces deux cibles sont compatibles, mais elles imposent mécaniquement le profil de
gains : un WR de 75 % avec PF = 2 implique un gain moyen **inférieur** à la perte
moyenne (ratio ≈ 0,67). Autrement dit, ce sont des cibles rapprochées et des
stops larges — le profil le plus **sensible aux coûts d'exécution** qui soit,
puisque le spread se compare à un objectif petit. Le premier backtest montrait
déjà un coût de 6 % du risque par trade en M3. Sur ce profil de gains, viser une
unité de temps plus grande n'est pas une option de confort : c'est une condition
d'existence.

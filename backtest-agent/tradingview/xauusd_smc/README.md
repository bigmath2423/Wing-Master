# XAUUSD SMC — versions de l'indicateur

| Fichier | Statut |
|---------|--------|
| `XAUUSD_SMC_V48_reference.pine` | **Référence figée. Ne jamais modifier.** Toute évolution se fait dans une nouvelle version. |
| `XAUUSD_SMC_V49_delta.pine` | V48 + Delta Volume Profile, en affichage seul. |
| `XAUUSD_SMC_V49_backtest.pine` | V49 transformé en stratégie testable (wrapper P0). |

## Backtester V49 (wrapper P0)

`XAUUSD_SMC_V49_backtest.pine` est une **copie exacte de V49**. Seuls deux
éléments diffèrent : `indicator()` devient `strategy()`, et le bloc
`08 • BACKTEST` est ajouté en fin de fichier. Ce bloc exécute les ordres
BUY/SELL LIMIT que V49 calcule déjà (entrée, SL, TP1, TP2), sans toucher à leur
logique.

### Réglages (groupe « 08 • BACKTEST »)

| Réglage | Effet |
|---------|-------|
| Gestion de l'ordre LIMIT | **V48 fidèle** (par défaut) : l'ordre suit la zone à chaque bougie et est annulé dès que le tableau ORDRES LIMIT n'affiche plus rien. **Ordre gelé (H1)** : l'ordre garde ses niveaux jusqu'au remplissage, à l'expiration ou à une clôture au-delà du SL. |
| Expiration de l'ordre gelé | Nombre de bougies avant annulation, en mode gelé uniquement. |
| Sortie | TP2 (par défaut, c'est lui qui sert au calcul du RR dans V48), TP1, ou 50 % / 50 %. |
| Début / fin du backtest | Pour découper une période d'apprentissage et une période de test. |

Une fois l'ordre rempli, le SL et le TP restent ceux de l'ordre au moment du
remplissage. Une seule position est ouverte à la fois.

### Ce qui part dans l'export

Le commentaire de chaque entrée, qui apparaît dans la colonne **Signal** de
l'export « List of Trades », contient le contexte du trade au moment de l'ordre :

```
SMC setup=OB sl=4175.2 tp=4192.8 tp1=4185.1 rr_plan=2.1 tp_synth=0 score_side=4 score_opp=2
aplus=1 zone=1 sweep=1 struct=1 trend=1 vwap=0 pd=1 vol=1 htf=0 choch_age=12 zone_age=34
zone_atr=0.85 dist_atr=1.2 atr=4.12
```

| Clé | Signification | Hypothèse testée |
|-----|---------------|------------------|
| `setup` | FVG, OB ou SR | Priorité FVG > OB > SR |
| `sl`, `tp`, `tp1` | Niveaux de l'ordre (permettent de calculer le R) | — |
| `rr_plan`, `tp_synth` | RR prévu ; 1 si le TP est le 1,8R synthétique et non un pivot | H9 |
| `score_side`, `score_opp`, `aplus`, `zone` | Score de confluence et état A+ au moment de l'ordre | H6, H13 |
| `sweep`, `struct`, `trend`, `vwap`, `pd`, `vol` | Les 6 critères du score, dans le sens du trade | H6, H7 |
| `htf` | 1 si la zone chevauche une zone D1/H4/H1 encore valide | H10 |
| `choch_age`, `zone_age` | Bougies depuis le CHoCH et depuis la naissance de la zone | H2, H4 |
| `zone_atr`, `dist_atr`, `atr` | Largeur de la zone et distance au prix, en ATR | H15 |

`backtest-agent` lit ce format directement : `sl=` et `tp=` deviennent
stop_loss et take_profit, donc le **R de chaque trade est calculé**. Toutes les
autres clés deviennent des conditions analysables.

### Sans abonnement payant : le tableau « STATS (R) »

TradingView réserve l'export de la List of Trades aux abonnements payants. Le
wrapper calcule donc lui-même les statistiques et les affiche en bas à gauche du
graphique (groupe « 09 • STATISTIQUES ») : **une capture d'écran suffit**.

| Colonne | Contenu |
|---------|---------|
| N | Nombre de trades du segment |
| Réussite | % de trades gagnants |
| Esp. R | Gain moyen par trade, en R (la colonne qui compte) |
| PF | Profit factor : somme des gains / somme des pertes, en R |
| Total R | Somme des R du segment |

Les lignes couvrent tous les trades, BUY/SELL, le type de setup, la séance
d'entrée (heures UTC : Asie 0h-7h, Londres 7h-12h, New York 12h-21h) et chaque
critère du contexte à 1 et à 0. Exemple de lecture : si `htf=1` a une Esp. R
nettement supérieure à `htf=0` avec assez de trades, la confluence HTF (H10)
mérite d'être testée comme filtre. Une ligne grisée a moins de trades que
« Échantillon minimum » (20 par défaut) : n'en tirez rien.

### Mode d'emploi

1. Ajoutez `XAUUSD_SMC_V49_backtest.pine` au graphique, sur le symbole et le
   timeframe que vous tradez réellement.
2. Ouvrez le Strategy Tester, puis exportez la **List of Trades** en CSV
   (abonnement payant). Sinon, faites une capture du tableau « STATS (R) ».
3. Lancez l'analyse :
   ```bash
   cd backtest-agent
   backtest-agent analyze chemin/vers/export.csv
   backtest-agent rolling chemin/vers/export.csv
   ```
4. Comparez ensuite les modes (V48 fidèle vs ordre gelé, TP2 vs TP1) **un
   réglage à la fois**, sur la même période.

### Limites à garder en tête

- **Historique limité** : TradingView ne charge qu'un nombre limité de bougies
  (environ 5 000 à 20 000 selon l'abonnement). En M5, cela ne fait que quelques
  semaines à quelques mois. Visez au moins 100 trades avant de conclure.
- **Remplissage dans la bougie** : quand le SL et le TP sont tous deux dans la
  même bougie, TradingView suppose un ordre des prix (open → plus proche
  extrême → l'autre). Le résultat de ces trades est incertain.
- **Spread** : seul le `Spread CFD` de V48 est appliqué (sur l'entrée). Aucune
  commission n'est simulée ; on peut en ajouter dans Propriétés → Commission.
- **Temps réel ≠ historique** : les données M15/H1/H4/D1 ne sont lues que sur
  bougie clôturée en historique, mais sur la bougie en cours en temps réel (voir
  l'analyse). Le backtest mesure le comportement historique.
- **Delta** : le profil n'a pas de valeur bougie par bougie, il n'apparaît donc
  pas dans l'export.

## V49 — changements par rapport à V48

Les signaux sont **identiques** à V48 : la structure, les FVG, les OB, le score A+
et les ordres LIMIT ne lisent aucune variable du module Delta.

- Ajout du module `07 • DELTA VOLUME PROFILE`, adapté de
  « Delta Volume Profile [BigBeluga] » (© BigBeluga, licence
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)).
- Nouvelle ligne `DELTA` dans le dashboard (Delta % sur la fenêtre analysée).
- `max_boxes_count` passe de 80 à 500. Le profil crée 3 boxes par niveau. Avec 80,
  Pine aurait supprimé automatiquement les boxes les plus anciennes, dont des OB et
  des FVG que le moteur LIMIT lit encore.

Écarts volontaires avec le script BigBeluga d'origine :

| Original | V49 | Raison |
|----------|-----|--------|
| Variables `atr`, `lookback`, `bins`… | Préfixe `dp*` | `atr` existe déjà dans V48 (ATR 14, et non ATR 200) |
| 2 labels créés **par niveau** | 2 labels au total | Doublons empilés au même endroit |
| `bins` peut valoir 0 | Au moins 1, plafonné (`Nombre max de niveaux`) | Erreur d'exécution si le range est < ATR 200 ; limite de boxes |
| Division par un volume nul | Gardée | Symboles ou périodes sans volume |
| Décalage fixe à +50 barres | Paramétrable | Chevauchement avec les zones projetées de V48 |
| Delta % = (V+ − V−) / V− | Au choix : original (par défaut) ou ÷ total | La formule d'origine est asymétrique |

Limites connues du profil, conservées telles quelles :

- Il est calculé uniquement sur la dernière barre : il n'existe aucune valeur
  historique, donc il est **inutilisable comme filtre de signal** en l'état.
- Chaque bougie verse **tout** son volume dans chaque niveau traversé par sa
  mèche : le volume des grandes bougies est compté plusieurs fois.
- Le sens dépend de la couleur de la bougie, et un doji compte comme vendeur.
- Sur XAUUSD (CFD, spot), le volume est du **volume tick** : le delta est une
  estimation, pas de l'order flow réel.

## Licence

Le module Delta est sous CC BY-NC-SA 4.0. Si V49 est partagé, il doit garder
l'attribution BigBeluga, rester non commercial et être partagé sous la même
licence.

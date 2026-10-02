# XAUUSD SMC — versions de l'indicateur

| Fichier | Statut |
|---------|--------|
| `XAUUSD_SMC_V48_reference.pine` | **Référence figée. Ne jamais modifier.** Toute évolution se fait dans une nouvelle version. |
| `XAUUSD_SMC_V49_delta.pine` | V48 + Delta Volume Profile, en affichage seul. |

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

# Intégration TradingView

## Contrainte fondamentale
Pine Script **ne peut pas** effectuer d'appels HTTP sortants. On ne peut donc
pas récupérer le score macro *à l'intérieur* de l'indicateur en direct.
L'architecture retenue inverse le flux : c'est **votre indicateur qui pousse**
son signal technique vers le backend, et le backend fait la fusion.

```
Votre indicateur (SMC/VWAP/Structure)
        │  alerte JSON (webhook)
        ▼
POST /tradingview/webhook  ──►  Fusion technique + macro
        │
        ├─► Réponse : { verdict: reinforced|warning|standard, final_confidence, message }
        └─► Notification Telegram / Discord
```

## Mise en place (5 minutes)

1. **Ajoutez `signal_bridge.pine`** à votre graphique (il ne modifie pas votre
   indicateur, il coexiste).
2. Dans le code, remplacez `technicalScore`, `longSignal` et `shortSignal` par
   les vraies sorties de votre indicateur (variables ou `plot`/`ta` existants).
3. Renseignez l'input **Secret** = la valeur `API_SHARED_SECRET` de votre `.env`.
4. Créez une **alerte** TradingView :
   - Condition : `Macro-Intel · Signal Bridge` → *alert() function calls only*
   - Webhook URL : `https://VOTRE_SERVEUR/tradingview/webhook`
   - (le corps du message est généré par le script, ne rien coller)
5. C'est tout : à chaque signal, vous recevez le verdict fusionné.

> ⚠️ Le webhook TradingView exige une URL **HTTPS publique**. En local,
> exposez le backend avec un tunnel (ex. `cloudflared`, `ngrok`).

## Affichage optionnel sur le graphique
`macro_overlay.pine` affiche un petit tableau (score / biais / confiance /
risque). Comme Pine ne peut pas lire l'API, ses valeurs se saisissent à la main
depuis `GET /macro/gold/pine` (ou via une automatisation navigateur). Pour du
temps réel sans saisie, préférez le **dashboard web** (`/`) ou les
notifications Telegram.

## Backtest de la stratégie SMC — `xauusd_smc_backtest.pine`

Version **strategy** (Strategy Tester) de l'indicateur *XAUUSD SMC Confluence
Signals*. La logique de signal est reprise **ligne pour ligne** : mêmes modules
1→12, même score /100, mêmes règles éliminatoires, mêmes Entry / SL / TP1 / TP2
/ TP Final. Seule l'**exécution des ordres** est ajoutée (groupe d'inputs
`🔁 BACKTEST`).

| Réglage | Défaut | Effet |
|---|---|---|
| Trader uniquement les signaux A+ | OFF | OFF = une position par flèche BUY/SELL affichée (reproduction exacte de l'indicateur). ON = seulement les signaux qui déclenchent l'alerte. |
| Taille de position | Risque 1 % | Quantité calculée pour que Entrée→SL = 1 % du capital. Sinon quantité fixe. |
| Ordre d'entrée | Limite | Ordre au prix du Precision Engine (bord d'OB / milieu de FVG). « Marché » entre à la clôture de la bougie du signal. |
| TP1 / TP2 | 50 % / 30 % | Sorties partielles ; le reliquat (20 %) part au TP Final. |
| SL au Break Even après TP1 | ON | Reproduit la gestion affichée par l'indicateur. |
| Signal opposé | Ignorer | La position vit sur son SL/TP. Options : fermer, ou inverser. |
| Période / protections | OFF | Fenêtre in-sample/out-of-sample, perte max/jour, nb max de trades/jour. |

**À savoir avant d'interpréter les résultats**

- **Commission et slippage** ne sont pas codés en dur : renseignez-les dans
  l'onglet *Propriétés* du Strategy Tester (spread + slippage réels du broker),
  sinon les résultats sont optimistes.
- En mode **Limite**, TradingView n'attache le SL/TP qu'à partir de la bougie
  *suivant* le remplissage (limite du moteur, pas du script) : effet globalement
  légèrement pessimiste. Le mode **Marché** n'a pas cette limitation.
- Sans **Bar Magnifier** (Premium), si SL et TP sont touchés dans la même
  bougie, TradingView retient le pire cas.
- Un SL très serré peut produire une quantité énorme en mode risque % : utilisez
  *Quantité maximum* pour plafonner.
- Ne concluez rien sous ~100 trades : l'échantillon n'est pas significatif.

## Endpoints utiles
| Endpoint | Usage |
|---|---|
| `GET /macro/latest` | Snapshot complet (dashboard) |
| `GET /macro/gold/pine` | Format compact `MACRO_SCORE / BIAS / RISK_LEVEL` |
| `POST /tradingview/webhook` | Réception du signal technique + fusion |
| `POST /tradingview/simulate?symbol=XAUUSD&side=buy&technical_score=88` | Test rapide |

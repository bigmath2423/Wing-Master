"""
backtest.py
===========
Backtest "walk-forward" du bot sur données historiques.

Principe :
1. On charge l'historique de tous les timeframes.
2. On avance bougie par bougie sur le timeframe d'entrée (M5 par défaut).
3. À chaque bougie, on ne montre aux agents QUE le passé (pas de triche) et on
   leur demande une décision, exactement comme en live.
4. Si le signal est BUY/SELL, on simule le trade en avançant dans le futur :
   le SL ou le TP est-il touché en premier ? -> gain/perte en "R" (multiples de
   risque). Une seule position à la fois.
5. On affiche les statistiques : nombre de trades, taux de réussite, R total,
   facteur de profit, etc.

Lancement :
    python backtest.py

Note : en mode simulation (sans MetaTrader5), les bougies sont synthétiques ;
le backtest sert alors à valider la MÉCANIQUE. Sur données MT5 réelles, il donne
une vraie estimation historique.
"""

from __future__ import annotations

import config
from core.mt5_client import MT5Client
from agents import (
    TechnicalAgent, ICTSMCAgent, MacroAgent, QuantAgent,
    SentimentAgent, RiskAgent, DecisionAgent,
)


class BacktestClient:
    """Client léger pour le backtest : renvoie le prix HISTORIQUE de la bougie
    en cours d'analyse (au lieu du dernier prix live)."""

    def __init__(self, real_client: MT5Client, config):
        self._real = real_client
        self.config = config
        self._price = 0.0

    def set_price(self, price: float) -> None:
        self._price = float(price)

    def get_tick(self) -> dict:
        return {"bid": self._price - 0.10, "ask": self._price + 0.10}

    def get_balance(self) -> float:
        return self._real.get_balance()

    def get_symbol_info(self) -> dict:
        return self._real.get_symbol_info()

    def is_demo(self) -> bool:
        return True


def _slice_market(full: dict, entry_tf: str, entry_time) -> dict:
    """Ne garde que les bougies antérieures ou égales à `entry_time`
    (aucune fuite d'information future)."""
    market = {}
    for tf, df in full.items():
        if df is None:
            market[tf] = None
        else:
            market[tf] = df[df["time"] <= entry_time]
    return market


def _simulate_trade(entry_df, start_idx, direction, entry, sl, tp) -> float:
    """Rejoue le futur à partir de start_idx+1. Retourne le résultat en R :
    +RR si TP touché, -1 si SL touché, sinon clôture à la dernière bougie."""
    risk = abs(entry - sl)
    if risk == 0:
        return 0.0
    highs = entry_df["high"].values
    lows = entry_df["low"].values
    closes = entry_df["close"].values
    n = len(entry_df)

    for j in range(start_idx + 1, n):
        hi, lo = highs[j], lows[j]
        if direction == "BUY":
            if lo <= sl:
                return -1.0          # SL touché en premier (hypothèse prudente)
            if hi >= tp:
                return (tp - entry) / risk
        else:  # SELL
            if hi >= sl:
                return -1.0
            if lo <= tp:
                return (entry - tp) / risk

    # Pas de sortie : on solde au dernier prix
    last = closes[-1]
    reward = (last - entry) if direction == "BUY" else (entry - last)
    return reward / risk


def run_backtest() -> None:
    print("=== BACKTEST — MT5 AI Trading Bot (XAUUSD) ===")
    real = MT5Client(config)
    if not real.connect():
        print("[backtest] Connexion impossible.")
        return

    # Historique complet
    full = {tf: real.get_rates(tf, config.BARS) for tf in config.TIMEFRAMES}
    entry_tf = config.ENTRY_TIMEFRAME
    entry_df = full[entry_tf].reset_index(drop=True)

    # Agents
    agents = [
        TechnicalAgent(config), ICTSMCAgent(config), MacroAgent(config),
        QuantAgent(config), SentimentAgent(config),
    ]
    risk = RiskAgent(config)
    bt_client = BacktestClient(real, config)
    decision = DecisionAgent(config, risk)

    warmup = config.EMA_SLOW + 5      # assez de bougies pour tous les indicateurs
    results: list[float] = []
    trades = []
    i = warmup

    while i < len(entry_df) - 1:
        row = entry_df.iloc[i]
        entry_time = row["time"]
        bt_client.set_price(row["close"])

        market = _slice_market(full, entry_tf, entry_time)
        # Aligne l'index du timeframe d'entrée sur la tranche vue par les agents
        opinions = [a.analyze(market) for a in agents]
        signal = decision.decide(opinions, market, bt_client)

        if signal.decision in ("BUY", "SELL") and signal.sl and signal.tp:
            r = _simulate_trade(entry_df, i, signal.decision,
                                signal.entry, signal.sl, signal.tp)
            results.append(r)
            trades.append((entry_time, signal.decision, round(r, 2), signal.confidence))
            # Avance après une sortie approximative pour éviter les trades superposés
            i += 3
        else:
            i += 1

    _report(results, trades)
    real.shutdown()


def _report(results: list[float], trades: list) -> None:
    line = "=" * 56
    print("\n" + line)
    print("  RÉSULTATS DU BACKTEST")
    print(line)
    if not results:
        print("  Aucun trade généré sur la période.")
        print(line)
        return

    n = len(results)
    wins = [r for r in results if r > 0]
    losses = [r for r in results if r <= 0]
    total_r = sum(results)
    win_rate = len(wins) / n * 100
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else float("inf")

    print(f"  Trades              : {n}")
    print(f"  Taux de réussite    : {win_rate:.1f}%  ({len(wins)}W / {len(losses)}L)")
    print(f"  Résultat total      : {total_r:+.2f} R")
    print(f"  Gain moyen / trade  : {total_r / n:+.2f} R")
    print(f"  Facteur de profit   : {profit_factor:.2f}")
    print(line)
    print("  5 derniers trades :")
    for t in trades[-5:]:
        print(f"     {t[0]:%Y-%m-%d %H:%M}  {t[1]:4s}  {t[2]:+.2f} R  (conf {t[3]:.0f}%)")
    print(line + "\n")
    print("  Rappel : résultats en 'R' (multiples du risque). Sur données")
    print("  simulées, ce test valide la mécanique, pas la rentabilité réelle.\n")


if __name__ == "__main__":
    run_backtest()

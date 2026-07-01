"""
main.py
=======
Point d'entrée du bot de trading IA pour MetaTrader 5 (XAUUSD).

Lancement :
    python main.py

Le bot :
1. se connecte à MT5 (ou bascule en simulation si MT5 indisponible) ;
2. récupère les bougies XAUUSD sur H1, M15, M5 ;
3. fait analyser le marché par les agents (technique + ICT/SMC) ;
4. l'agent de décision agrège tout et produit un signal ;
5. affiche BUY / SELL / NO TRADE avec entrée, SL, TP, raison, confiance ;
6. n'exécute AUCUN trade tant que AUTO_TRADE=False (config.py).
"""

from __future__ import annotations

import sys
import time
from datetime import datetime

import config
from core.mt5_client import MT5Client
from agents import (
    TechnicalAgent,
    ICTSMCAgent,
    MacroAgent,
    QuantAgent,
    SentimentAgent,
    RiskAgent,
    DecisionAgent,
    ExecutionAgent,
)
from utils.display import print_signal, print_opinions


def fetch_market(client: MT5Client) -> dict:
    """Récupère les données pour tous les timeframes configurés."""
    market = {}
    for tf in config.TIMEFRAMES:
        try:
            market[tf] = client.get_rates(tf, config.BARS)
        except Exception as exc:  # pragma: no cover
            print(f"[main] Erreur récupération {tf} : {exc}")
            market[tf] = None
    return market


def run_once(client: MT5Client) -> None:
    """Exécute un cycle complet d'analyse et affiche le signal."""
    market = fetch_market(client)

    # Agents d'analyse
    technical = TechnicalAgent(config)
    ict = ICTSMCAgent(config)
    macro = MacroAgent(config)
    quant = QuantAgent(config)
    sentiment = SentimentAgent(config)
    opinions = [
        technical.analyze(market),
        ict.analyze(market),
        macro.analyze(market),
        quant.analyze(market),
        sentiment.analyze(market),
    ]

    # Décision (utilise l'agent de risque pour les niveaux)
    risk = RiskAgent(config)
    decision = DecisionAgent(config, risk)
    signal = decision.decide(opinions, market, client)

    # Affichage
    print_opinions(opinions)
    print_signal(signal, config.SYMBOL)

    # Exécution (désactivée par défaut)
    executor = ExecutionAgent(config, client)
    result = executor.execute(signal)
    print(f"[Exécution] {result['reason']}")


def run_loop(client: MT5Client) -> None:
    """Relance l'analyse en continu toutes les LOOP_INTERVAL_MINUTES minutes."""
    interval = max(1, int(config.LOOP_INTERVAL_MINUTES)) * 60
    print(f"[main] Mode boucle : analyse toutes les "
          f"{config.LOOP_INTERVAL_MINUTES} min. (Ctrl+C pour arrêter)")
    while True:
        run_once(client)
        nxt = datetime.now().timestamp() + interval
        print(f"[main] Prochaine analyse vers {datetime.fromtimestamp(nxt):%H:%M:%S}.\n")
        time.sleep(interval)


def main() -> int:
    print("=== MT5 AI Trading Bot (XAUUSD) ===")
    client = MT5Client(config)
    if not client.connect():
        print("[main] Connexion MT5 impossible. Arrêt.")
        return 1

    try:
        if config.LOOP_ENABLED:
            run_loop(client)
        else:
            run_once(client)
    except KeyboardInterrupt:
        print("\n[main] Arrêt demandé par l'utilisateur.")
    finally:
        client.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())

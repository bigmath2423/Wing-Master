"""
core/mt5_client.py
==================
Couche d'accès à MetaTrader 5.

Responsabilités :
- se connecter au terminal MT5
- récupérer les données OHLC (bougies) pour XAUUSD sur plusieurs timeframes
- exposer les infos compte / symbole nécessaires au calcul du risque
- envoyer un ordre (utilisé uniquement par l'agent d'exécution, en démo)

Si le module `MetaTrader5` n'est pas installé (ex: hors Windows), le client
bascule en MODE SIMULATION : il génère des bougies synthétiques afin que tout
le reste du bot (agents, décision, affichage) puisse être testé sans MT5.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

try:
    import MetaTrader5 as mt5  # type: ignore
    MT5_AVAILABLE = True
except Exception:  # pragma: no cover - dépend de l'environnement
    mt5 = None
    MT5_AVAILABLE = False


# Correspondance string -> constante MT5 (et minutes pour le mode simulation)
_TIMEFRAME_MINUTES = {
    "M1": 1, "M5": 5, "M15": 15, "M30": 30,
    "H1": 60, "H4": 240, "D1": 1440,
}


def _mt5_timeframe(tf: str):
    """Convertit 'M5' -> mt5.TIMEFRAME_M5."""
    if not MT5_AVAILABLE:
        return _TIMEFRAME_MINUTES.get(tf, 5)
    return getattr(mt5, f"TIMEFRAME_{tf}")


class MT5Client:
    """Encapsule la connexion et les requêtes vers MetaTrader 5."""

    def __init__(self, config):
        self.config = config
        self.connected = False
        self.simulation = not MT5_AVAILABLE

    # ------------------------------------------------------------------ #
    # Connexion
    # ------------------------------------------------------------------ #
    def connect(self) -> bool:
        """Initialise la connexion au terminal MT5.

        Retourne True si connecté (ou en mode simulation)."""
        if self.simulation:
            print("[MT5Client] Module MetaTrader5 indisponible -> MODE SIMULATION.")
            self.connected = True
            return True

        kwargs = {}
        if self.config.MT5_TERMINAL_PATH:
            kwargs["path"] = self.config.MT5_TERMINAL_PATH
        if self.config.MT5_LOGIN:
            kwargs["login"] = int(self.config.MT5_LOGIN)
        if self.config.MT5_PASSWORD:
            kwargs["password"] = self.config.MT5_PASSWORD
        if self.config.MT5_SERVER:
            kwargs["server"] = self.config.MT5_SERVER

        if not mt5.initialize(**kwargs):
            print(f"[MT5Client] Echec initialize() : {mt5.last_error()}")
            return False

        # S'assure que le symbole est disponible dans le Market Watch
        if not mt5.symbol_select(self.config.SYMBOL, True):
            print(f"[MT5Client] Symbole {self.config.SYMBOL} indisponible.")
            return False

        self.connected = True
        info = mt5.account_info()
        if info:
            print(f"[MT5Client] Connecté. Compte {info.login} "
                  f"({'DÉMO' if info.trade_mode == 0 else 'RÉEL'}), "
                  f"solde {info.balance} {info.currency}.")
        return True

    def shutdown(self) -> None:
        if not self.simulation and MT5_AVAILABLE:
            mt5.shutdown()
        self.connected = False

    # ------------------------------------------------------------------ #
    # Données de marché
    # ------------------------------------------------------------------ #
    def get_rates(self, timeframe: str, bars: int | None = None) -> pd.DataFrame:
        """Récupère `bars` bougies pour le symbole sur `timeframe`.

        Retourne un DataFrame avec colonnes : time, open, high, low, close,
        tick_volume."""
        bars = bars or self.config.BARS

        if self.simulation:
            return self._simulated_rates(timeframe, bars)

        rates = mt5.copy_rates_from_pos(
            self.config.SYMBOL, _mt5_timeframe(timeframe), 0, bars
        )
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"Aucune donnée pour {self.config.SYMBOL} {timeframe} : "
                f"{mt5.last_error()}"
            )
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def get_tick(self) -> dict:
        """Dernier prix bid/ask du symbole."""
        if self.simulation:
            df = self._simulated_rates(self.config.ENTRY_TIMEFRAME, 1)
            price = float(df["close"].iloc[-1])
            return {"bid": price - 0.10, "ask": price + 0.10}

        tick = mt5.symbol_info_tick(self.config.SYMBOL)
        return {"bid": tick.bid, "ask": tick.ask}

    # ------------------------------------------------------------------ #
    # Infos compte / symbole
    # ------------------------------------------------------------------ #
    def get_balance(self) -> float:
        if self.simulation:
            return self.config.ACCOUNT_BALANCE_FALLBACK
        info = mt5.account_info()
        return float(info.balance) if info else self.config.ACCOUNT_BALANCE_FALLBACK

    def is_demo(self) -> bool:
        """True si le compte est un compte démo (ou en simulation)."""
        if self.simulation:
            return True
        info = mt5.account_info()
        # trade_mode : 0 = DEMO, 1 = CONTEST, 2 = REAL
        return bool(info) and info.trade_mode == 0

    def get_symbol_info(self) -> dict:
        """Infos nécessaires au calcul du lot (taille de tick, valeur, etc.)."""
        if self.simulation:
            # Valeurs typiques pour XAUUSD
            return {
                "point": 0.01,
                "trade_tick_size": 0.01,
                "trade_tick_value": 1.0,    # ~1$ par tick pour 1 lot
                "volume_min": self.config.MIN_LOT,
                "volume_max": self.config.MAX_LOT,
                "volume_step": 0.01,
                "digits": 2,
            }
        si = mt5.symbol_info(self.config.SYMBOL)
        return {
            "point": si.point,
            "trade_tick_size": si.trade_tick_size,
            "trade_tick_value": si.trade_tick_value,
            "volume_min": si.volume_min,
            "volume_max": si.volume_max,
            "volume_step": si.volume_step,
            "digits": si.digits,
        }

    # ------------------------------------------------------------------ #
    # Exécution d'ordre (utilisé par l'agent d'exécution)
    # ------------------------------------------------------------------ #
    def send_order(self, direction: str, lot: float, sl: float, tp: float) -> dict:
        """Envoie un ordre marché. direction = 'BUY' ou 'SELL'.

        En mode simulation, ne fait rien de réel : retourne un faux ticket."""
        if self.simulation:
            print("[MT5Client] (Simulation) Ordre non envoyé : pas de terminal MT5.")
            return {"ok": False, "reason": "simulation", "ticket": None}

        tick = mt5.symbol_info_tick(self.config.SYMBOL)
        price = tick.ask if direction == "BUY" else tick.bid
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.SYMBOL,
            "volume": float(lot),
            "type": order_type,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": self.config.DEVIATION,
            "magic": self.config.MAGIC_NUMBER,
            "comment": "mt5_ai_bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        ok = result.retcode == mt5.TRADE_RETCODE_DONE
        return {
            "ok": ok,
            "reason": result.comment,
            "ticket": getattr(result, "order", None),
            "retcode": result.retcode,
        }

    # ------------------------------------------------------------------ #
    # Mode simulation
    # ------------------------------------------------------------------ #
    def _simulated_rates(self, timeframe: str, bars: int) -> pd.DataFrame:
        """Génère des bougies synthétiques réalistes (marche aléatoire)
        autour d'un prix d'or ~2300 pour tester le bot sans MT5."""
        rng = np.random.default_rng(seed=hash(timeframe) % (2**32))
        minutes = _TIMEFRAME_MINUTES.get(timeframe, 5)

        base = 2300.0
        # tendance + bruit
        drift = rng.normal(0, 0.5, bars).cumsum()
        noise = rng.normal(0, 1.2, bars)
        close = base + drift + noise
        open_ = np.concatenate([[close[0]], close[:-1]])
        spread = np.abs(rng.normal(0, 1.0, bars)) + 0.5
        high = np.maximum(open_, close) + spread
        low = np.minimum(open_, close) - spread
        volume = rng.integers(100, 1000, bars)

        end = datetime.utcnow()
        times = [end - timedelta(minutes=minutes * (bars - i)) for i in range(bars)]

        return pd.DataFrame({
            "time": times,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": volume,
        })

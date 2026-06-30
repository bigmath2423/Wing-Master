"""
config.py
=========
Fichier central de configuration du bot.
Modifie ici le symbole, les timeframes, le risque, etc.
Aucune logique métier : uniquement des réglages.
"""

# ---------------------------------------------------------------------------
# CONNEXION MT5
# ---------------------------------------------------------------------------
# Laisse ces champs vides pour utiliser le terminal MT5 déjà ouvert et connecté.
# Sinon renseigne les identifiants de ton compte DÉMO.
MT5_LOGIN = None          # ex: 12345678 (int) ou None
MT5_PASSWORD = None       # ex: "motdepasse" ou None
MT5_SERVER = None         # ex: "MetaQuotes-Demo" ou None
MT5_TERMINAL_PATH = None  # ex: r"C:\\Program Files\\MetaTrader 5\\terminal64.exe" ou None

# ---------------------------------------------------------------------------
# MARCHÉ
# ---------------------------------------------------------------------------
SYMBOL = "XAUUSD"          # Symbole à trader (Or vs Dollar)

# Timeframes analysés. Le bot fait une analyse multi-timeframe.
# H1  -> tendance de fond
# M15 -> structure intermédiaire
# M5  -> timing d'entrée
TIMEFRAMES = ["H1", "M15", "M5"]

# Timeframe principal pour l'entrée / calcul du SL-TP
ENTRY_TIMEFRAME = "M5"

# Nombre de bougies récupérées par timeframe
BARS = 500

# ---------------------------------------------------------------------------
# GESTION DU RISQUE
# ---------------------------------------------------------------------------
RISK_PER_TRADE = 0.01      # Risque max par trade = 1% du capital
ACCOUNT_BALANCE_FALLBACK = 10000.0  # Capital utilisé si MT5 indisponible (mode simulation)

# Ratio Risque/Récompense visé (TP = RR * distance du SL)
RISK_REWARD_RATIO = 2.0

# Bornes du lot (sécurité)
MIN_LOT = 0.01
MAX_LOT = 1.00

# Marge ajoutée au stop loss (en multiples d'ATR) pour éviter les mèches
SL_ATR_MULTIPLIER = 1.5
ATR_PERIOD = 14

# ---------------------------------------------------------------------------
# INDICATEURS TECHNIQUES
# ---------------------------------------------------------------------------
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Fenêtre (en bougies) pour détecter les supports/résistances et la structure
SWING_LOOKBACK = 20

# ---------------------------------------------------------------------------
# DÉCISION
# ---------------------------------------------------------------------------
# Confiance minimale (0-100) requise pour émettre un signal BUY/SELL.
MIN_CONFIDENCE = 55

# ---------------------------------------------------------------------------
# EXÉCUTION
# ---------------------------------------------------------------------------
# IMPORTANT : par défaut le bot N'EXÉCUTE PAS de trade.
# Il affiche seulement un signal. Mets True quand tu es prêt (compte DÉMO).
AUTO_TRADE = False

# Sécurité : refuse d'envoyer un ordre si le compte n'est pas un compte démo.
DEMO_ONLY = True

# Numéro magique pour identifier les ordres du bot
MAGIC_NUMBER = 555001
DEVIATION = 20             # slippage autorisé (points)

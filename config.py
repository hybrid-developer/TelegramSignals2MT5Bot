# config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

TELEGRAM_CHAT_IDS = [
    -1003771192148
]

# Broker symbol mapping
SYMBOL_MAP = {
    "GOLD": "XAUUSD",
    "XAUUSD": "XAUUSD",
    "SPX500": "US500",
    "US500": "US500",
    "NAS100": "USTEC",
    "USTEC": "USTEC",
    "GER30": "DE40",
    "DE40": "DE40",
    "EURUSD": "EURUSD",
    "GBPJPY": "GBPJPY",
}

# Risk and trading limits
RISK_PER_TRADE = 1.0
RISK_PERCENT = 1.0
DEFAULT_LOT_SIZE = 0.01
USE_FIXED_LOT_SIZE = True
MAX_DAILY_LOSS = 100.0          # Effectively disabled (very high threshold)
MAX_TRADES_PER_DAY = 9999       # Effectively disabled
MAX_OPEN_TRADES = 150

CORRELATED = [["US500", "USTEC"]]
NEWS_FILTER_MINUTES = 30

# AI filter — DISABLED
AI_FILTER_ENABLED = False
AI_MIN_SCORE = 0.0
AI_SCORE_DIVISOR = 2.0
AI_BONUS_MULTIPLE_TPS = 0.10
AI_REQUIRE_SL = False
AI_REQUIRE_TP = False

# Spread filter — DISABLED
ENABLE_SPREAD_FILTER = False
MAX_SPREAD_FOREX = 9999
MAX_SPREAD_GOLD = 9999
MAX_SPREAD_DEFAULT = 9999

# Multi-TP settings — each TP gets its own trade at same lot size
MULTI_TP_ENABLED = True
MULTI_TP_FIXED_LOT_EACH = True
MULTI_TP_LOT_SIZE = 0.01
MAX_TP_ORDERS = 10              # Support up to 10 TPs

# Execution settings
DEVIATION = 20
MAGIC_NUMBER = 20260318

# News filter — DISABLED
NEWS_FILTER_ENABLED = False

# Session/time filter — DISABLED
SESSION_FILTER_ENABLED = False

# Correlation filter — DISABLED
CORRELATION_FILTER_ENABLED = False
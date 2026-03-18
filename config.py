# config.py

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# List of allowed chat IDs (groups/channels)
TELEGRAM_CHAT_IDS = [
    123456789,
    987654321,
    1122334455,
]

# Risk & trading limits
RISK_PER_TRADE = 1.0
MAX_DAILY_LOSS = 5.0
MAX_TRADES_PER_DAY = 5
CORRELATED = [["US500", "USTEC"]]
NEWS_FILTER_MINUTES = 30

# Symbol mapping for IC Markets
SYMBOL_MAP = {
    "GOLD": "XAUUSD",
    "SPX500": "US500",
    "NAS100": "USTEC",
    "GER30": "DE40",
    "EURUSD": "EURUSD",
    "GBPJPY": "GBPJPY",
}
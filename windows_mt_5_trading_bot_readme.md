# Windows MT5 Telegram Auto-Trading Bot

This folder contains a full **Windows-ready MT5 Telegram bot**, fully headless, multi-channel, and AI-filtered.

---

## Folder Structure

```
trading_bot_windows/
├── telegram_async_bot.py    # Async Telegram bot
├── executor.py              # MT5 execution with TP scaling
├── parser.py                # Signal parser
├── ai_filter.py             # A+ setup scoring
├── logger.py                # Logging trades & win rate
├── config.py                # Bot configuration
├── start_bot.bat            # Windows startup batch file
├── dashboard.py             # FastAPI live PnL dashboard
├── requirements.txt         # Python dependencies
└── README.md                # This guide
```

---

## Prerequisites

- Windows 10 or 11
- IC Markets MT5 Terminal installed
- MT5 account logged in with **Save Password** and **Allow Automated Trading** enabled
- Python 3.10+
- Python dependencies installed (`pip install -r requirements.txt`)

---

## Configuration (`config.py`)

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Telegram channel/group IDs to read signals from
TELEGRAM_CHAT_IDS = [123456789, 987654321]

RISK_PER_TRADE = 1.0      # % risk per trade
MAX_DAILY_LOSS = 5.0      # Kill switch
MAX_TRADES_PER_DAY = 5     # Trade limiter
CORRELATED = [["US500", "USTEC"]]  # Correlated symbols
NEWS_FILTER_MINUTES = 30   # Ignore high-impact news within 30 min

# MT5 Path
MT5_PATH = r"C:\MT5_ICMarkets\terminal64.exe"
```

---

## Installation

1. Install Python 3.10+
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Ensure MT5 is installed and logged in, with "Allow Automated Trading" checked.

---

## Running the Bot

1. **Manual Run:**

```powershell
python telegram_async_bot.py
```

2. **Headless Startup:**

- `start_bot.bat` launches the bot automatically:

```bat
@echo off
cd C:\path\to\trading_bot_windows
python telegram_async_bot.py
pause
```

- Place `start_bot.bat` in the Windows Startup folder (`Win+R` → `shell:startup`).

---

## Dashboard

Track live PnL and trades:

```powershell
uvicorn dashboard:app --reload --host 0.0.0.0 --port 8000
```

Access in browser at `http://<VPS_IP>:8000`.

---

## Features

- Async multi-channel Telegram reading
- AI trade filter (A+ setups)
- Partial TP scaling (TP1/TP2/TP3)
- Risk management & kill switch
- Max trades per day limiter
- News filter (ForexFactory high-impact events)
- Correlation filter (avoid stacking SPX + NAS)
- Logging & dashboard for PnL and win rate
- Fully headless operation on Windows

---

## Notes

- MT5 credentials remain **inside MT5**, never in Python code
- Ensure MT5 terminal is running or auto-started on boot
- Python bot communicates via `MetaTrader5` API
- Recommended to run on a VPS or always-on PC for 24/7 operation


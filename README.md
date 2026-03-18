# 📈 MT5 Telegram Auto-Trading Bot (Async, Multi-Channel)

## Overview

This bot allows you to automatically execute trading signals from multiple Telegram channels on your MT5 account. Features include:

- Async Telegram listener for multiple channels/groups
- AI trade filter (executes only A+ setups)
- Partial TP scaling (TP1/TP2/TP3)
- Risk management & kill switch
- Trade limiter (max trades/day)
- News filter (high-impact events from ForexFactory)
- Correlation filter (avoid SPX + NAS stacking)
- Logging system with win rate tracking
- Web dashboard for live PnL

---

## Project Structure

trading_bot/
├── main.py                  # Optional CLI version
├── telegram_async_bot.py    # Async Telegram bot
├── dashboard.py             # FastAPI dashboard
├── parser.py                # Signal parser
├── executor.py              # MT5 execution with TP scaling
├── risk.py                  # Lot sizing & kill switch
├── filters.py               # Spread/session/trade/correlation filters
├── news.py                  # ForexFactory news filter
├── manager.py               # Position management (partial TP / BE)
├── ai_filter.py             # A+ setup scoring
├── logger.py                # Logging trades & calculating win rate
├── config.py                # Dynamic configuration
├── requirements.txt         # Python dependencies
└── README.md                # This guide

---

## Prerequisites

- VPS recommended: Ubuntu 22.04+, 2 cores, 4GB RAM
- Python 3.10+
- IC Markets MT5 Terminal installed
- MT5 account with "Allow Automated Trading" enabled

---

## Installation

1. Clone the project:

```bash
git clone <repo_url>
cd trading_bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Edit `config.py`:

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# List all allowed chat IDs (channels/groups)
TELEGRAM_CHAT_IDS = [
    123456789,
    987654321,
    1122334455,
]

RISK_PER_TRADE = 1.0      # % risk per trade
MAX_DAILY_LOSS = 5.0      # Kill switch
MAX_TRADES_PER_DAY = 5     # Trade limiter
CORRELATED = [["US500", "USTEC"]]  # Correlated symbols
NEWS_FILTER_MINUTES = 30   # Ignore high-impact news within 30 min
```

---

## Running the Bot

### Async Telegram Bot (Recommended)

```bash
python3 telegram_async_bot.py
```

- Listens to all channels in `TELEGRAM_CHAT_IDS`
- Executes signals automatically with AI filter & TP scaling
- Replies to Telegram messages with execution status

### Optional CLI Bot

```bash
python3 main.py
```
- Manual entry of signals via CLI

---

## Dashboard

Track trades, PnL, and win rate:

```bash
uvicorn dashboard:app --reload --host 0.0.0.0 --port 8000
```
- Open `http://<VPS_IP>:8000` in your browser
- Shows total trades, total PnL, win rate, and recent trades

---

## Features

1. AI Filter – Only executes high-quality (A+) setups
2. Partial TP Scaling – Supports 1–4 TPs with proportional lot sizes
3. Kill Switch – Stops trading if max daily loss is reached
4. Trade Limiter – Max trades per day enforced
5. News Filter – Avoids trades around high-impact news
6. Correlation Filter – Prevents stacking correlated trades (e.g., SPX + NAS)
7. Multi-Channel Telegram Support – Receive signals from multiple groups/channels
8. Logging & Dashboard – Track PnL, win rate, and history

---

## VPS Deployment

Use systemd for 24/7 uptime:

```bash
sudo nano /etc/systemd/system/tradingbot.service
```

Add:

```ini
[Unit]
Description=MT5 Telegram Trading Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/trading_bot
ExecStart=/usr/bin/python3 /home/ubuntu/trading_bot/telegram_async_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
sudo systemctl status tradingbot
```

---

## Logs & Win Rate

- Trades are logged in `trades.json`
- `logger.py` tracks daily trades, PnL, and calculates win rate
- Dashboard visualizes the latest 10 trades

---

## Notes

- Ensure MT5 terminal is running and logged in
- Add all signal source channels to `TELEGRAM_CHAT_IDS`
- AI filter scoring ensures only high RR setups are executed
- Partial TP scaling closes positions incrementally to secure profit
- Keep VPS running 24/7 for uninterrupted signal execution

---

This README ensures full guidance for setup, deployment, multi-channel Telegram support, and monitoring.


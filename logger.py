# logger.py
import json
import os
from datetime import datetime, date

FILE = "trades.json"


def _load_data():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _apply_defaults(trade):
    trade.setdefault("timestamp", datetime.utcnow().isoformat())
    trade.setdefault("date", str(date.today()))
    trade.setdefault("symbol", "UNKNOWN")
    trade.setdefault("category", "")
    trade.setdefault("side", "")
    trade.setdefault("entry", None)
    trade.setdefault("sl", None)
    trade.setdefault("tp", None)
    trade.setdefault("lot", None)
    trade.setdefault("pnl", 0)
    trade.setdefault("result", "open")
    trade.setdefault("source_chat", None)
    trade.setdefault("raw_signal", "")
    trade.setdefault("order_id", None)
    trade.setdefault("status", "active")
    trade.setdefault("closed_at", None)
    return trade


def classify_symbol(symbol):
    if not symbol:
        return "Other"

    s = symbol.upper()

    forex_pairs = {
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
        "EURGBP", "EURJPY", "GBPJPY", "GBPAUD", "EURAUD", "AUDJPY", "CADJPY",
        "GBPCHF", "EURCHF", "AUDCAD", "NZDJPY"
    }

    indices = {
        "US30", "NAS100", "SPX500", "GER40", "UK100", "JP225", "AUS200", "FRA40"
    }

    metals = {"XAUUSD", "XAGUSD"}

    if s in forex_pairs:
        return "Forex"
    if s in indices:
        return "Indices"
    if s in metals:
        return "Metals"
    return "Other"


def log_trade(trade):
    if not isinstance(trade, dict):
        raise ValueError("trade must be a dictionary")

    data = _load_data()
    trade = _apply_defaults(trade)

    if not trade.get("category"):
        trade["category"] = classify_symbol(trade.get("symbol"))

    order_id = trade.get("order_id")

    if order_id is not None:
        for existing in data:
            if existing.get("order_id") == order_id:
                existing.update({k: v for k, v in trade.items() if v is not None})
                if existing.get("result") in ("win", "loss", "breakeven"):
                    existing["status"] = "closed"
                    existing["closed_at"] = datetime.utcnow().isoformat()
                _save_data(data)
                return existing

    data.append(trade)
    _save_data(data)
    return trade


def update_trade(order_id, **updates):
    data = _load_data()

    for trade in data:
        if trade.get("order_id") == order_id:
            for key, value in updates.items():
                if value is not None:
                    trade[key] = value

            if not trade.get("category"):
                trade["category"] = classify_symbol(trade.get("symbol"))

            if trade.get("result") in ("win", "loss", "breakeven"):
                trade["status"] = "closed"
                trade["closed_at"] = datetime.utcnow().isoformat()

            _save_data(data)
            return trade

    return None


def get_trade(order_id):
    data = _load_data()
    for trade in data:
        if trade.get("order_id") == order_id:
            return trade
    return None


def get_all_trades():
    return _load_data()


def get_today_trades():
    data = _load_data()
    today = str(date.today())
    return len([t for t in data if t.get("date") == today])


def calculate_winrate():
    data = _load_data()
    closed = [t for t in data if t.get("result") in ("win", "loss", "breakeven")]
    wins = sum(1 for t in closed if t.get("result") == "win")
    total = len(closed)
    return round((wins / total) * 100, 2) if total else 0

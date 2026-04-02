# dashboard_app/services.py
import json
from datetime import datetime
from logger import FILE


def load_data():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def fmt_date(dt):
    return dt.strftime("%Y-%m-%d") if dt else ""


def fmt_time(dt):
    return dt.strftime("%H:%M:%S") if dt else ""


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def enrich_rows(data):
    for row in data:
        placed_dt = parse_dt(row.get("placed_at") or row.get("timestamp"))
        executed_dt = parse_dt(row.get("executed_at"))
        tp_dt = parse_dt(row.get("tp_reached_at"))
        sl_dt = parse_dt(row.get("sl_reached_at"))

        row["_placed_dt"] = placed_dt
        row["_placed_date"] = fmt_date(placed_dt)
        row["_placed_time"] = fmt_time(placed_dt)
        row["_executed_time"] = fmt_time(executed_dt)
        row["_tp_time"] = fmt_time(tp_dt)
        row["_sl_time"] = fmt_time(sl_dt)
        row["_category"] = row.get("category") or "Other"

    return data


def apply_filters(data, category="", symbol="", event_type="", status="", result="", day=""):
    rows = data

    if category:
        rows = [r for r in rows if r.get("_category") == category]
    if symbol:
        rows = [r for r in rows if str(r.get("symbol", "")) == symbol]
    if event_type:
        rows = [r for r in rows if str(r.get("event_type", "")) == event_type]
    if status:
        rows = [r for r in rows if str(r.get("status", "")) == status]
    if result:
        rows = [r for r in rows if str(r.get("result", "")) == result]
    if day:
        rows = [r for r in rows if r.get("_placed_date") == day]

    return rows


def build_summary(rows):
    total_events = len(rows)
    total_pnl = round(sum(to_float(r.get("pnl", 0)) for r in rows), 2)
    trades_placed = sum(1 for r in rows if r.get("event_type") == "trade_placed")
    trades_failed = sum(1 for r in rows if r.get("event_type") == "trade_failed")
    filter_rejected = sum(1 for r in rows if r.get("event_type") == "filter_rejected")
    execution_rejected = sum(1 for r in rows if r.get("event_type") == "execution_rejected")
    wins = sum(1 for r in rows if str(r.get("result", "")).lower() == "win")
    losses = sum(1 for r in rows if str(r.get("result", "")).lower() == "loss")
    breakeven = sum(1 for r in rows if str(r.get("result", "")).lower() == "breakeven")
    winrate = round((wins / max(1, wins + losses)) * 100, 2)

    return {
        "total_events": total_events,
        "total_pnl": total_pnl,
        "trades_placed": trades_placed,
        "trades_failed": trades_failed,
        "filter_rejected": filter_rejected,
        "execution_rejected": execution_rejected,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "winrate": winrate,
    }


def build_daily_stats(rows):
    grouped = {}
    for r in rows:
        d = r.get("_placed_date") or "Unknown"
        grouped.setdefault(d, {"wins": 0.0, "losses": 0.0})

        pnl = to_float(r.get("pnl", 0))
        result = str(r.get("result", "")).lower()

        if result == "win" or pnl > 0:
            grouped[d]["wins"] += max(pnl, 0)
        elif result == "loss" or pnl < 0:
            grouped[d]["losses"] += min(pnl, 0)

    return dict(sorted(grouped.items(), reverse=True))


def build_category_counts(rows):
    grouped = {}
    for r in rows:
        cat = r.get("_category", "Other")
        grouped[cat] = grouped.get(cat, 0) + 1
    return grouped


def build_symbol_counts(rows):
    grouped = {}
    for r in rows:
        symbol = r.get("symbol") or "Unknown"
        grouped[symbol] = grouped.get(symbol, 0) + 1
    return grouped


def build_filter_options(data):
    return {
        "categories": sorted(set(r.get("_category", "") for r in data if r.get("_category"))),
        "symbols": sorted(set(str(r.get("symbol", "")) for r in data if r.get("symbol"))),
        "event_types": sorted(set(str(r.get("event_type", "")) for r in data if r.get("event_type"))),
        "statuses": sorted(set(str(r.get("status", "")) for r in data if r.get("status"))),
        "results": sorted(set(str(r.get("result", "")) for r in data if r.get("result"))),
        "days": sorted(set(r.get("_placed_date", "") for r in data if r.get("_placed_date"))),
    }

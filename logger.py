# logger.py
import json
import os
from datetime import datetime, date

FILE = "trades.json"


def _utc_now():
    return datetime.utcnow().isoformat()


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


def classify_symbol(symbol):
    s = (symbol or "").upper()

    if s in ("XAUUSD", "GOLD", "XAGUSD"):
        return "Metals"
    if s in ("US30", "NAS100", "SPX500", "GER40", "UK100"):
        return "Indices"
    if len(s) == 6:
        return "Forex"

    return "Other"


def build_log_record(
    event_type,
    status,
    symbol=None,
    action=None,
    order_type=None,
    entry=None,
    sl=None,
    tp=None,
    tp_index=None,
    lot=None,
    order_id=None,
    deal_id=None,
    source_chat=None,
    raw_signal=None,
    reason=None,
    result=None,
    pnl=0.0,
    placed_at=None,
    executed_at=None,
    tp_reached_at=None,
    sl_reached_at=None,
    extra=None,
):
    record = {
        "timestamp": _utc_now(),
        "date": str(date.today()),
        "event_type": event_type,
        "status": status,
        "symbol": symbol,
        "category": classify_symbol(symbol),
        "action": action,
        "order_type": order_type,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "tp_index": tp_index,
        "lot": lot,
        "order_id": order_id,
        "deal_id": deal_id,
        "source_chat": source_chat,
        "raw_signal": raw_signal,
        "reason": reason,
        "result": result,
        "pnl": pnl,
        "placed_at": placed_at,
        "executed_at": executed_at,
        "tp_reached_at": tp_reached_at,
        "sl_reached_at": sl_reached_at,
    }

    if extra and isinstance(extra, dict):
        record.update(extra)

    return record


def log_event(record):
    data = _load_data()
    data.append(record)
    _save_data(data)
    return record


def log_signal_received(signal, source_chat=None, raw_signal=None):
    return log_event(build_log_record(
        event_type="signal_received",
        status="received",
        symbol=signal.get("symbol"),
        action=signal.get("action"),
        order_type=signal.get("order_type"),
        entry=signal.get("entry"),
        sl=signal.get("sl"),
        tp=signal.get("tps")[0] if signal.get("tps") else None,
        source_chat=source_chat,
        raw_signal=raw_signal or signal.get("raw"),
        placed_at=_utc_now(),
    ))


def log_filter_rejected(signal, reason="Rejected by AI filter", source_chat=None, raw_signal=None):
    return log_event(build_log_record(
        event_type="filter_rejected",
        status="rejected",
        symbol=signal.get("symbol"),
        action=signal.get("action"),
        order_type=signal.get("order_type"),
        entry=signal.get("entry"),
        sl=signal.get("sl"),
        tp=signal.get("tps")[0] if signal.get("tps") else None,
        source_chat=source_chat,
        raw_signal=raw_signal or signal.get("raw"),
        reason=reason,
        placed_at=_utc_now(),
    ))


def log_execution_rejected(signal, reason, source_chat=None, raw_signal=None):
    return log_event(build_log_record(
        event_type="execution_rejected",
        status="rejected",
        symbol=signal.get("symbol"),
        action=signal.get("action"),
        order_type=signal.get("order_type"),
        entry=signal.get("entry"),
        sl=signal.get("sl"),
        tp=signal.get("tps")[0] if signal.get("tps") else None,
        source_chat=source_chat,
        raw_signal=raw_signal or signal.get("raw"),
        reason=reason,
        placed_at=_utc_now(),
    ))


def log_trade_placed(signal, tp, tp_index, lot, order_id=None, deal_id=None, source_chat=None, raw_signal=None):
    now = _utc_now()
    return log_event(build_log_record(
        event_type="trade_placed",
        status="placed",
        symbol=signal.get("symbol"),
        action=signal.get("action"),
        order_type=signal.get("order_type"),
        entry=signal.get("entry"),
        sl=signal.get("sl"),
        tp=tp,
        tp_index=tp_index,
        lot=lot,
        order_id=order_id,
        deal_id=deal_id,
        source_chat=source_chat,
        raw_signal=raw_signal or signal.get("raw"),
        result="open",
        placed_at=now,
        executed_at=now,
    ))


def log_trade_failed(signal, tp, tp_index, lot, reason, source_chat=None, raw_signal=None):
    return log_event(build_log_record(
        event_type="trade_failed",
        status="failed",
        symbol=signal.get("symbol"),
        action=signal.get("action"),
        order_type=signal.get("order_type"),
        entry=signal.get("entry"),
        sl=signal.get("sl"),
        tp=tp,
        tp_index=tp_index,
        lot=lot,
        source_chat=source_chat,
        raw_signal=raw_signal or signal.get("raw"),
        reason=reason,
        placed_at=_utc_now(),
    ))


def get_all_trades():
    return _load_data()

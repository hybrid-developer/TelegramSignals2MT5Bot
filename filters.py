# filters.py
import MetaTrader5 as mt5
import config
from logger import get_today_trades
from datetime import datetime


def spread_ok(symbol, max_spread=9999):
    if not getattr(config, "ENABLE_SPREAD_FILTER", False):
        return True
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)
    if not tick or not info:
        return False
    spread = (tick.ask - tick.bid) / info.point
    return spread <= max_spread


def session_ok():
    if not getattr(config, "SESSION_FILTER_ENABLED", False):
        return True
    hour = datetime.utcnow().hour
    return 7 <= hour <= 20


def trade_limit_ok():
    if not getattr(config, "MAX_TRADES_PER_DAY", 9999):
        return True
    return get_today_trades() < getattr(config, "MAX_TRADES_PER_DAY", 9999)


def correlation_ok(symbol, open_positions):
    if not getattr(config, "CORRELATION_FILTER_ENABLED", False):
        return True
    for group in config.CORRELATED:
        if symbol in group:
            for pos in open_positions:
                if pos.symbol in group:
                    return False
    return True
# filters.py
import MetaTrader5 as mt5
from config import MAX_TRADES_PER_DAY, CORRELATED
from logger import get_today_trades
from datetime import datetime

def spread_ok(symbol, max_spread=30):
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)
    if not tick or not info: return False
    spread = (tick.ask-tick.bid)/info.point
    return spread<=max_spread

def session_ok():
    hour=datetime.utcnow().hour
    return 7<=hour<=20

def trade_limit_ok():
    return get_today_trades()<MAX_TRADES_PER_DAY

def correlation_ok(symbol, open_positions):
    for group in CORRELATED:
        if symbol in group:
            for pos in open_positions:
                if pos.symbol in group: return False
    return True
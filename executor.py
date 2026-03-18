# executor.py
import MetaTrader5 as mt5
from risk import calculate_lot
from filters import spread_ok, session_ok, trade_limit_ok, correlation_ok
from news import high_impact_news_soon

def build_tp_scaling(tps):
    n = len(tps)
    if n==1: weights=[1.0]
    elif n==2: weights=[0.6,0.4]
    elif n==3: weights=[0.5,0.3,0.2]
    elif n==4: weights=[0.4,0.3,0.2,0.1]
    else: weights=[1/n]*n
    return [{"price":tp,"close_pct":w} for tp,w in zip(tps,weights)]

def execute(signal, balance):
    symbol = signal["symbol"]

    if not spread_ok(symbol):
        return "❌ Spread too high"
    if not session_ok():
        return "❌ Bad session"
    if not trade_limit_ok():
        return "❌ Trade limit hit"
    if high_impact_news_soon():
        return "❌ News filter active"

    positions = mt5.positions_get()
    if not correlation_ok(symbol, positions):
        return "❌ Correlated symbol open"

    tp_levels = build_tp_scaling(signal["tps"])
    lot_total = calculate_lot(signal["entry"], signal["sl"], balance, 1.0)

    for tp in tp_levels:
        lot = round(lot_total * tp["close_pct"],2)
        request = {
            "action": mt5.TRADE_ACTION_PENDING if signal["order_type"]=="LIMIT" else mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_LIMIT if signal["action"]=="BUY" else mt5.ORDER_TYPE_SELL_LIMIT,
            "price": signal["entry"],
            "sl": signal["sl"],
            "tp": tp["price"],
            "deviation": 20,
            "magic": 123,
            "comment": "bot",
            "type_time": mt5.ORDER_TIME_GTC,
        }
        mt5.order_send(request)

    return "✅ Executed"
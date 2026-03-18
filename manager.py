# manager.py
import MetaTrader5 as mt5

def manage_positions():
    positions=mt5.positions_get()
    for pos in positions:
        entry=pos.price_open
        tick=mt5.symbol_info_tick(pos.symbol)
        current=tick.bid if pos.type==1 else tick.ask
        if abs(current-entry)>50:
            request={
                "action":mt5.TRADE_ACTION_SLTP,
                "position":pos.ticket,
                "sl":entry,
                "tp":pos.tp
            }
            mt5.order_send(request)
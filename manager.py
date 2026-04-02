# manager.py
import MetaTrader5 as mt5
import logging


def manage_positions():
    positions = mt5.positions_get()
    if positions is None:
        logging.warning("manage_positions: positions_get returned None")
        return

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick is None:
            continue

        is_sell = pos.type == mt5.POSITION_TYPE_SELL
        current_price = tick.bid if is_sell else tick.ask
        entry = pos.price_open
        current_sl = pos.sl
        current_tp = pos.tp

        profit_distance = abs(current_price - entry)

        if profit_distance <= 50:
            continue

        if current_sl == entry:
            continue

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": pos.ticket,
            "symbol": pos.symbol,
            "sl": entry,
            "tp": current_tp,
        }

        result = mt5.order_send(request)

        if result is None:
            logging.warning(f"manage_positions: order_send failed for {pos.symbol} ticket={pos.ticket} err={mt5.last_error()}")
            continue

        if result.retcode not in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED):
            logging.warning(
                f"manage_positions: failed to move SL to breakeven for {pos.symbol} "
                f"ticket={pos.ticket} retcode={result.retcode} comment={result.comment}"
            )
        else:
            logging.info(f"Moved SL to breakeven for {pos.symbol} ticket={pos.ticket}")

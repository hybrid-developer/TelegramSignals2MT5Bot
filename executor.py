# executor.py
import MetaTrader5 as mt5
import config


def build_tp_scaling(tps):
    valid = [tp for tp in tps if isinstance(tp, (int, float)) and tp > 0]
    return [{"tp": tp, "portion": 1.0} for tp in valid]


def classify_symbol(symbol):
    s = (symbol or "").upper()
    if s in ("XAUUSD", "GOLD"):
        return "GOLD"
    if len(s) == 6:
        return "FOREX"
    return "OTHER"


def normalize_symbol(symbol):
    s = (symbol or "").upper()
    if s == "GOLD":
        return "XAUUSD"
    return s


def get_max_spread(symbol):
    group = classify_symbol(symbol)
    if group == "GOLD":
        return getattr(config, "MAX_SPREAD_GOLD", 120)
    if group == "FOREX":
        return getattr(config, "MAX_SPREAD_FOREX", 30)
    return getattr(config, "MAX_SPREAD_DEFAULT", 50)


def count_open_positions():
    positions = mt5.positions_get()
    if positions is None:
        return 0
    return len(positions)


def spread_check(symbol):
    if not getattr(config, "ENABLE_SPREAD_FILTER", True):
        return True, "Spread filter disabled"

    info = mt5.symbol_info(symbol)
    if info is None:
        return False, f"❌ Symbol info not found for {symbol}"

    current_spread = info.spread
    max_spread = get_max_spread(symbol)

    if current_spread > max_spread:
        return False, f"❌ Spread too high ({current_spread} > {max_spread})"

    return True, f"Spread OK ({current_spread} <= {max_spread})"


def ensure_symbol(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        return False, f"❌ Symbol not found: {symbol}"

    if not info.visible:
        if not mt5.symbol_select(symbol, True):
            return False, f"❌ Failed to select symbol: {symbol}"

    return True, "Symbol ready"


def get_order_type(action, order_type):
    action = (action or "").upper()
    order_type = (order_type or "MARKET").upper()

    if order_type == "MARKET":
        return mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
    if order_type == "LIMIT":
        return mt5.ORDER_TYPE_BUY_LIMIT if action == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT
    if order_type == "STOP":
        return mt5.ORDER_TYPE_BUY_STOP if action == "BUY" else mt5.ORDER_TYPE_SELL_STOP

    return None


def get_order_price(symbol, action, order_type, entry):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    action = (action or "").upper()
    order_type = (order_type or "MARKET").upper()

    if order_type == "MARKET":
        return tick.ask if action == "BUY" else tick.bid

    return entry


def get_valid_tps(tps):
    return [tp for tp in tps if isinstance(tp, (int, float)) and tp > 0][:getattr(config, "MAX_TP_ORDERS", 3)]


def allowed_filling_modes():
    return [
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_RETURN,
    ]


def filling_mode_name(mode):
    if mode == mt5.ORDER_FILLING_FOK:
        return "FOK"
    if mode == mt5.ORDER_FILLING_IOC:
        return "IOC"
    if mode == mt5.ORDER_FILLING_RETURN:
        return "RETURN"
    return str(mode)


def validate_stops(symbol, action, price, sl, tp):
    info = mt5.symbol_info(symbol)
    if info is None:
        return False, "❌ Symbol info not found for stop validation"

    point = info.point
    min_stop_points = info.trade_stops_level
    min_distance = min_stop_points * point

    if action == "BUY":
        if sl and sl >= price:
            return False, f"❌ Invalid SL for BUY ({sl} >= {price})"
        if tp and tp <= price:
            return False, f"❌ Invalid TP for BUY ({tp} <= {price})"
        if sl and (price - sl) < min_distance:
            return False, f"❌ SL too close for BUY (min distance {min_distance})"
        if tp and (tp - price) < min_distance:
            return False, f"❌ TP too close for BUY (min distance {min_distance})"

    if action == "SELL":
        if sl and sl <= price:
            return False, f"❌ Invalid SL for SELL ({sl} <= {price})"
        if tp and tp >= price:
            return False, f"❌ Invalid TP for SELL ({tp} >= {price})"
        if sl and (sl - price) < min_distance:
            return False, f"❌ SL too close for SELL (min distance {min_distance})"
        if tp and (price - tp) < min_distance:
            return False, f"❌ TP too close for SELL (min distance {min_distance})"

    return True, "Stops valid"


def send_with_supported_filling(request):
    last_result = None

    for fill_mode in allowed_filling_modes():
        req = dict(request)
        req["type_filling"] = fill_mode

        result = mt5.order_send(req)
        last_result = result

        if result is None:
            continue

        if result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED):
            return True, result, filling_mode_name(fill_mode)

        if result.retcode != 10030:
            return False, result, filling_mode_name(fill_mode)

    return False, last_result, None


def execute(signal, balance):
    symbol = normalize_symbol(signal.get("symbol"))
    action = signal.get("action")
    order_type = signal.get("order_type", "MARKET")
    entry = signal.get("entry")
    sl = signal.get("sl")
    tps = get_valid_tps(signal.get("tps", []))

    if not symbol or symbol in ("SELL", "BUY"):
        return f"❌ Invalid symbol parsed: {symbol}"

    ok, msg = ensure_symbol(symbol)
    if not ok:
        return msg

    ok, msg = spread_check(symbol)
    if not ok:
        return msg

    if not tps:
        return "❌ No valid TP values found"

    order_mt5_type = get_order_type(action, order_type)
    if order_mt5_type is None:
        return f"❌ Unsupported order type: {order_type}"

    price = get_order_price(symbol, action, order_type, entry)
    if price is None:
        return "❌ Failed to get order price"

    per_order_lot = float(getattr(config, "MULTI_TP_LOT_SIZE", 0.01))

    existing_positions = count_open_positions()
    allowed_total = getattr(config, "MAX_OPEN_TRADES", 1)
    needed_orders = len(tps)

    if allowed_total is not None and existing_positions + needed_orders > allowed_total:
        return f"❌ Not enough trade slots: open={existing_positions}, needed={needed_orders}, max={allowed_total}"

    deviation = getattr(config, "DEVIATION", 20)
    magic = getattr(config, "MAGIC_NUMBER", 20260318)

    results = []

    for idx, tp in enumerate(tps, start=1):
        ok, stop_msg = validate_stops(symbol, action, price, sl, tp)
        if not ok:
            results.append({
                "tp_index": idx,
                "tp": tp,
                "success": False,
                "lot": per_order_lot,
                "error": stop_msg
            })
            continue

        request = {
            "action": mt5.TRADE_ACTION_DEAL if order_type.upper() == "MARKET" else mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": per_order_lot,
            "type": order_mt5_type,
            "price": price,
            "sl": sl if sl else 0.0,
            "tp": tp,
            "deviation": deviation,
            "magic": magic,
            "comment": f"TG Bot {order_type} TP{idx}",
            "type_time": mt5.ORDER_TIME_GTC,
        }

        success, mt5_result, fill_name = send_with_supported_filling(request)

        if success:
            results.append({
                "tp_index": idx,
                "tp": tp,
                "success": True,
                "lot": per_order_lot,
                "order_id": getattr(mt5_result, "order", None),
                "deal_id": getattr(mt5_result, "deal", None),
                "retcode": mt5_result.retcode,
                "comment": mt5_result.comment,
                "filling_mode": fill_name,
            })
        else:
            if mt5_result is None:
                err = f"❌ order_send failed: {mt5.last_error()}"
            else:
                err = f"❌ Order failed | retcode={mt5_result.retcode} | comment={mt5_result.comment}"

            results.append({
                "tp_index": idx,
                "tp": tp,
                "success": False,
                "lot": per_order_lot,
                "error": err
            })

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    return {
        "success": success_count > 0,
        "symbol": symbol,
        "action": action,
        "order_type": order_type,
        "entry": price,
        "sl": sl,
        "orders_sent": success_count,
        "orders_failed": fail_count,
        "results": results,
    }

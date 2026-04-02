# risk.py
import config

def calculate_lot(entry, sl, balance, risk_percent=None):
    if config.USE_FIXED_LOT_SIZE:
        return config.DEFAULT_LOT_SIZE

    if risk_percent is None:
        risk_percent = config.RISK_PERCENT

    risk_amount = balance * (risk_percent / 100)
    stop = abs(entry - sl)

    if stop == 0:
        return config.DEFAULT_LOT_SIZE

    lot = risk_amount / (stop * 10)
    return round(max(lot, config.DEFAULT_LOT_SIZE), 2)


def kill_switch(daily_loss_percent):
    return daily_loss_percent >= config.MAX_DAILY_LOSS

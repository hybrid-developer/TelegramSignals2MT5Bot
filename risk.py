# risk.py
from config import MAX_DAILY_LOSS

def calculate_lot(entry, sl, balance, risk_percent):
    risk_amount = balance * (risk_percent / 100)
    stop = abs(entry-sl)
    if stop==0: return 0.01
    return round(max(risk_amount/(stop*10),0.01),2)

def kill_switch(daily_loss_percent):
    return daily_loss_percent >= MAX_DAILY_LOSS
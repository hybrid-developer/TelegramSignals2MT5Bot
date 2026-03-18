# main.py
import MetaTrader5 as mt5
from parser import SignalParser
from executor import execute, build_tp_scaling
from manager import manage_positions
from logger import log_trade
from ai_filter import is_a_plus

mt5.initialize()
parser=SignalParser()
balance=mt5.account_info().balance

while True:
    text_signal=input("Enter signal: ")
    signal=parser.parse(text_signal)
    if not signal:
        print("❌ Invalid signal")
        continue

    if not is_a_plus(signal):
        print("⚠️ Signal rejected by AI filter")
        continue

    signal["tp_levels"]=build_tp_scaling(signal["tps"])
    result=execute(signal,balance)
    print(result)
    manage_positions()
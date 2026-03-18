# logger.py
import json
from datetime import date

FILE="trades.json"

def log_trade(result):
    try:
        with open(FILE,"r") as f: data=json.load(f)
    except: data=[]
    data.append(result)
    with open(FILE,"w") as f: json.dump(data,f,indent=2)

def get_today_trades():
    try:
        with open(FILE,"r") as f: data=json.load(f)
    except: return 0
    today=str(date.today())
    return len([t for t in data if t.get("date")==today])

def calculate_winrate():
    try:
        with open(FILE,"r") as f: data=json.load(f)
    except: return 0
    wins=sum(1 for t in data if t.get("result")=="win")
    total=len(data)
    return round((wins/total)*100,2) if total else 0
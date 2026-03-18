# dashboard.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
from logger import FILE

app=FastAPI()

@app.get("/")
def dashboard():
    try:
        with open(FILE,"r") as f: data=json.load(f)
    except: data=[]
    total_pnl=sum(t.get("pnl",0) for t in data)
    total_trades=len(data)
    winrate=sum(1 for t in data if t.get("result")=="win")/max(1,total_trades)*100
    html=f"""
    <h1>Trading Dashboard</h1>
    <p>Total Trades: {total_trades}</p>
    <p>Total PnL: {total_pnl}</p>
    <p>Win Rate: {winrate:.2f}%</p>
    <h2>Recent Trades:</h2>
    <pre>{json.dumps(data[-10:],indent=2)}</pre>
    """
    return HTMLResponse(html)
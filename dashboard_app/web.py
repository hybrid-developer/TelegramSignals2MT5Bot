# dashboard_app/web.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router

app = FastAPI(title="Trading Dashboard")
app.mount("/static", StaticFiles(directory="dashboard_app/static"), name="static")
app.include_router(router)

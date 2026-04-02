# dashboard_app/routes.py
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .services import (
    load_data,
    enrich_rows,
    apply_filters,
    build_summary,
    build_daily_stats,
    build_category_counts,
    build_symbol_counts,
    build_filter_options,
)

router = APIRouter()
templates = Jinja2Templates(directory="dashboard_app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    category: str = Query(default=""),
    symbol: str = Query(default=""),
    event_type: str = Query(default=""),
    status: str = Query(default=""),
    result: str = Query(default=""),
    day: str = Query(default="")
):
    data = enrich_rows(load_data())

    filtered = apply_filters(
        data=data,
        category=category,
        symbol=symbol,
        event_type=event_type,
        status=status,
        result=result,
        day=day,
    )

    context = {
        "request": request,
        "rows": list(reversed(filtered[-300:])),
        "summary": build_summary(filtered),
        "daily_stats": build_daily_stats(filtered),
        "category_counts": build_category_counts(filtered),
        "symbol_counts": build_symbol_counts(filtered),
        "options": build_filter_options(data),
        "selected": {
            "category": category,
            "symbol": symbol,
            "event_type": event_type,
            "status": status,
            "result": result,
            "day": day,
        },
    }

    return templates.TemplateResponse("dashboard.html", context)

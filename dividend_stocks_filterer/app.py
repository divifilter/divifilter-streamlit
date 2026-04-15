import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request, Form
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List

from configure import read_configurations
from db_functions import MysqlConnection
from helper_functions import radar_dict_to_table

app = FastAPI()
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

# --- One-time startup (mirrors ui.py) ---
configuration = read_configurations()
db = MysqlConnection(
    db_host=configuration["db_host"], db_schema=configuration["db_schema"],
    db_password=configuration["db_pass"], db_port=configuration["db_port"],
    db_user=configuration["db_user"]
)

_raw = db.min_max_all_values()
ranges = {
    # Dividend section
    "streak_default": 5,
    "yield_max": min(max(_raw['yield_max_raw'], _raw['5y_yield_max']), 25.0),
    "dgr_min": max(min(_raw['dgr1y_min'], _raw['dgr3y_min'], _raw['dgr5y_min'], _raw['dgr10y_min']), -25.0),
    "dgr_max": min(max(_raw['dgr1y_max'], _raw['dgr3y_max'], _raw['dgr5y_max'], _raw['dgr10y_max']), 25.0),
    "chowder_max": int(min(_raw['chowder_max_raw'], 25.0)),
    # Financial section
    "price_max": _raw['price_max_raw'],
    "fv_min": int(max(_raw['fv_min_raw'], -25.0)),
    "fv_max": int(max(_raw['fv_max_raw'], 0.0)),
    "revenue_min": _raw['revenue_min'],
    "revenue_max": _raw['revenue_max'],
    "npm_min": _raw['npm_min'],
    "npm_max": _raw['npm_max'],
    "cf_min": _raw['cf_min'],
    "cf_max": _raw['cf_max'],
    "roe_min": _raw['roe_min'],
    "roe_max": _raw['roe_max'],
    "pe_min": max(_raw['pe_min_raw'], -50.0),
    "pe_max": min(_raw['pe_max_raw'], 100.0),
    "pbv_min": _raw['pbv_min'],
    "pbv_max": _raw['pbv_max'],
    "debt_max": _raw['debt_max_raw'],
    "payout_max": _raw['payout_ratio_max_raw'] if _raw['payout_ratio_max_raw'] is not None else 1.0,
    # Exclusion options
    "symbols": db.list_values_of_key_in_db("Symbol"),
    "sectors": db.list_values_of_key_in_db("Sector"),
    "industries": db.list_values_of_key_in_db("Industry"),
}


@app.get("/health")
async def health():
    try:
        await run_in_threadpool(db.run_sql_query, "SELECT 1")
        return JSONResponse({"status": "ok"})
    except Exception:
        return JSONResponse({"status": "error"}, status_code=503)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db_update_dates = await run_in_threadpool(db.check_db_update_dates)
    return templates.TemplateResponse(request, "index.html", {
        "ranges": ranges,
        "db_update_dates": db_update_dates,
        "ga_measurement_id": configuration.get("ga_measurement_id", ""),
    })


@app.post("/filter", response_class=HTMLResponse)
async def filter_stocks(
    request: Request,
    min_streak_years: int = Form(5),
    yield_range_min: float = Form(0.0),
    yield_range_max: float = Form(10.0),
    min_dgr: float = Form(0.0),
    chowder_number: int = Form(0),
    price_range_min: float = Form(1.0),
    price_range_max: float = Form(500.0),
    fair_value: int = Form(0),
    min_revenue: float = Form(0.0),
    min_npm: float = Form(0.0),
    min_cf_per_share: float = Form(0.0),
    min_roe: float = Form(0.0),
    pe_range_min: float = Form(-50.0),
    pe_range_max: float = Form(100.0),
    max_price_per_book_value: float = Form(10.0),
    max_debt_per_capital_value: float = Form(1.0),
    max_payout_ratio: float = Form(1.0),
    excluded_symbols: List[str] = Form(default=[]),
    excluded_sectors: List[str] = Form(default=[]),
    excluded_industries: List[str] = Form(default=[]),
):
    results = await run_in_threadpool(
        db.run_filter_query,
        min_streak_years, yield_range_min, yield_range_max,
        min_dgr, chowder_number, price_range_min, price_range_max,
        fair_value, min_revenue, min_npm, min_cf_per_share, min_roe,
        pe_range_min, pe_range_max, max_price_per_book_value,
        max_debt_per_capital_value, max_payout_ratio,
        excluded_symbols, excluded_sectors, excluded_industries
    )
    df = radar_dict_to_table(results)
    return templates.TemplateResponse(request, "_table.html", {
        "table_html": df.to_html(
            classes="table table-striped table-hover table-sm", border=0, index=True
        ),
        "row_count": len(df),
    })

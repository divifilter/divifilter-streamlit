import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request, Form
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

ranges = {
    # Dividend section
    "streak_default": 5,
    "yield_max": min(max(db.min_max_value_of_any_stock_key("Div Yield", "max"),
                         db.min_max_value_of_any_stock_key("5Y Avg Yield", "max")), 25.0),
    "dgr_min": max(min(db.min_max_value_of_any_stock_key("DGR 1Y", "min"),
                       db.min_max_value_of_any_stock_key("DGR 3Y", "min"),
                       db.min_max_value_of_any_stock_key("DGR 5Y", "min"),
                       db.min_max_value_of_any_stock_key("DGR 10Y", "min")), -25.0),
    "dgr_max": min(max(db.min_max_value_of_any_stock_key("DGR 1Y", "max"),
                       db.min_max_value_of_any_stock_key("DGR 3Y", "max"),
                       db.min_max_value_of_any_stock_key("DGR 5Y", "max"),
                       db.min_max_value_of_any_stock_key("DGR 10Y", "max")), 25.0),
    "chowder_max": int(min(db.min_max_value_of_any_stock_key("Chowder Number", "max"), 25.0)),
    # Financial section
    "price_max": db.min_max_value_of_any_stock_key("Price", "max"),
    "fv_min": int(max(db.min_max_value_of_any_stock_key("FV %", "min"), -25.0)),
    "fv_max": int(max(db.min_max_value_of_any_stock_key("FV %", "max"), 0.0)),
    "revenue_min": db.min_max_value_of_any_stock_key("Revenue 1Y", "min"),
    "revenue_max": db.min_max_value_of_any_stock_key("Revenue 1Y", "max"),
    "npm_min": db.min_max_value_of_any_stock_key("NPM", "min"),
    "npm_max": db.min_max_value_of_any_stock_key("NPM", "max"),
    "cf_min": db.min_max_value_of_any_stock_key("CF/Share", "min"),
    "cf_max": db.min_max_value_of_any_stock_key("CF/Share", "max"),
    "roe_min": db.min_max_value_of_any_stock_key("ROE", "min"),
    "roe_max": db.min_max_value_of_any_stock_key("ROE", "max"),
    "pe_min": max(db.min_max_value_of_any_stock_key("P/E", "min"), -50.0),
    "pe_max": min(db.min_max_value_of_any_stock_key("P/E", "max"), 100.0),
    "pbv_min": db.min_max_value_of_any_stock_key("P/BV", "min"),
    "pbv_max": db.min_max_value_of_any_stock_key("P/BV", "max"),
    "debt_max": db.min_max_value_of_any_stock_key("Debt/Capital", "max"),
    # Exclusion options
    "symbols": db.list_values_of_key_in_db("Symbol"),
    "sectors": db.list_values_of_key_in_db("Sector"),
    "industries": db.list_values_of_key_in_db("Industry"),
}


@app.get("/health")
async def health():
    try:
        db.run_sql_query("SELECT 1")
        return JSONResponse({"status": "ok"})
    except Exception:
        return JSONResponse({"status": "error"}, status_code=503)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db_update_dates = db.check_db_update_dates()
    initial_df = radar_dict_to_table(db.run_filter_query(
        ranges["streak_default"], 0.0, ranges["yield_max"], 0.0, 0,
        1.0, ranges["price_max"], ranges["fv_max"], 0.0, 0.0, 0.0, 0.0,
        ranges["pe_min"], ranges["pe_max"], ranges["pbv_max"],
        ranges["debt_max"], [], [], []
    ))
    return templates.TemplateResponse(request, "index.html", {
        "ranges": ranges,
        "db_update_dates": db_update_dates,
        "table_html": initial_df.to_html(
            classes="table table-striped table-hover table-sm table-dark", border=0, index=True
        ),
        "row_count": len(initial_df),
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
    excluded_symbols: List[str] = Form(default=[]),
    excluded_sectors: List[str] = Form(default=[]),
    excluded_industries: List[str] = Form(default=[]),
):
    results = db.run_filter_query(
        min_streak_years, yield_range_min, yield_range_max,
        min_dgr, chowder_number, price_range_min, price_range_max,
        fair_value, min_revenue, min_npm, min_cf_per_share, min_roe,
        pe_range_min, pe_range_max, max_price_per_book_value,
        max_debt_per_capital_value, excluded_symbols, excluded_sectors,
        excluded_industries
    )
    df = radar_dict_to_table(results)
    return templates.TemplateResponse(request, "_table.html", {
        "table_html": df.to_html(
            classes="table table-striped table-hover table-sm table-dark", border=0, index=True
        ),
        "row_count": len(df),
    })

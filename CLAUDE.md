# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Divifilter is a FastAPI + HTMX web app for filtering dividend stocks. It connects to a MySQL/MariaDB database containing dividend stock data and provides an interactive UI with sidebar filters (dividend metrics, financial metrics, exclusions). Results display as a pandas DataFrame table rendered as HTML, updated via HTMX partial swaps without full page reloads.

## Commands

```bash
# Run the app locally (requires DB connection via env vars or config files)
uvicorn dividend_stocks_filterer.app:app --host 0.0.0.0 --port 8080 --reload

# Run all tests
coverage run -m unittest

# Lint (matches CI config)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Docker
docker build -t divifilter-ui .
docker run -p 80:80 divifilter-ui

# Health check
curl http://localhost:8080/health
```

## Architecture

Five modules in `dividend_stocks_filterer/`:

- **app.py** — FastAPI entry point. Computes all slider range values once at startup from DB min/max queries. `GET /` serves the full page; `POST /filter` returns the HTMX table fragment. Uses Jinja2 templates.
- **templates/index.html** — Full-page Bootstrap 5 layout: `col-md-3` sidebar with noUiSlider range sliders + Tom Select multiselects + HTMX form; `col-md-9` results area.
- **templates/_table.html** — HTMX partial fragment: row count + table div (swapped on every filter change).
- **db_functions.py** — `MysqlConnection` class wrapping PyMySQL. Maintains two connections (tuple and dict cursor). Key method `run_filter_query()` builds a parameterized SQL WHERE clause across ~19 filter dimensions against `dividend_data_table`. Column names use backtick quoting (they contain spaces like `Div Yield`, `No Years`).
- **configure.py** — Uses `parse_it` library to read config from files, env vars, or defaults. Required: `db_host`, `db_pass`. Defaults: `db_port=3306`, `db_user=root`, `db_schema=defaultdb`.
- **helper_functions.py** — Single function `radar_dict_to_table()` converting dict to pandas DataFrame.

## Database

Two tables: `dividend_data_table` (stock data with financial/dividend columns) and `dividend_update_times` (metadata on data freshness). Column names have spaces and special characters — always use backtick quoting in SQL.

## CI/CD

GitHub Actions runs on push to main/master:
1. Tests + flake8 lint on Python 3.12, 3.13, 3.14
2. Multi-arch Docker build (amd64/arm64) pushed to DockerHub
3. Versioned image deployed to Northflank

PR workflow runs tests and lint only.

## Code Style

- Max line length: 127 characters
- Max cyclomatic complexity: 10

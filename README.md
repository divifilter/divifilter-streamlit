# divifilter-ui

[![CI/CD](https://github.com/divifilter/divifilter-ui/actions/workflows/full_ci_cd_workflow.yml/badge.svg)](https://github.com/divifilter/divifilter-ui/actions/workflows/full_ci_cd_workflow.yml)
[![codecov](https://codecov.io/gh/divifilter/divifilter-ui/branch/main/graph/badge.svg?token=ZB0FX61FU9)](https://codecov.io/gh/divifilter/divifilter-ui)

A web app for filtering dividend stocks by financial and dividend metrics. Built with FastAPI and HTMX, it connects to a MySQL/MariaDB database and provides an interactive UI with real-time filtering — no full page reloads.

## Features

- Interactive sidebar filters: dividend yield, streak years, DGR, Chowder Number, P/E, price, fair value, revenue, NPM, ROE, CF/Share, P/BV, Debt/Capital
- Exclude stocks by symbol, sector, or industry
- Save and load filter presets
- Dark/light theme toggle
- Real-time results via HTMX partial swaps
- Responsive design with mobile offcanvas sidebar

## Tech Stack

FastAPI, HTMX, Bootstrap 5, noUiSlider, Tom Select, Jinja2, PyMySQL, Pandas

## Quick Start

### Prerequisites

- Python 3.12+
- MySQL/MariaDB database with dividend data

### Configuration

Environment variables (or config files via [`parse_it`](https://github.com/naorlivne/parse_it)):

| Variable    | Required | Default     |
|-------------|----------|-------------|
| `DB_HOST`   | Yes      | —           |
| `DB_PASS`   | Yes      | —           |
| `DB_PORT`   | No       | `3306`      |
| `DB_USER`   | No       | `root`      |
| `DB_SCHEMA` | No       | `defaultdb` |

### Run locally

```bash
pip install -r requirements.txt
uvicorn dividend_stocks_filterer.app:app --host 0.0.0.0 --port 8080 --reload
```

### Docker

Prebuilt multi-arch images (amd64/arm64) are available on [Docker Hub](https://hub.docker.com/r/naorlivne/divifilter-ui):

```bash
docker run -p 80:80 -e DB_HOST=... -e DB_PASS=... naorlivne/divifilter-ui
```

Or build locally:

```bash
docker build -t divifilter-ui .
docker run -p 80:80 -e DB_HOST=... -e DB_PASS=... divifilter-ui
```

## Related Projects

- [divifilter-data-updater](https://github.com/divifilter/divifilter-data-updater) — Data scraper that populates the MySQL/MariaDB database this app reads from.

## Testing

```bash
coverage run -m unittest
```

## Linting

```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## License

This project is licensed under the [GNU Lesser General Public License v3.0](LICENSE).

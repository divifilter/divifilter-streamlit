import sys
import types
import unittest
import importlib
from unittest.mock import MagicMock

import pandas


class TestApp(unittest.TestCase):

    def setUp(self):
        mock_mysql = MagicMock()
        mock_mysql.check_db_update_dates.return_value = {
            "radar_file": "2024-01-01",
            "yahoo_finance": "2024-01-02"
        }
        mock_mysql.min_max_value_of_any_stock_key.return_value = 10.0
        mock_mysql.list_values_of_key_in_db.return_value = ["AAPL", "MSFT"]
        mock_mysql.run_filter_query.return_value = {}
        self.mock_mysql = mock_mysql

        mock_configure = types.ModuleType('configure')
        mock_configure.read_configurations = MagicMock(return_value={
            "db_host": "h", "db_port": 3306, "db_user": "u",
            "db_pass": "p", "db_schema": "s"
        })
        mock_db_mod = types.ModuleType('db_functions')
        mock_db_mod.MysqlConnection = MagicMock(return_value=mock_mysql)
        mock_helper = types.ModuleType('helper_functions')
        mock_helper.radar_dict_to_table = MagicMock(return_value=pandas.DataFrame())

        self.mocks = {
            'configure': mock_configure,
            'helper_functions': mock_helper,
            'db_functions': mock_db_mod,
        }
        self.saved = {k: sys.modules.get(k) for k in self.mocks}
        for k, v in self.mocks.items():
            sys.modules[k] = v

        app_key = 'dividend_stocks_filterer.app'
        sys.modules.pop(app_key, None)
        self.app_module = importlib.import_module(app_key)

        from fastapi.testclient import TestClient
        self.client = TestClient(self.app_module.app)

    def tearDown(self):
        for k in self.mocks:
            if self.saved[k] is not None:
                sys.modules[k] = self.saved[k]
            elif k in sys.modules:
                del sys.modules[k]
        sys.modules.pop('dividend_stocks_filterer.app', None)

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_contains_form(self):
        response = self.client.get("/")
        self.assertIn('hx-post="/filter"', response.text)

    def test_index_contains_update_dates(self):
        response = self.client.get("/")
        self.assertIn("2024-01-01", response.text)

    def test_post_filter_returns_200(self):
        response = self.client.post("/filter", data={
            "min_streak_years": 5,
            "yield_range_min": 0.0,
            "yield_range_max": 10.0,
            "min_dgr": 0.0,
            "chowder_number": 0,
            "price_range_min": 1.0,
            "price_range_max": 500.0,
            "fair_value": 0,
            "min_revenue": 0.0,
            "min_npm": 0.0,
            "min_cf_per_share": 0.0,
            "min_roe": 0.0,
            "pe_range_min": -50.0,
            "pe_range_max": 100.0,
            "max_price_per_book_value": 10.0,
            "max_debt_per_capital_value": 1.0,
        })
        self.assertEqual(response.status_code, 200)

    def test_post_filter_calls_run_filter_query(self):
        self.mock_mysql.run_filter_query.reset_mock()
        self.client.post("/filter", data={
            "min_streak_years": 10,
            "yield_range_min": 1.0,
            "yield_range_max": 8.0,
            "min_dgr": 0.5,
            "chowder_number": 5,
            "price_range_min": 10.0,
            "price_range_max": 200.0,
            "fair_value": 5,
            "min_revenue": 0.01,
            "min_npm": 1.0,
            "min_cf_per_share": 0.5,
            "min_roe": 5.0,
            "pe_range_min": 0.0,
            "pe_range_max": 30.0,
            "max_price_per_book_value": 3.0,
            "max_debt_per_capital_value": 0.6,
        })
        self.mock_mysql.run_filter_query.assert_called_once()

    def test_post_filter_returns_table_html(self):
        self.mocks['helper_functions'].radar_dict_to_table.return_value = pandas.DataFrame(
            {"Symbol": ["AAPL"], "Price": [150.0]}
        )
        response = self.client.post("/filter", data={
            "min_streak_years": 5,
            "yield_range_min": 0.0,
            "yield_range_max": 10.0,
            "min_dgr": 0.0,
            "chowder_number": 0,
            "price_range_min": 1.0,
            "price_range_max": 500.0,
            "fair_value": 0,
            "min_revenue": 0.0,
            "min_npm": 0.0,
            "min_cf_per_share": 0.0,
            "min_roe": 0.0,
            "pe_range_min": -50.0,
            "pe_range_max": 100.0,
            "max_price_per_book_value": 10.0,
            "max_debt_per_capital_value": 1.0,
        })
        self.assertIn("<table", response.text)

    def test_post_filter_empty_results(self):
        self.mock_mysql.run_filter_query.return_value = {}
        self.mocks['helper_functions'].radar_dict_to_table.return_value = pandas.DataFrame()
        response = self.client.post("/filter", data={
            "min_streak_years": 50,
            "yield_range_min": 0.0,
            "yield_range_max": 0.0,
            "min_dgr": 0.0,
            "chowder_number": 0,
            "price_range_min": 1.0,
            "price_range_max": 500.0,
            "fair_value": 0,
            "min_revenue": 0.0,
            "min_npm": 0.0,
            "min_cf_per_share": 0.0,
            "min_roe": 0.0,
            "pe_range_min": -50.0,
            "pe_range_max": 100.0,
            "max_price_per_book_value": 10.0,
            "max_debt_per_capital_value": 1.0,
        })
        self.assertIn("0 stock(s) found", response.text)

    def test_post_filter_excluded_symbols_forwarded(self):
        self.mock_mysql.run_filter_query.reset_mock()
        self.client.post("/filter", data={
            "min_streak_years": 5,
            "yield_range_min": 0.0,
            "yield_range_max": 10.0,
            "min_dgr": 0.0,
            "chowder_number": 0,
            "price_range_min": 1.0,
            "price_range_max": 500.0,
            "fair_value": 0,
            "min_revenue": 0.0,
            "min_npm": 0.0,
            "min_cf_per_share": 0.0,
            "min_roe": 0.0,
            "pe_range_min": -50.0,
            "pe_range_max": 100.0,
            "max_price_per_book_value": 10.0,
            "max_debt_per_capital_value": 1.0,
            "excluded_symbols": ["AAPL", "MSFT"],
        })
        args = self.mock_mysql.run_filter_query.call_args
        self.assertIn("AAPL", args[0][16])
        self.assertIn("MSFT", args[0][16])

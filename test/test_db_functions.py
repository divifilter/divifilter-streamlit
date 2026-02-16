import unittest
from unittest.mock import patch, MagicMock
from dividend_stocks_filterer.db_functions import MysqlConnection


class TestMysqlConnection(unittest.TestCase):

    @patch('dividend_stocks_filterer.db_functions.pymysql.connect')
    def setUp(self, mock_connect):
        self.mock_conn = MagicMock()
        self.mock_dict_conn = MagicMock()
        mock_connect.side_effect = [self.mock_conn, self.mock_dict_conn]
        self.db = MysqlConnection(
            db_host="localhost", db_port=3306, db_user="root",
            db_password="pass", db_schema="testdb"
        )

    def test_init_creates_two_connections(self):
        self.assertIs(self.db.conn, self.mock_conn)
        self.assertIs(self.db.dict_conn, self.mock_dict_conn)

    def test_run_sql_query_tuple(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        self.mock_conn.cursor.return_value = mock_cursor

        result = self.db.run_sql_query("SELECT 1", "tuple")

        mock_cursor.execute.assert_called_once_with("SELECT 1")
        self.assertEqual(result, [("row1",), ("row2",)])

    def test_run_sql_query_dict(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"col": "val"}]
        self.mock_dict_conn.cursor.return_value = mock_cursor

        result = self.db.run_sql_query("SELECT 1", "dict")

        mock_cursor.execute.assert_called_once_with("SELECT 1")
        self.assertEqual(result, [{"col": "val"}])

    def test_run_sql_query_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            self.db.run_sql_query("SELECT 1", "invalid")

    def test_check_db_update_dates(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("radar_file", "2024-01-01"),
            ("yahoo_finance", "2024-01-02")
        ]
        self.mock_conn.cursor.return_value = mock_cursor

        result = self.db.check_db_update_dates()

        self.assertEqual(result, {"radar_file": "2024-01-01", "yahoo_finance": "2024-01-02"})

    def test_min_max_value_max(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(25.5,)]
        self.mock_conn.cursor.return_value = mock_cursor

        result = self.db.min_max_value_of_any_stock_key("Div Yield", "max")

        self.assertEqual(result, 25.5)
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("MAX", executed_query)
        self.assertIn("`Div Yield`", executed_query)

    def test_min_max_value_min(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(0.1,)]
        self.mock_conn.cursor.return_value = mock_cursor

        result = self.db.min_max_value_of_any_stock_key("Price", "min")

        self.assertEqual(result, 0.1)
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("MIN", executed_query)
        self.assertIn("`Price`", executed_query)

    def test_min_max_value_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.db.min_max_value_of_any_stock_key("Price", "avg")

    def test_list_values_of_key_in_db(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("AAPL",), ("MSFT",), ("GOOG",)]
        self.mock_conn.cursor.return_value = mock_cursor

        result = self.db.list_values_of_key_in_db("Symbol")

        self.assertEqual(result, ["AAPL", "MSFT", "GOOG"])
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("DISTINCT", executed_query)
        self.assertIn("Symbol", executed_query)

    def test_run_filter_query_no_exclusions(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"Symbol": "AAPL", "Price": 150.0},
            {"Symbol": "MSFT", "Price": 300.0}
        ]
        self.mock_dict_conn.cursor.return_value = mock_cursor

        result = self.db.run_filter_query(
            min_streak_years=10, yield_range_min=0.0, yield_range_max=10.0,
            min_dgr=0.0, chowder_number=0, price_range_min=1.0, price_range_max=500.0,
            fair_value=25, min_eps=0.0, min_revenue=0.0, min_npm=0.0,
            min_cf_per_share=0.0, min_roe=0.0, pe_range_min=0.0, pe_range_max=50.0,
            max_price_per_book_value=100.0, max_debt_per_capital_value=1.0,
            excluded_symbols=[], excluded_sectors=[], excluded_industries=[]
        )

        self.assertEqual(len(result), 2)
        self.assertIn("AAPL", result)
        self.assertIn("MSFT", result)
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertNotIn("NOT IN", executed_query)

    def test_run_filter_query_with_exclusions(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"Symbol": "MSFT", "Price": 300.0}
        ]
        self.mock_dict_conn.cursor.return_value = mock_cursor

        result = self.db.run_filter_query(
            min_streak_years=10, yield_range_min=0.0, yield_range_max=10.0,
            min_dgr=0.0, chowder_number=0, price_range_min=1.0, price_range_max=500.0,
            fair_value=25, min_eps=0.0, min_revenue=0.0, min_npm=0.0,
            min_cf_per_share=0.0, min_roe=0.0, pe_range_min=0.0, pe_range_max=50.0,
            max_price_per_book_value=100.0, max_debt_per_capital_value=1.0,
            excluded_symbols=["AAPL"], excluded_sectors=["Technology"],
            excluded_industries=["Software"]
        )

        self.assertEqual(len(result), 1)
        self.assertIn("MSFT", result)
        executed_query = mock_cursor.execute.call_args[0][0]
        self.assertIn("`Symbol` NOT IN", executed_query)
        self.assertIn("'AAPL'", executed_query)
        self.assertIn("`Sector` NOT IN", executed_query)
        self.assertIn("'Technology'", executed_query)
        self.assertIn("`Industry` NOT IN", executed_query)
        self.assertIn("'Software'", executed_query)

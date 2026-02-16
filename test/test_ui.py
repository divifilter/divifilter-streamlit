import sys
import types
import unittest
from unittest.mock import MagicMock
import importlib


class TestUI(unittest.TestCase):

    def test_ui_loads_and_displays(self):
        # Create mock streamlit with return values matching ui.py's expectations
        mock_st = MagicMock()
        mock_st.slider.side_effect = [
            10,            # min_streak_years (single int)
            (0.0, 10.0),   # yield_range_min, yield_range_max (tuple)
            0.0,           # min_dgr (single float)
            0,             # chowder_number (single int)
            (1.0, 500.0),  # price_range_min, price_range_max (tuple)
            25,            # fair_value (single int)
            0.0,           # min_revenue
            0.0,           # min_npm
            0.0,           # min_cf_per_share
            0.0,           # min_roe
            (0.0, 20.0),   # pe_range_min, pe_range_max (tuple)
            100.0,         # max_price_per_book_value
            0.5,           # max_debt_per_capital_value
        ]
        mock_st.multiselect.return_value = []

        # Create mock MysqlConnection instance
        mock_mysql = MagicMock()
        mock_mysql.check_db_update_dates.return_value = {
            "radar_file": "2024-01-01",
            "yahoo_finance": "2024-01-02"
        }
        mock_mysql.min_max_value_of_any_stock_key.return_value = 10.0
        mock_mysql.list_values_of_key_in_db.return_value = ["AAPL", "MSFT"]
        mock_mysql.run_filter_query.return_value = {}

        # Create mock modules for the non-package imports that ui.py uses
        mock_configure = types.ModuleType('configure')
        mock_configure.read_configurations = MagicMock(return_value={
            "db_host": "localhost",
            "db_port": 3306,
            "db_user": "root",
            "db_pass": "pass",
            "db_schema": "testdb"
        })

        mock_helper = types.ModuleType('helper_functions')
        mock_helper.radar_dict_to_table = MagicMock(return_value=MagicMock())

        mock_db = types.ModuleType('db_functions')
        mock_db.MysqlConnection = MagicMock(return_value=mock_mysql)

        # Install mocks in sys.modules, saving originals for cleanup
        mocks = {
            'streamlit': mock_st,
            'configure': mock_configure,
            'helper_functions': mock_helper,
            'db_functions': mock_db,
        }
        saved = {name: sys.modules.get(name) for name in mocks}
        for name, mod in mocks.items():
            sys.modules[name] = mod

        ui_key = 'dividend_stocks_filterer.ui'
        saved_ui = sys.modules.pop(ui_key, None)

        try:
            importlib.import_module(ui_key)

            mock_configure.read_configurations.assert_called_once()
            mock_db.MysqlConnection.assert_called_once()
            mock_mysql.check_db_update_dates.assert_called_once()
            mock_mysql.run_filter_query.assert_called_once()
            mock_helper.radar_dict_to_table.assert_called_once()
        finally:
            # Restore sys.modules to original state
            if saved_ui is not None:
                sys.modules[ui_key] = saved_ui
            elif ui_key in sys.modules:
                del sys.modules[ui_key]
            for name in mocks:
                if saved[name] is not None:
                    sys.modules[name] = saved[name]
                elif name in sys.modules:
                    del sys.modules[name]

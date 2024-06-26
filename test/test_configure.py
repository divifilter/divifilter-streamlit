import unittest
from dividend_stocks_filterer.configure import read_configurations


class TestReadConfigurations(unittest.TestCase):

    def test_read_configurations(self):
        # Test reading all configurations with default values
        config = read_configurations()
        self.assertEqual(config["db_user"], "root")

    def test_read_configurations_missing_key(self):
        # Test missing configuration key
        config = read_configurations(config_folder="tests/test_configs/missing_key")
        with self.assertRaises(KeyError):
            config["non_existent_key"]

    def test_read_configurations_default_values(self):
        # Test reading configurations with default values and some overridden values
        config = read_configurations(config_folder="tests/test_configs/default_values")
        self.assertEqual(config["db_port"], 3306)
        self.assertEqual(config["db_user"], "root")
        self.assertEqual(config["db_schema"], "defaultdb")

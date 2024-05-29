import pymysql
from typing import List


class MysqlConnection:

    def __init__(self, db_host: str, db_port: int, db_user: str, db_password: str, db_schema: str):
        self.conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_schema)

    def run_sql_query(self, sql_query):
        cur = self.conn.cursor()
        cur.execute(sql_query)
        query_response = cur.fetchall()
        return query_response

    def check_db_update_dates(self):
        db_update_query = "SELECT * FROM dividend_update_times"
        return dict(self.run_sql_query(db_update_query))

    def get_tickers_from_db(self):
        """
        Retrieve a list of tickers from the 'dividend_data_table' in the database.

        Returns:
            list: List of tickers.
        """
        # Create a SQL query to select all distinct tickers from the table
        query = "SELECT DISTINCT Symbol FROM dividend_data_table;"

        # Execute the query and fetch the results
        result = self.run_sql_query(query)

        # Extract the tickers from the result set
        tickers = [row[0] for row in result]

        return tickers

    def run_filter_query(self, min_streak_years: int, yield_range_min: float, yield_range_max: float,
                         min_dgr: float, chowder_number: float, price_range_min: float, price_range_max: float,
                         fair_value: float, min_eps: float, min_revenue: float, min_npm: float, min_cf_per_share: float,
                         min_roe: float, pe_range_min: float, pe_range_max: float, max_price_per_book_value: float,
                         max_debt_per_capital_value: float, excluded_symbols: List[str], excluded_sectors: List[str],
                         excluded_industries: List[str]) -> dict:
        filter_query = """
            SELECT *
            FROM your_table_name
            WHERE 
                `No Years` >= {}
                AND `Div Yield` BETWEEN {} AND {}
                AND `5Y Avg Yield` BETWEEN {} AND {}
                AND `DGR 1Y` >= {}
                AND `DGR 3Y` >= {}
                AND `DGR 5Y` >= {}
                AND `DGR 10Y` >= {}
                AND `Chowder Number` >= {}
                AND `Price` BETWEEN {} AND {}
                AND `FV %` <= {}
                AND `EPS 1Y` >= {}
                AND `Revenue 1Y` >= {}
                AND `NPM` >= {}
                AND `CF/Share` >= {}
                AND `ROE` >= {}
                AND `P/E` BETWEEN {} AND {}
                AND `P/BV` <= {}
                AND `Debt/Capital` <= {}
                AND `Symbol` NOT IN {}
                AND `Sector` NOT IN {}
                AND `Industry` NOT IN {}
        """.format(min_streak_years, yield_range_min, yield_range_max, yield_range_min, yield_range_max,
                   min_dgr, min_dgr, min_dgr, min_dgr, chowder_number, price_range_min, price_range_max,
                   fair_value, min_eps, min_revenue, min_npm, min_cf_per_share, min_roe,
                   pe_range_min, pe_range_max, max_price_per_book_value, max_debt_per_capital_value,
                   tuple(excluded_symbols), tuple(excluded_sectors), tuple(excluded_industries))
        return dict(self.run_sql_query(filter_query))

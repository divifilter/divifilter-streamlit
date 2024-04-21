import pymysql


class MysqlConnection:

    def __init__(self, db_host: str, db_port: int, db_user: str, db_password: str, db_schema: str):
        self.conn = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_schema)

    def run_sql_query(self, sql_query):
        cur = self.conn.cursor()
        cur.execute(sql_query)
        query_response = cur.fetchall()
        return query_response

    def check_db_update_dates(self):
        if not self.engine.dialect.has_table(self.conn, "dividend_update_times"):
            self.dividend_update_times.create(self.conn)
        data_dict = dict(self.conn.execute(select(self.dividend_update_times)).fetchall())
        return data_dict

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






query = """
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
           excluded_symbols, excluded_sectors, excluded_industries)



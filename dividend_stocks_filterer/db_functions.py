from sqlalchemy import create_engine, MetaData, Table, Column, String, text, select, inspect
import pandas as pd


class MysqlConnection:

    def __init__(self, uri_string: str):
        # check due to pymsql requiring changes to the URI string that are often forgetten
        if "pymysql" not in uri_string:
            uri_string = uri_string.replace("mysql", "mysql+pymysql", 1)
        self.engine = create_engine(uri_string, echo=False)
        self.conn = self.engine.connect()
        self.meta = MetaData()
        self.dividend_update_times = Table(
            'dividend_update_times', self.meta,
            Column('name', String(32), primary_key=True, unique=True),
            Column('last_update_time', String(32))
        )

    def update_data_table_from_data_frame(self, data_table_to_update: pd.DataFrame):
        data_table_to_update.to_sql("dividend_data_table", con=self.engine, if_exists="replace", index=False)

    def update_metadata_table(self, time_dict_to_update: dict):
        self.meta.create_all(self.conn, tables=[self.dividend_update_times])
        for timestamp_key, timestamp_value in time_dict_to_update.items():
            self.run_sql_query("INSERT INTO dividend_update_times (name, last_update_time) VALUES ('" + timestamp_key +
                               "', '" + timestamp_value + "') ON DUPLICATE KEY UPDATE last_update_time = '"
                               + timestamp_value + "';")

    def run_sql_query(self, sql_query):
        query = text(sql_query)
        result = self.conn.execute(query)
        if "SELECT" in query.text.upper():
            data = result.fetchall()
        else:
            data = None
            self.conn.commit()
        return data

    def check_db_update_dates(self):
        if not self.engine.dialect.has_table(self.conn, "dividend_update_times"):
            self.dividend_update_times.create(self.conn)
        data_dict = dict(self.conn.execute(select(self.dividend_update_times)).fetchall())
        return data_dict

    def update_data_table(self, finviz_data: tuple):
        """
        Update the 'dividend_data_table' with data obtained from Finviz for a list of tickers.

        Args:
            finviz_data (tuple): Tuple containing a timestamp and a dictionary of data for tickers.

        Returns:
            None
        """
        # Check if the 'dividend_data_table' exists; if not, create it
        if not self.engine.dialect.has_table(self.conn, "dividend_data_table"):
            self.create_dividend_data_table()

        # Ensure that finviz_data is a tuple with the expected structure
        if not (isinstance(finviz_data, tuple) and len(finviz_data) == 2):
            raise ValueError("finviz_data must be a tuple containing a timestamp and a dictionary")

        timestamp, ticker_data = finviz_data

        # Iterate through the ticker data and update rows in the database
        for symbol, data in ticker_data.items():
            # Check if the columns exist in the table; if not, create them
            for column_name, value in data.items():
                if not self.column_exists("dividend_data_table", column_name):
                    self.add_column_to_table("dividend_data_table", column_name)

                # Construct the SQL update statement dynamically based on columns with data
                if value is not None:
                    update_sql = f"""
                        UPDATE dividend_data_table
                        SET `{column_name}` = COALESCE('{value}', `{column_name}`)
                        WHERE Symbol = '{symbol}';
                    """
                    self.run_sql_query(update_sql)

    def create_dividend_data_table(self):
        """
        Create the 'dividend_data_table' if it does not exist.

        Returns:
            None
        """
        dividend_data_table = Table(
            'dividend_data_table', self.meta,
            Column('Symbol', String(32), primary_key=True),
            Column('Company', String(255)),
            Column('Sector', String(255)),
            Column('No Years', String(32)),
            Column('Price', String(32)),
            Column('Div Yield', String(32)),
            Column('5Y Avg Yield', String(32)),
            Column('Current Div', String(32)),
            Column('Payouts/ Year', String(32)),
            Column('Annualized', String(32)),
            Column('Low', String(32)),
            Column('High', String(32)),
            Column('DGR 1Y', String(32)),
            Column('DGR 3Y', String(32)),
            Column('DGR 5Y', String(32)),
            Column('DGR 10Y', String(32)),
            Column('TTR 1Y', String(32)),
            Column('TTR 3Y', String(32)),
            Column('Fair Value', String(32)),
            Column('FV %', String(32)),
            Column('Chowder Number', String(32)),
            Column('EPS 1Y', String(32)),
            Column('Revenue 1Y', String(32)),
            Column('NPM', String(32)),
            Column('CF/Share', String(32)),
            Column('ROE', String(32)),
            Column('Debt/Capital', String(32)),
            Column('ROTC', String(32)),
            Column('P/E', String(32)),
            Column('P/BV', String(32)),
            Column('PEG', String(32)),
            Column('Industry', String(255))
        )

        if not inspect(self.conn).has_table("dividend_data_table"):
            dividend_data_table.create(self.conn)

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

    def column_exists(self, table_name, column_name):
        inspector = inspect(self.engine)
        return column_name in [col['name'] for col in inspector.get_columns(table_name)]

    def add_column_to_table(self, table_name, column_name):
        # Enclose column name with backticks to handle spaces
        column_name_with_backticks = f"`{column_name}`"
        self.run_sql_query(f'ALTER TABLE {table_name} ADD COLUMN {column_name_with_backticks} VARCHAR(255);')


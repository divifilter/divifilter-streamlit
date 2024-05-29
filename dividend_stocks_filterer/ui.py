import streamlit as st
from configure import *
from helper_functions import *
from db_functions import *


configuration = read_configurations()

st.set_page_config(layout="wide", page_title="Divifilter - easily filter dividends stocks")
hide_streamlit_style = """
<style>
.block-container {
                    margin-top: -60px;
                    padding-bottom: 0rem;
                }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

mysql_connection = MysqlConnection(db_host=configuration["db_host"], db_schema=configuration["db_schema"],
                                   db_password=configuration["db_pass"], db_port=configuration["db_port"],
                                   db_user=configuration["db_user"])
db_update_dates = mysql_connection.check_db_update_dates()

st.title('Divifilter')
st.text("dividend file update date: " + db_update_dates["radar_file"] + ", yahoo finance update time: " +
        db_update_dates["yahoo_finance"])

with st.sidebar:

    with st.expander("Dividend filtering options", expanded=True):

        # filter to only stocks with a dividend streak of over selected # of years
        min_streak_years = st.slider(label="Select minimum number of years of dividend streaks to display", min_value=5,
                                     max_value=50, value=18, key="min_dividend_streak_years",
                                     help="Choose the minimum number of consecutive years a stock has paid dividends "
                                          "to be displayed")

        # filter based on yield, both current & 5y avg
        max_stock_yield_to_filter = mysql_connection.min_max_value_of_any_stock_key( "Div Yield", "max")
        max_stock_yield_to_filter_5y_avg = mysql_connection.min_max_value_of_any_stock_key( "5Y Avg Yield", "max")
        max_stock_yield_to_filter_highest_value = max([max_stock_yield_to_filter, max_stock_yield_to_filter_5y_avg])
        yield_range_min, yield_range_max = st.slider(label="Select range of stock dividends yield to filter by",
                                                     max_value=min(max_stock_yield_to_filter_highest_value, 25.0),
                                                     key="dividend_yield_range", min_value=0.0,
                                                     value=(0.0, min(max_stock_yield_to_filter_highest_value, 25.0)),
                                                     help="Use this slider to filter stocks by dividend yield, which "
                                                          "is the percentage of the stock's current value paid back as "
                                                          "dividends. This slider will also filter by 5-year average "
                                                          "yield")

        # filter to only stocks with a DGR over the selected percentage% for 1,3,5 & 10 years
        max_stock_yield_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 1Y", "max")
        max_stock_yield_to_filter_3y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 3Y", "max")
        max_stock_yield_to_filter_5y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 5Y", "max")
        max_stock_yield_to_filter_10y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 10Y", "max")
        max_stock_yield_to_filter_highest_value = max([max_stock_yield_to_filter_1y_avg,
                                                       max_stock_yield_to_filter_3y_avg,
                                                       max_stock_yield_to_filter_5y_avg,
                                                       max_stock_yield_to_filter_10y_avg])
        min_stock_yield_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 1Y", "min")
        min_stock_yield_to_filter_3y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 3Y", "min")
        min_stock_yield_to_filter_5y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 5Y", "min")
        min_stock_yield_to_filter_10y_avg = mysql_connection.min_max_value_of_any_stock_key( "DGR 10Y", "min")
        min_stock_yield_to_filter_highest_value = min([min_stock_yield_to_filter_1y_avg,
                                                       min_stock_yield_to_filter_3y_avg,
                                                       min_stock_yield_to_filter_5y_avg,
                                                       min_stock_yield_to_filter_10y_avg])
        min_dgr = st.slider(min_value=max(min_stock_yield_to_filter_highest_value, -25.0),
                            max_value=min(max_stock_yield_to_filter_highest_value, 25.0),
                            key="min_dgr", value=0.0, label="Select minimum DGR % to display",
                            help="this will filter the DGR % (dividend growth rate - the percentage dividend "
                                 "increased) of 1,3,5 & 10 years (where applicable)")

        # filter to only stocks with a chowder number over the selected value
        max_chowder_number_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "Chowder Number",
                                                                             "max")
        chowder_number = st.slider(min_value=0, max_value=int(min(max_chowder_number_to_filter_1y_avg, 25.0)),
                                   key="min_chowder_number", value=0, label="Select minimum chowder number to display",
                                   help="Filters for stocks with a Chowder number of the given value or higher. "
                                        "Chowder number is a rule-based system used to identify dividend growth "
                                        "stocks with strong total return potential by combining dividend yield and "
                                        "dividend growth. A Chowder number of 12 or higher is generally considered a "
                                        "good value")

    with st.expander("Financial filtering options", expanded=True):

        # filter based on stock prices
        max_stock_price_to_filter = mysql_connection.min_max_value_of_any_stock_key( "Price", "max")
        price_range_min, price_range_max = st.slider(label="Select range of stock prices to filter by", min_value=1.0,
                                                     max_value=max_stock_price_to_filter, key="stock_price_range",
                                                     value=(1.0, max_stock_price_to_filter),
                                                     help="Select the minimum and maximum prices of stocks to display")

        # filter to only stocks with a fair value under the selected percentage
        max_fair_value_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "FV %", "max")
        min_fair_value_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "FV %", "min")
        fair_value = st.slider(min_value=int(max(min_fair_value_to_filter_1y_avg, -25.0)),
                               max_value=int(max(max_fair_value_to_filter_1y_avg, 0.0)),
                               key="max_fair_value", value=0, label="Select maximum fair value % to display",
                               help="This filter will only display stocks with a Fair Value Percentage (FV%) below "
                                    "the set FV% indicates how much the company stock is judged to cost compared to "
                                    "its actual worth")

        # filter to only stocks with a EPS over the selected value
        max_eps_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "EPS 1Y", "max")
        min_eps_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "EPS 1Y", "min")
        min_eps = st.slider(min_value=min_eps_to_filter_1y_avg, key="min_eps_number", value=0.0,
                            max_value=max_eps_to_filter_1y_avg,
                            label="Select minimum EPS growth over 1 year to display",
                            help="EPS stands for earning per share, how much a company earned for each share at the "
                                 "timeframe, this will filter to only companies with the given value has grown over "
                                 "the past year or higher")

        # filter to only stocks with a revenue over 1y over the selected value
        max_revenue_1y_avg_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "Revenue 1Y", "max")
        min_revenue_1y_avg_to_filter_1y_avg = mysql_connection.min_max_value_of_any_stock_key( "Revenue 1Y", "min")
        min_revenue = st.slider(min_value=min_revenue_1y_avg_to_filter_1y_avg, key="min_revenue_1y_avg", value=0.0,
                                max_value=max_revenue_1y_avg_to_filter_1y_avg,
                                label="Select minimum revenue growth over 1 year to display",
                                help="this will filter to only companies who's revenues have grown at or over the "
                                     "given value")

        # filter to only stocks with a NPM percentage over the selected value
        max_npm_to_filter = mysql_connection.min_max_value_of_any_stock_key( "NPM", "max")
        min_npm_to_filter = mysql_connection.min_max_value_of_any_stock_key( "NPM", "min")
        min_npm = st.slider(min_value=min_npm_to_filter, key="min_npm_number", value=0.0,
                            max_value=max_npm_to_filter, label="Select minimum NPM % to display",
                            help="NPM stands for net profit margin, calculated by dividing earnings after taxes by net "
                                 "revenue, and multiplying the total by 100%. The higher the ratio, the more cash the "
                                 "company has available to distribute to shareholders or invest in new opportunities")

        # filter to only stocks with a cf/share over the selected value
        max_cf_per_share_to_filter = mysql_connection.min_max_value_of_any_stock_key( "CF/Share", "max")
        min_cf_per_share_to_filter = mysql_connection.min_max_value_of_any_stock_key( "CF/Share", "min")
        min_cf_per_share = st.slider(min_value=min_cf_per_share_to_filter, key="min_cf_per_share_number", value=0.0,
                                     max_value=max_cf_per_share_to_filter, label="Select minimum cf/share to display",
                                     help="cf/share stands for cash flow per share,  the after-tax earnings plus "
                                          "depreciation on a per-share basis that functions as a measure of a firm's "
                                          "financial strength. Many financial analysts place more emphasis on cash "
                                          "flow per share than on earnings per share")

        # filter to only stocks with a ROE over the selected value
        max_roe_to_filter = mysql_connection.min_max_value_of_any_stock_key( "ROE", "max")
        min_roe_to_filter = mysql_connection.min_max_value_of_any_stock_key( "ROE", "min")
        min_roe = st.slider(min_value=min_roe_to_filter, key="min_roe_number", value=0.0,
                            max_value=max_roe_to_filter, label="Select minimum ROE to display",
                            help="ROE (return on equity) is equal to a fiscal year net income, divided by total "
                                 "equity, expressed as a percentage, this will filter to only companies who have an "
                                 "ROE over the given value")

        # filter based on P/E
        max_stock_pe_to_filter = mysql_connection.min_max_value_of_any_stock_key( "P/E", "max")
        min_stock_pe_to_filter = mysql_connection.min_max_value_of_any_stock_key( "P/E", "min")
        pe_range_min, pe_range_max = st.slider(label="Select range of stock to filter by it's P/E",
                                               max_value=min(max_stock_pe_to_filter, 100.0),
                                               key="dividend_pe_range", value=(0.0, 20.0),
                                               min_value=max(min_stock_pe_to_filter, -50.0),
                                               help="Use this slider to filter stocks by price to earnings ratio,"
                                                    " which is the  price of the stoc compared to it's earning, "
                                                    "negative values mean the company is losing money, a P/E "
                                                    "over 20 is generally considered expensive while while under"
                                                    "15 (but above 0) is considered cheap")

        # filter to only stocks with a p/bv under the selected value
        max_price_per_book_value_to_filter = mysql_connection.min_max_value_of_any_stock_key( "P/BV", "max")
        min_price_per_book_value_to_filter = mysql_connection.min_max_value_of_any_stock_key( "P/BV", "min")
        max_price_per_book_value = st.slider(min_value=min_price_per_book_value_to_filter,
                                             key="max_price_per_book_value_number",
                                             value=max_price_per_book_value_to_filter,
                                             max_value=max_price_per_book_value_to_filter,
                                             label="Select maximum P/BV to display",
                                             help="P/BV stands for price to book value, the ratio of the market value "
                                                  "of a company's shares (share price) over its book value of equity. "
                                                  "The book value of equity, in turn, is the value of a company's "
                                                  "assets expressed on the balance sheet, the lower the value "
                                                  "usually the better the cost to value ratio is")

        # filter to only stocks with a Debt/Capital under the selected value
        max_debt_per_capital_to_filter = mysql_connection.min_max_value_of_any_stock_key( "Debt/Capital", "max")
        max_debt_per_capital_value = st.slider(min_value=0.0, key="max_debt_per_capital_value",
                                               value=0.5, max_value=min(5.0, max_debt_per_capital_to_filter),
                                               label="Select maximum Debt/Capital to display",
                                               help="the debt to capital ratio, how much the company barrowed devided "
                                                    "to how much it has, the lower the value to less the company owes "
                                                    "compared to the assets is has, investors tend to like it to stay "
                                                    "under 0.6 (6o%) but some go up to 0.8 (80%) or higher as debt can "
                                                    "mean also a growing company which uses the debt to increase it's "
                                                    "size")

    with st.expander("Exclusion filtering options", expanded=True):

        # exclude stocks by symbols
        excluded_symbols = st.multiselect(label='Stock symbols to exclude', key="excluded_symbols",
                                          options=mysql_connection.list_values_of_key_in_db("Symbol"),
                                          help="exclude specific stocks from your search")

        # exclude stocks by sector
        excluded_sectors = st.multiselect(label='Sector to exclude', key="excluded_sectors",
                                          options=mysql_connection.list_values_of_key_in_db("Sector"),
                                          help="exclude whole sectors from your search")

        # exclude stocks by industry
        excluded_industries = st.multiselect(label='Industry to exclude', key="excluded_industries",
                                          options=mysql_connection.list_values_of_key_in_db("Industry"),
                                          help="exclude whole industries from your search")

# TODO - move to centralized db that is updated via cron

# TODO - add line of when was the last data pull from finviz (datetime is created when function runs, just
# need to print it on the ui remains

# TODO - unit tests all full coverage and readme badge

# TODO - real DNS domain - current test domain is https://divifilter.naor.eu.org/

# TODO - readme

# TODO - github link to website

# TODO - publicize & monetize somehow?

# TODO - some user analytics - google analytics in streamlit is too hacky right now

st.divider()

st.dataframe(radar_dict_to_table(radar_dict_filtered), use_container_width=True)

st.info("""
The information provided by Divifilter is for informational purposes only and should not be considered as financial 
advice. The information provided by Divifilter is not intended to provide investment advice or recommendations. Users 
are solely responsible for their own investment decisions.

Divifilter is not affiliated with any financial institution or investment company. The accuracy of the data provided 
by Divifilter cannot be guaranteed and is subject to change without notice.

By using Divifilter you acknowledge that you have read and understand this legal notification. You agree to use the 
information provided by Divifilter at your own risk and agree to hold harmless the creators of Divifilter from any and 
all claims or damages arising from your use of Divifilter.
""", icon="ℹ️")

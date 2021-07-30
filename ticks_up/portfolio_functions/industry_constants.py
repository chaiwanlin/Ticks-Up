# Categories

# Overview
OVERVIEW = "Overview"

LAST = "close" , 1

CHG = "change", 2

CHG_ABS = "change_abs", 3

RATING = "Recommend.All", 4

VOL = "volume" , 5

MKT_CAP = "market_cap_basic", 6

PE_TTM = "price_earnings_ttm", 7

EPS_TTM = "earnings_per_share_basic_ttm", 8

EMPLY = "number_of_employees", 9

# Performance
PERFORMANCE = "Performance"

ONE_M_CHG = "change.1", 1

FIVE_M_CHG = "change.5", 2

FIFTEEN_M_CHG = "change.15", 3

ONE_H_CHG = "change.60", 4

FOUR_H_CHG = "change.240", 5

<<<<<<< HEAD
CHG_PERF = CHG, 6
=======
# CHG
>>>>>>> e2c0993c107619e2a5a16be28f02483f82c31829

ONE_W_CHG = "change.1W", 7

ONE_M_CHG = "change.1M", 8

THREE_M_CHG = "Perf.3M", 9

SIX_M_CHG = "Perf.6M", 10

YTD = "Perf.YTD", 11

YEARLY = "Perf.Y", 12 # FY

ONE_Y_BETA = "beta_1_year", 13

VOL = "Volatility.D", 14

# Valuation
VALUATION = "Valuation"

MKTCAP_VAL = MKT_CAP, 2

PE_TTM_VAL = PE_TTM, 3

P_REV = "price_revenue_ttm", 4

EPS_TTM = "earnings_per_share_basic_ttm", 5

EPS_DIL_FY = "last_annual_eps", 6

EV_EBITDA = "enterprise_value_ebitda_ttm", 7

EV = "enterprise_value_fq", 8

SHARES = "total_shares_outstanding_fundamental", 9

# Dividends
DIVIDENDS = "Dividends"

DIV_YIELD = "dividend_yield_recent", 2

DIV_PAID = "dividends_paid", 3

DIV_SHARE = "dps_common_stock_prim_issue_fy", 4

# Margins
MARGINS = "Margins"

GROSS_MARGIN = "gross_margin", 1

OPERATING_MARGIN = "operating_margin", 2

PRETAX_MARGIN = "pre_tax_margin", 3

NET_MARGIN = "after_tax_margin", 4

# Income Statement
INCOME_STMT = "Income Statement"

EPS_FY = "basic_eps_net_income", 1

EPS_TTM_INC  = EPS_TTM, 2

EPS_DIL_TTM = "earnings_per_share_diluted_ttm", 3

EBITDA = "ebitda", 4

GROSS_PROFIT_MRQ = "gross_profit_fq", 5

GROSS_PROFIT_FY = "gross_profit", 6

REVENUE = "total_revenue", 7

EPS_DIL_FY_INC = EPS_DIL_FY, 8

ANNUAL_REV = "last_annual_revenue", 9

INCOME = "net_income", 10

# Balance Sheet
BALANCE_SHT = "Balance Sheet"

CURR_RATIO = "current_ratio", 1

DEBT_EQUITY = "debt_to_equity", 2

NET_DEBT = "net_debt", 3

QUICK_RATIO = "quick_ratio", 4

ASSET = "total_assets", 5

DEBT = "total_debt", 6

CURR_ASSET = "total_current_assets", 7

# Oscillators
OSC = "Oscillators"

OSC_RATING = "Recommend.Other", 1

# Trend-Following
TREND = "Trend-Following"

MOV_AVG_RATING = "Recommend.MA", 1

CATEGORIES = {
    "Overview" : OVERVIEW,
    "Performance" : PERFORMANCE,
    "Valuation" : VALUATION,
    "Dividends" : DIVIDENDS,
    "Margins" : MARGINS,
    "Income Statement" : INCOME_STMT,
    "Balance Sheet" : BALANCE_SHT,
    "Oscillators" : OSC,
    "Price Trend" : TREND
}

OVERVIEW_CHOICES = {
    "Last Price" : LAST,
    "Change %" : CHG,
    "Change" : CHG_ABS,
    "Rating" : RATING,
    "Volume" : VOL,
    "Market Cap" : MKT_CAP,
    "P/E (TTM)" : PE_TTM,
    "EPS (TTM)" : EPS_TTM,
    "Number of employees" : EMPLY
}

PERFORMANCE_CHOICES = {
    "1M Change %" : ONE_M_CHG,
    "5M Change %" : FIVE_M_CHG,
    "15M Change %" : FIFTEEN_M_CHG,
    "1H Change %" : ONE_H_CHG,
    "4H Change %" : FOUR_H_CHG,
    "Change %" : CHG_PERF,
    "1W Change" : ONE_W_CHG,
    "1M Change" : ONE_M_CHG,
    "3M Change" : THREE_M_CHG,
    "6M Change" : SIX_M_CHG,
    "Year to Date": YTD,
    "Yearly Performance" : YEARLY,
    "One Year Beta" : ONE_Y_BETA,
    "Volatility" : VOL
}
<<<<<<< HEAD
# valuation
{
    "Market Cap" : MKTCAP_VAL,
    "P/E (TTM)" : PE_TTM_VAL,
=======

VALUATION_CHOICES = {
    "Market Cap" : MKT_CAP,
    "P/E (TTM)" : PE_TTM,
>>>>>>> e2c0993c107619e2a5a16be28f02483f82c31829
    "Price/Revenue" : P_REV,
    "EPS (TTM)" : EPS_TTM,
    "EPS Diluted (FY)" : EPS_DIL_FY,
    "EV/EBITDA" : EV_EBITDA,
    "Enterprise Value" : EV,
    "Shares Outstanding" : SHARES
}

DIVIDEND_CHOICES = {
    "Dividend Yield %" : DIV_YIELD,
    "Dividend Paid" : DIV_PAID,
    "Dividend Per Share" : DIV_SHARE
}

MARGIN_CHOICES = {
    "Gross Margin" : GROSS_MARGIN,
    "Operating Margin" : OPERATING_MARGIN,
    "Pretax Margin" : PRETAX_MARGIN,
    "Net_margin" : NET_MARGIN
}

INCOME_STMT_CHOICES = {
    "EPS (FY)" : EPS_FY,
    "EPS (TTM)" : EPS_TTM_INC,
    "EPS Diluted (TTM)" : EPS_DIL_TTM,
    "EBITDA" : EBITDA,
    "Gross Profit (MRQ)" : GROSS_PROFIT_MRQ,
    "Gross Profit (FY)" : GROSS_PROFIT_FY,
    "Revenue" : REVENUE,
    "EPS Diltuted (FY)" : EPS_DIL_FY_INC,
    "Annual Revenue" : ANNUAL_REV,
    "Annual Income" : INCOME
}

<<<<<<< HEAD
# Balance Sheet
{

=======
BALANCE_SHT_CHOICES = {
>>>>>>> e2c0993c107619e2a5a16be28f02483f82c31829
    "Current Ratio" : CURR_RATIO,
    "Debt/Equity Ratio" : DEBT_EQUITY,
    "Net Debt" : NET_DEBT,
    "Quick Ratio" : QUICK_RATIO,
    "Total Asset" : ASSET,
    "Total Debt" : DEBT,
    "Total Current Asset" : CURR_ASSET
}

# OSCILLATOR_CHOICES = {
#     "Oscillator Rating" : OSC_RATING
# }
#
# TREND_CHOICES = {
#     "Moving Average Rating" : MOV_AVG_RATING
# }

CATEGORIES_INDICATORS_DICT = {
    OVERVIEW : OVERVIEW_CHOICES,
    PERFORMANCE : PERFORMANCE_CHOICES,
    VALUATION : VALUATION_CHOICES,
    DIVIDENDS : DIVIDEND_CHOICES,
    MARGINS : MARGIN_CHOICES,
    INCOME_STMT : INCOME_STMT_CHOICES,
    BALANCE_SHT : BALANCE_SHT_CHOICES,
    # OSC : OSCILLATOR_CHOICES,
    # TREND : TREND_CHOICES,
}

LIST_OF_INDICATORS_DICT_BY_CAT = [
    OVERVIEW_CHOICES,
    PERFORMANCE_CHOICES,
    VALUATION_CHOICES,
    DIVIDEND_CHOICES,
    MARGIN_CHOICES,
    INCOME_STMT_CHOICES,
    BALANCE_SHT_CHOICES,
    # OSCILLATOR_CHOICES,
    # TREND_CHOICES,
]

LIST_OF_INDICATORS = []
for dic in LIST_OF_INDICATORS_DICT_BY_CAT:
    for key, val in dic.items():
        LIST_OF_INDICATORS.append((val, key))
import time 
import json
import urllib.request
import datetime
import math
from hedge.spread import collar
from instruments.option import Put, Call

def historical_volatility(ticker):
    # no reliable way to get data :( 
    # probably will do alot of the main computation in stock Class
    return None

def volatility_skew(ticker):
    # math still abit fucky :(
    # some time IV on yahoo fiancnce broken also :(
    return None

def get_iv(ticker, days):
    call = Call(ticker).get_nearest_day(days).aggregated_iv()
    put = Put(ticker).get_nearest_day(days).aggregated_iv()
    ratio = put_call_ratio(ticker, days)

    print(put[0])
    call_iv = call[0] * (1 / (ratio + 1))
    put_iv = put[0] * (ratio / (ratio + 1))

    return range_to_date(call_iv + put_iv, days)

def put_call_ratio(ticker, days):
    return Put(ticker).get_nearest_day(days).get_open_interest_count() / Call(ticker).get_nearest_day(days).get_open_interest_count()

def range_to_date(IV, stock_price, days = None):
    if not days:
        return IV
    else:
        return stock_price * IV * math.sqrt(days.days / 365)

def hedge_stock(ticker, entry_price, breakeven_point, risk, days, capped = True, target_price = None):
    result = Put(ticker).get_nearest_day(days).get_hedge_stike(risk, entry_price)

    if capped:
        return [result, collar(ticker, days, entry_price, breakeven_point, target_price, risk)]
    else:
        return result

# print(hedge_stock("aapl", 135, 10, 140, 30, False, 150))
# print(get_iv("aapl", 30))
# print(range_to_date(datetime.date(2021, 6,20), 0.2, 100))


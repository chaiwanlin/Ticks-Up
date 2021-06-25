import time 
import json
import urllib.request
import datetime
import math
from hedge.spread import collar
from instruments.option import Put, Call

def historical_volatility():
    return None

def volatility_skew():
    return None

def put_call_ratio(ticker, days):
    return Put(ticker).get_nearest_day(days).get_open_interest_count() / Call(ticker).get_nearest_day(days).get_open_interest_count()

def range_to_date(date, IV, stock_price, days = None):
    if not days and date:
        days = date - datetime.date.today()
    return stock_price * IV * math.sqrt(days.days / 365)

def hedge_stock(ticker, entry, risk, break_point, days, capped = True, target_price = None):
    risk_amount = (1.0 - risk) * entry
    break_amount = (1.0 - break_point) * entry + entry
    result = Put(ticker).get_nearest_day(days).get_hedge_stike(risk_amount, entry, break_amount)

    if not capped:
        return [result, collar(ticker, days, entry, break_amount, target_price, risk_amount)]

# print(hedge_stock("aapl", 135, 0.2, 0.1, 30, False, 150))
print(put_call_ratio("aapl", 0))

# print(range_to_date(datetime.date(2021, 6,20), 0.2, 100))
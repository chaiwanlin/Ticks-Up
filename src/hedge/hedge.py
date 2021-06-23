import time 
import json
import urllib.request
import datetime
import math
from instruments.option import Put

def range_to_date(date, IV, stock_price, days = None):
    if not days and date:
        days = date - datetime.date.today()
    return stock_price * IV * math.sqrt(days.days / 365)

def hedge_stock(stock, entry, risk, break_point, days, uncapped = True):
    risk_amount = (1.0 - risk) * entry
    break_amount = (1.0 - break_point) * entry
    return Put(stock).get_nearest_day(days).get_hedge_stike(risk_amount, entry, break_amount)

    # if not uncapped:
    #     return None

print(hedge_stock("aapl", 135, 0.2, 0.1, 30))



# print(range_to_date(datetime.date(2021, 6,20), 0.2, 100))
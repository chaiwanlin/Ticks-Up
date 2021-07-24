import time 
import json
import urllib.request as rq
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from portfolio.portfolio_constants import PATH
import requests
import datetime
import math
from spread import collar
from ticks_up.hedge_instruments.option import Put, Call

def historical_volatility(ticker):
    # driver = webdriver.Chrome(PATH)
    # driver.get(f"https://www.optionseducation.org/toolsoptionquotes/historical-and-implied-volatility")
    # WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located((By.XPATH, '//input[name="ticker"]'))
    #     ).click().send_keys("ads")
    return None

def volatility_skew(ticker, days = 30):
    calls = Call(ticker).get_nearest_day(days).get_25_delta()
    puts = Put(ticker).get_nearest_day(days).get_25_delta()
    return puts - calls

def get_iv(ticker, days):
    call = Call(ticker).get_nearest_day(days).aggregated_iv()
    put = Put(ticker).get_nearest_day(days).aggregated_iv()
    ratio = put_call_ratio(ticker, days)

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

def hedge_stock(ticker, entry_price, risk, breakeven_point, days, capped = True, target_price = None):
    result = Put(ticker).get_nearest_day(days).get_hedge_stike(risk, entry_price)
    if capped:
        return [result, collar(ticker, days, entry_price, breakeven_point, target_price, risk)]
    else:
        return result

# print(hedge_stock("aapl", 135, 10, 140, 30, False, 150))
# print(historical_volatility("AAPL"))
# print(get_iv("aapl", 30))
# print(range_to_date(datetime.date(2021, 6,20), 0.2, 100))


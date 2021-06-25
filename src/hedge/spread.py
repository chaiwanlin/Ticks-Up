from utility.search import bin_search_closest
from instruments.instrument import Instrument
from instruments.option import Call, Put
from instruments.stock import Stock

# incoperate open interest? alot of outlier data 

def bull_credit_spread(ticker, days, lower_bound, target_price, risk):
    puts = Put(ticker).get_nearest_day(days)
    strikes = puts.get_strikes()
    closest_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_put = puts.get_option_for_strike(closest_price).get_price()
    result = puts.get_strike_for_breakeven_credit(lower_bound, closest_price, short_put, risk)

    return result

def bull_debit_spread(ticker, days, lower_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_call = calls.get_option_for_strike(closest_price).get_price()
    result = calls.get_strike_for_breakeven_debit(lower_bound,risk, short_call)

    return result

# risk per stock
def bear_credit_spread(ticker, days, upper_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_call = calls.get_option_for_strike(closest_price).get_price()
    result = calls.get_strike_for_breakeven_credit(upper_bound, closest_price, short_call, risk)

    return result

def bear_debit_spread(ticker, days, upper_bound, target_price, risk):
    puts = Put(ticker).get_nearest_day(days)
    strikes = puts.get_strikes()
    closest_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_put = puts.get_option_for_strike(closest_price).get_price()
    result = puts.get_strike_for_breakeven_debit(upper_bound, risk, short_put)

    return result

def collar(ticker, days, entry_price, lower_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_price = strikes[bin_search_closest(target_price, strikes)[0]]

    long_call = calls.get_option_for_strike(closest_price).get_price()

    return Put(ticker).get_nearest_day(days).get_strike_for_breakeven_collar(entry_price, lower_bound, closest_price, long_call, risk)



# print(bull_credit_spread("aapl", 58, 140, 160, 20))
print(collar("aapl", 30, 120, 130, 150, 20))
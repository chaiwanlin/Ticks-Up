from utility.search import bin_search_closest
from instruments.instrument import Instrument
from instruments.option import Call, Put
from instruments.stock import Stock
from portfolio.portfolio_constants import BEAR, BULL, STRADDLE, NEUTRAL

# incoperate open interest? alot of outlier data 

def bull_credit_spread(ticker, days, lower_bound, target_price, risk):
    puts = Put(ticker).get_nearest_day(days)
    strikes = puts.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_put_premium = puts.get_option_for_strike(closest_target_price).get_price()
    result = puts.get_strike_for_breakeven_credit(lower_bound, closest_target_price, short_put_premium, risk)

    return result

def bull_debit_spread(ticker, days, lower_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_call_premium = calls.get_option_for_strike(closest_target_price).get_price()
    result = calls.get_strike_for_breakeven_debit(lower_bound, closest_target_price, short_call_premium,  risk)

    return result

def bear_credit_spread(ticker, days, upper_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_call_premium = calls.get_option_for_strike(closest_target_price).get_price()
    result = calls.get_strike_for_breakeven_credit(upper_bound, closest_target_price, short_call_premium, risk)

    return result

def bear_debit_spread(ticker, days, upper_bound, target_price, risk):
    puts = Put(ticker).get_nearest_day(days)
    strikes = puts.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    short_put_premium = puts.get_option_for_strike(closest_target_price).get_price()
    result = puts.get_strike_for_breakeven_debit(upper_bound, closest_target_price, short_put_premium, risk)

    return result

def collar(ticker, days, entry_price, lower_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    long_call_premium = calls.get_option_for_strike(closest_target_price).get_price()
    result = Put(ticker).get_nearest_day(days).get_strike_for_breakeven_collar(entry_price, lower_bound, closest_target_price, long_call_premium, risk)

    return result


# def adjust_bull_spread(ticker, net_premium, lower_bound, upper_bound, outlook, new_target_price, risk):
#     # debit spread
#     if net_premium < 0:
#         calls = Call(ticker)
#         # roll short leg down/ roll long leg back(-ve breakeven value)/short call 
#         if outlook == BEAR:
#             short_call = calls.get_option_for_strike(upper_bound).get_price()
            
#             calls.get_strike_for_breakeven_debit()

#         # rikk out long leg
#         elif outlook == BULL:

#         # roll back short leg
#         elif outlook == NEUTRAL:
        
            

#     # credit spread
#     else:
#         puts = Put(ticker)
#         if outlook == BEAR:

#         # 
#         elif outlook == BULL:

#         # roll back short leg
#         elif outlook == NEUTRAL:
#     return 0

# def adjust_bull_spread_to_condor(ticker, net_premium, lower_bound, upper_bound):
#     # debit spread
#     if net_premium < 0:
#         calls = Call(ticker)
#     # credit spread
#     else:
#         puts = Put(ticker)
#     return 0
        



print(bull_credit_spread("aapl", 30, 140, 150, 20))
# print(bear_credit_spread("aapl", 30, 130, 120, 80))
# print(collar("aapl", 30, 120, 130, 150, 20))
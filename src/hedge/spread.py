from utility.search import bin_search_closest
from instruments.instrument import Instrument
from instruments.option import Call, Put
from instruments.stock import Stock
from portfolio.portfolio_constants import BEAR, BULL, STRADDLE, NEUTRAL, OTM, ATM, ITM

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

def adjust_bull_spread(ticker, day, month, year, net_premium, short_leg, long_leg, moneyness, outlook, target_price, risk):
    # debit spread
    if net_premium < 0:
        calls = Call(ticker, day, month, year)
        strikes = calls.get_strikes()

        # roll short leg down/ roll long leg back(-ve breakeven value)/short call 
        if outlook == BEAR:
            if moneyness == ITM:
                #just close it lol
                return {
                    "close trade" : "close trade"
                }

            if moneyness == OTM:
                # roll short leg down even to bear spread
                closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]
                old_short_call = calls.get_option_for_strike(short_leg).get_price()
                new_short_call = calls.get_option_for_strike(closest_target_price).get_price()               
                net_cost = new_short_call - old_short_call

                # short call
                naked_short_call = calls.get_option_nearest_premium(short_leg, old_short_call)
                

                # iron butterfly
                diff = short_leg - long_leg

                long_put_premium = long_leg
                long_put_price = calls.get_option_for_strike(long_put_premium).get_price()

                short_put_premium = short_leg - diff
                short_put_price = calls.get_option_for_strike(short_put_premium).get_price()

                max_loss = 

                # calender

                return{
                    "Roll short leg down": {
                        "net_cost" : net_cost,

                    },
                    "Naked short call" : {
                        "net_credit" : naked_short_call["Premium"],
                        "Short call Strike" : naked_short_call["Strike"]
                    },
                    "Iron Butterfly" : {

                        "strike_price" : max_gain_strike,
                        "strike_premium" : max_gain_premium,
                        "net_value_at_breakeven" : max_gain_net_value,
                        "max_profit" : max_gain_profit,
                        "breakeven" : max_gain_breakeven,
                        "max_loss" : max_gain_loss

                    }
                    
                }

        # rikk out long leg
        elif outlook == BULL:
            if moneyness == ITM:
                #just close it lol
                #roll out short leg(debit)
                return "close trade" 

            if moneyness == OTM:
                # roll out expiry
                # calender

    # credit spread
    else:
        puts = Put(ticker)
        if outlook == BEAR:
            if moneyness == ITM:
                #just close it lol
                return "close trade" 

            if moneyness == OTM:
                # roll short leg down, short call, iron butterfllllllllllllllllllllllllllllllllllllllllllllllllllllly
                short_call = calls.get_option_for_strike().get_price()               
                calls.get_strike_for_breakeven_debit()

        # rikk out long leg
        elif outlook == BULL:
            if moneyness == ITM:
                #just close it lol
                #roll out short leg(debit)
                return "close trade" 

            if moneyness == OTM:
                # roll out expiry        if outlook == BEAR:


    return 0

# def adjust_bull_spread_to_condor(ticker, net_premium, lower_bound, upper_bound):
#     # debit spread
#     if net_premium < 0:
#         calls = Call(ticker)
#     # credit spread
#     else:
#         puts = Put(ticker)
#     return 0

def adjust_collar(ticker, net_premium, lower_bound, upper_bound, outlook, new_target_price, risk):
    # roll out, adj challenged leg
        
def adjust_condor():


# print(bull_debit_spread("aapl", 30, 140, 150, 30))
# print(bear_credit_spread("aapl", 30, 130, 120, 80))
# print(collar("aapl", 30, 120, 130, 150, 20))
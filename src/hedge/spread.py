import math
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

# target price to be treated more like rebound price/highest price it will ever go in their mind
def adjust_bull_spread(ticker, day, month, year, net_premium, short_leg_strike, long_leg_strike, moneyness, outlook, target_price, risk):
    puts = Put(ticker, day, month, year)
    put_strikes = puts.get_strikes
    
    calls = Call(ticker, day, month, year)
    call_strikes = calls.get_strikes()

    # debit spread
    if net_premium < 0:
        # roll short leg down/ roll long leg back(-ve breakeven value)/short call 
        if outlook == BEAR:
            if moneyness == ITM:
                #just close it lol
                return {
                    "Close trade" : "close trade"
                }

            if moneyness == OTM:
                # roll short leg down even to bear spread
                new_short_call_price = call_strikes[bin_search_closest(target_price, call_strikes)[0]]
                old_short_call_premium = calls.get_option_for_strike(short_leg_strike).get_price()
                new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()     

                net_credit = new_short_call_premium - old_short_call_premium

                # still debit call spread
                if new_short_call_price >= long_leg_strike:                    
                    new_premium = net_premium - net_credit
                    roll_down_max_profit = new_short_call_premium - long_leg_strike - new_premium
                    roll_down_breakeven = long_leg_strike + new_premium
                    roll_down_max_loss = new_premium
                else:
                    new_premium = net_credit - net_premium
                    roll_down_max_profit = new_premium
                    roll_down_breakeven = new_short_call_price + new_premium
                    roll_down_max_loss = long_leg_strike - new_short_call_premium - new_premium


                # short call
                naked_short_call = calls.get_option_nearest_premium(short_leg_strike, old_short_call_premium)

                naked_call_new_premium = net_premium - naked_short_call["Premium"]
                naked_call_max_profit = short_leg_strike - long_leg_strike - naked_call_new_premium
                naked_call_breakeven = long_leg_strike + naked_call_new_premium
                naked_call_max_bear_loss = naked_call_new_premium
                naked_call_max_bull_loss = math.inf                

                # iron butterfly
                diff = short_leg_strike - long_leg_strike

                long_put_strike_price = long_leg_strike
                long_put_premium = puts.get_option_for_strike(long_put_strike_price).get_price()

                short_put_strike_price = short_leg_strike - diff
                short_put_premium = puts.get_option_for_strike(short_put_strike_price).get_price()

                butterfly_new_premium = long_put_premium - short_put_premium

                butterfly_max_profit = diff * 2 - net_premium - butterfly_new_premium
                butterfly_breakeven_bear = long_put_strike_price - butterfly_new_premium
                butterfly_breakeven_bull = long_leg_strike + butterfly_new_premium

                # calender

                return {
                    "Roll short leg down": {
                        "net_credit" : net_credit,
                        "strike_price" : new_short_call_price,
                        "strike_premium" : new_short_call_premium,
                        "max_profit" : roll_down_max_profit,
                        "breakeven" : roll_down_breakeven,
                        "max_loss" : roll_down_max_loss
                    },
                    "Naked short call" : {
                        "net_credit" : naked_short_call["Premium"],
                        "strike_price" : naked_short_call["Strike"],
                        "strike_premium" : naked_short_call["Premium"],
                        "max_profit" : naked_call_max_profit,
                        "breakeven" : naked_call_breakeven,
                        "max_loss_bear" : naked_call_max_bear_loss,
                        "max_loss_bull" : naked_call_max_bull_loss
                    },
                    "Iron Butterfly" : {                                       
                        "long_put_strike_price" : new_short_call_price,
                        "long_put_strike_premium" : long_put_premium,
                        "short_put_strike_price" : short_put_strike_price,
                        "short_put_strike_premium" : short_put_premium,

                        "net_debit" : butterfly_new_premium,
                        "max_profit" : butterfly_max_profit,
                        "breakeven_bear" : butterfly_breakeven_bear,
                        "breakeven_bull" : butterfly_breakeven_bull,
                        "max_loss" : butterfly_new_premium
                    }
                }

        # roll out long leg
        elif outlook == BULL:
            if moneyness == ITM:
                #just close it lol
                #roll out short leg(debit)
                new_short_call_price = call_strikes[bin_search_closest(target_price, call_strikes)[0]]
                old_short_call_premium = calls.get_option_for_strike(short_leg_strike).get_price()
                new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()     

                net_debit = old_short_call_premium - new_short_call_premium

                new_premium = net_premium + net_debit
                roll_up_max_profit = new_short_call_premium - long_leg_strike - new_premium
                roll_up_breakeven = long_leg_strike + new_premium
                roll_up_max_loss = new_premium
                return {
                    "Close trade" : "close trade",
                    "Roll short leg up" : {
                        "net_debit" : net_debit,
                        "strike_price" : new_short_call_price,
                        "strike_premium" : new_short_call_premium,
                        "max_profit" : roll_up_max_profit,
                        "breakeven" : roll_up_breakeven,
                        "max_loss" : roll_up_max_loss
                    }
                }

            if moneyness == OTM:
                # roll out expiry
                later_calls = calls.get_nearest_day(28)
                
                old_long_call_premium = later_calls.get_option_for_strike(long_leg_strike).get_price()
                old_short_call_premium = later_calls.get_option_for_strike(short_leg_strike).get_price()
                cost_to_close = old_long_call_premium - old_short_call_premium  

                new_long_call_premium = later_calls.get_option_for_strike(long_leg_strike).get_price()
                new_short_call_premium = later_calls.get_option_for_strike(short_leg_strike).get_price()
                cost_to_open = new_long_call_premium - new_short_call_premium

                net_debit = cost_to_open - cost_to_close
                new_premium = net_premium + net_debit

                roll_out_max_profit = short_leg_strike - long_leg_strike - new_premium
                roll_out_breakeven = long_leg_strike + new_premium

                # calender
                return {
                    "Roll out expiry": {
                        "net_debit" : net_debit,
                        "new_long_call_premium" : new_long_call_premium,
                        "new_short_call_premium" : new_short_call_premium,
                        "max_profit" : roll_out_max_profit,
                        "breakeven" : roll_out_breakeven,
                        "max_loss" : new_premium
                    }
                }
    # credit spread
    else:
        if outlook == BEAR:
            diff = short_leg_strike - long_leg_strike

            # iron butterfly
            if target_price < short_leg_strike: 
                short_call_strike_price = short_leg_strike
                short_call_premium = calls.get_option_for_strike(short_call_strike_price).get_price()

                long_call_strike_price = short_leg_strike + diff
                long_call_premium = calls.get_option_for_strike(long_call_strike_price).get_price()                   
            else:
                short_call_strike_price = call_strikes[bin_search_closest(target_price, call_strikes)[0]]
                short_call_premium = calls.get_option_for_strike(short_call_strike_price).get_price()

                long_call_strike_price = short_call_strike_price + diff
                long_call_premium = calls.get_option_for_strike(long_call_strike_price).get_price()

            butterfly_credit = short_call_premium - long_call_premium
            
            butterfly_new_credit = net_premium + butterfly_credit
            butterfly_breakeven_bear = short_call_strike_price - butterfly_new_credit
            butterfly_breakeven_bull = short_leg_strike + butterfly_new_credit
            butterfly_max_loss = diff - butterfly_new_credit
            
            return {
                # if proffitable
                "Close trade" : "Close Trade",
                "Iron Butterfly" : {                                       
                    "long_call_strike_price" : long_call_strike_price,
                    "long_call_premium" : long_call_premium,
                    "short_call_strike_price" : short_call_strike_price,
                    "short_call_premium" : short_call_premium,

                    "net_credit" : butterfly_credit,
                    "max_profit" : butterfly_new_credit,
                    "breakeven_bear" : butterfly_breakeven_bear,
                    "breakeven_bull" : butterfly_breakeven_bull,
                    "max_loss" : butterfly_max_loss
                }
            }
        elif outlook == BULL:
            if moneyness == ITM:
                # wait lol/roll expiry   
                later_puts = puts.get_nearest_day(28)
                
                old_long_put_premium = later_puts.get_option_for_strike(long_leg_strike).get_price()
                old_short_put_premium = later_puts.get_option_for_strike(short_leg_strike).get_price()
                cost_to_close = old_short_put_premium - old_long_put_premium

                new_long_put_premium = later_puts.get_option_for_strike(long_leg_strike).get_price()
                new_short_put_premium = later_puts.get_option_for_strike(short_leg_strike).get_price()
                cost_to_open = new_short_put_premium - new_long_put_premium

                net_cost = cost_to_close - cost_to_open
                new_credit = net_premium - net_cost

                roll_out_max_loss = short_leg_strike - long_leg_strike - new_credit
                roll_out_breakeven = long_leg_strike + new_credit

                return {
                    "Wait" : "Wait",
                    "Roll out expiry": {
                        "net_cost" : net_cost,
                        "new_long_put_premium" : new_long_put_premium,
                        "new_short_put_premium" : new_short_put_premium,
                        "max_profit" : new_credit,
                        "breakeven" : roll_out_breakeven,
                        "max_loss" : roll_out_max_loss
                    }
                }

            if moneyness == OTM:
            # just close it lol or wait idiot 
                return {
                    "Close trade" : "Close Trade",
                    "Wait" : "Wait"
                }

def adjust_bear_spread(ticker, day, month, year, net_premium, short_leg_strike, long_leg_strike, moneyness, outlook, target_price, risk):
    puts = Put(ticker, day, month, year)
    put_strikes = puts.get_strikes
    
    calls = Call(ticker, day, month, year)
    call_strikes = calls.get_strikes()

    # debit spread
    if net_premium < 0:
        # roll short leg down/ roll long leg back(-ve breakeven value)/short call 
        if outlook == BULL:
            if moneyness == ITM:
                #just close it lol
                return {
                    "Close trade" : "close trade"
                }

            if moneyness == OTM:
                # roll short leg up even to bull spread
                new_short_put_price = put_strikes[bin_search_closest(target_price, put_strikes)[0]]
                old_short_put_premium = puts.get_option_for_strike(short_leg_strike).get_price()
                new_short_put_premium = puts.get_option_for_strike(new_short_put_price).get_price()     

                net_credit = new_short_put_premium - old_short_put_premium

                # still debit call spread
                if new_short_put_price <= long_leg_strike:

                    new_premium = net_premium - net_credit

                    roll_up_max_profit =  long_leg_strike - new_short_put_price - new_premium
                    roll_up_breakeven = long_leg_strike - new_premium
                    roll_up_max_loss = new_premium
                else:

                    new_premium = net_credit - net_premium

                    roll_up_max_profit = new_premium
                    roll_up_breakeven = new_short_put_price - new_premium
                    roll_up_max_loss = new_short_put_price - long_leg_strike - new_premium

                # short call
                naked_short_put = puts.get_option_nearest_premium(short_leg_strike, old_short_put_premium)

                naked_put_new_premium = net_premium - naked_short_put["Premium"]
                naked_put_max_profit =  long_leg_strike - short_leg_strike - naked_put_new_premium
                naked_put_breakeven = long_leg_strike - naked_put_new_premium
                naked_put_max_bear_loss = math.inf
                naked_put_max_bull_loss = naked_put_new_premium            

                # iron butterfly
                diff = long_leg_strike - short_leg_strike

                long_call_strike_price = long_leg_strike
                long_call_premium = puts.get_option_for_strike(long_call_strike_price).get_price()

                short_call_strike_price = short_leg_strike - diff
                short_call_premium = puts.get_option_for_strike(short_call_strike_price).get_price()

                butterfly_new_premium = long_call_premium - short_call_premium

                butterfly_max_profit = diff * 2 - net_premium - butterfly_new_premium
                butterfly_breakeven_bear = long_leg_strike - butterfly_new_premium
                butterfly_breakeven_bull = long_leg_strike + butterfly_new_premium

                # calender

                return {
                    "Roll short leg up": {
                        "net_credit" : net_credit,
                        "strike_price" : new_short_put_price,
                        "strike_premium" : new_short_put_premium,
                        "max_profit" : roll_up_max_profit,
                        "breakeven" : roll_up_breakeven,
                        "max_loss" : roll_up_max_loss
                    },
                    "Naked short put" : {
                        "net_credit" : naked_short_put["Premium"],
                        "strike_price" : naked_short_put["Strike"],
                        "strike_premium" : naked_short_put["Premium"],
                        "max_profit" : naked_put_max_profit,
                        "breakeven" : naked_put_breakeven,
                        "max_loss_bear" : naked_put_max_bear_loss,
                        "max_loss_bull" : naked_put_max_bull_loss
                    },
                    "Iron Butterfly" : {                                       
                        "long_call_strike_price" : long_call_strike_price,
                        "long_put_strike_premium" : long_call_premium,
                        "short_put_strike_price" : short_call_strike_price,
                        "short_put_strike_premium" : short_call_premium,

                        "net_debit" : butterfly_new_premium,
                        "max_profit" : butterfly_max_profit,
                        "breakeven_bear" : butterfly_breakeven_bear,
                        "breakeven_bull" : butterfly_breakeven_bull,
                        "max_loss" : butterfly_new_premium
                    }
                }
        # roll out long leg
        elif outlook == BEAR:
            if moneyness == ITM:
                #just close it lol
                #roll down short leg(debit)
                new_short_put_price = put_strikes[bin_search_closest(target_price, put_strikes)[0]]
                old_short_put_premium = puts.get_option_for_strike(short_leg_strike).get_price()
                new_short_put_premium = puts.get_option_for_strike(new_short_put_price).get_price()     

                net_debit = old_short_put_premium - new_short_put_premium

                new_premium = net_premium + net_debit
                roll_out_max_profit = - long_leg_strike - new_short_put_premium  - new_premium
                roll_out_breakeven = long_leg_strike - new_premium
                roll_out_max_loss = new_premium
                
                return {
                    "Close trade" : "close trade",
                    "Roll short leg up" : {
                        "net_debit" : net_debit,
                        "strike_price" : new_short_put_price,
                        "strike_premium" : new_short_put_premium,
                        "max_profit" : roll_out_max_profit,
                        "breakeven" : roll_out_breakeven,
                        "max_loss" : roll_out_max_loss
                    }
                }

            if moneyness == OTM:
                # roll out expiry
                later_puts = puts.get_nearest_day(28)
                
                old_long_put_premium = later_puts.get_option_for_strike(long_leg_strike).get_price()
                old_short_put_premium = later_puts.get_option_for_strike(short_leg_strike).get_price()
                cost_to_close = old_long_put_premium - old_short_put_premium  

                new_long_put_premium = later_puts.get_option_for_strike(long_leg_strike).get_price()
                new_short_put_premium = later_puts.get_option_for_strike(short_leg_strike).get_price()
                cost_to_open = new_long_put_premium - new_short_put_premium

                net_debit = cost_to_open - cost_to_close
                new_premium = net_premium + net_debit

                roll_out_max_profit = long_leg_strike -short_leg_strike  - new_premium
                roll_out_breakeven = long_leg_strike - new_premium

                # calender
                return {
                    "Roll out expiry": {
                        "net_debit" : net_debit,
                        "new_long_call_premium" : new_long_put_premium,
                        "new_short_call_premium" : new_short_put_premium,
                        "max_profit" : roll_out_max_profit,
                        "breakeven" : roll_out_breakeven,
                        "max_loss" : new_premium
                    }
                }
    # credit spread
    else:
        if outlook == BULL:
            diff = long_leg_strike - short_leg_strike

            if target_price > short_leg_strike: 
                short_put_strike_price = short_leg_strike
                short_put_premium = puts.get_option_for_strike(short_put_strike_price).get_price()

                long_put_strike_price = short_leg_strike - diff
                long_put_premium = puts.get_option_for_strike(long_put_strike_price).get_price()                   
            else:
                short_put_strike_price = put_strikes[bin_search_closest(target_price, put_strikes)[0]]
                short_put_premium = puts.get_option_for_strike(short_put_strike_price).get_price()

                long_put_strike_price = short_put_strike_price - diff
                long_put_premium = calls.get_option_for_strike(long_put_strike_price).get_price()

            butterfly_credit = short_put_premium - long_put_premium
            
            butterfly_new_credit = net_premium + butterfly_credit
            butterfly_breakeven_bear = short_put_strike_price - butterfly_new_credit
            butterfly_breakeven_bull = short_leg_strike + butterfly_new_credit
            butterfly_max_loss = diff - butterfly_new_credit
            
            return {
                "Close trade" : "Close Trade",
                "Iron Butterfly" : {                                       
                    "long_put_strike_price" : long_put_strike_price,
                    "long_put_premium" : long_put_premium,
                    "short_put_strike_price" : short_put_strike_price,
                    "short_put_premium" : short_put_premium,

                    "net_credit" : butterfly_credit,
                    "max_profit" : butterfly_new_credit,
                    "breakeven_bear" : butterfly_breakeven_bear,
                    "breakeven_bull" : butterfly_breakeven_bull,
                    "max_loss" : butterfly_max_loss
                }
            }
        elif outlook == BEAR:
            if moneyness == ITM:
            # wait lol/roll expiry   
                later_calls = calls.get_nearest_day(28)
                
                old_long_call_premium = later_calls.get_option_for_strike(long_leg_strike).get_price()
                old_short_call_premium = later_calls.get_option_for_strike(short_leg_strike).get_price()
                cost_to_close = old_short_call_premium - old_long_call_premium

                new_long_call_premium = later_calls.get_option_for_strike(long_leg_strike).get_price()
                new_short_call_premium = later_calls.get_option_for_strike(short_leg_strike).get_price()
                cost_to_open = new_short_call_premium - new_long_call_premium

                net_cost = cost_to_close - cost_to_open
                new_credit = net_premium - net_cost

                roll_out_max_loss = - long_leg_strike - short_leg_strike - new_credit
                roll_out_breakeven = long_leg_strike - new_credit

                return {
                    "Wait" : "Wait",
                    "Roll out expiry": {
                        "net_cost" : net_cost,
                        "new_long_put_premium" : new_long_call_premium,
                        "new_short_put_premium" : new_short_call_premium,
                        "max_profit" : new_credit,
                        "breakeven" : roll_out_breakeven,
                        "max_loss" : roll_out_max_loss
                    }
                }
            if moneyness == OTM:
            # just close it lol or wait idiot 
                return {
                    "Close trade" : "Close Trade",
                    "Wait" : "Wait"
                }

def adjust_collar(ticker, net_premium, lower_bound, upper_bound, outlook, new_target_price, risk):
    # roll out, adj challenged leg
        
def adjust_condor():


# print(bull_debit_spread("aapl", 30, 140, 150, 30))
# print(bear_credit_spread("aapl", 30, 130, 120, 80))
# print(collar("aapl", 30, 120, 130, 150, 20))
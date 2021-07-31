import math
from utils.search import bin_search_closest
from utils.graphs import draw_graph
from hedge_instruments.instrument import Instrument
from hedge_instruments.option import Call, Put
from hedge_instruments.stock import Stock
from portfolio_functions.portfolio_constants import BEAR, BULL, STRADDLE, NEUTRAL, OTM, ATM, ITM

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


def hedge_stock(ticker, entry_price, risk, breakeven_point, days, capped = True, target_price = None):
    result = Put(ticker).get_nearest_day(days).get_hedge_strike(risk, entry_price)

    return result


def collar(ticker, days, entry_price, lower_bound, target_price, risk):
    calls = Call(ticker).get_nearest_day(days)
    strikes = calls.get_strikes()
    closest_target_price = strikes[bin_search_closest(target_price, strikes)[0]]

    long_call_premium = calls.get_option_for_strike(closest_target_price).get_price()
    result = Put(ticker).get_nearest_day(days).get_strike_for_breakeven_collar(entry_price, lower_bound, closest_target_price, long_call_premium, risk)

    return result


def iron_condor(ticker, days, lower_bound, upper_bound, risk):
    breakeven_acceptable_range = 0.05 * Stock(ticker).get_price()

    calls = Call(ticker).get_nearest_day(days)
    puts = Put(ticker).get_nearest_day(days)

    call_strikes = calls.get_strikes()
    put_strikes = puts.get_strikes()
    # print(call_strikes)
    # print(put_strikes)

    mid_strike = lower_bound + ((upper_bound - lower_bound) / 2)
    short_call_range_start = bin_search_closest(mid_strike, call_strikes)[1]
    short_call_range_end = bin_search_closest(upper_bound, call_strikes)[0]
    short_put_range_start = bin_search_closest(lower_bound, put_strikes)[1]
    short_put_range_end = bin_search_closest(mid_strike, put_strikes)[0]

    # print("CALL RANGE: [{}] {} - [{}] {}".format(short_call_range_start, call_strikes[short_call_range_start], short_call_range_end, call_strikes[short_call_range_end]))
    # print("PUT RANGE: [{}] {} - [{}] {}".format(short_put_range_start, put_strikes[short_put_range_start], short_put_range_end, put_strikes[short_put_range_end]))

    max_gain = {"expiration_date": calls.expiration_date, "max_profit": -math.inf, "max_loss": -math.inf}
    min_loss = {"expiration_date": calls.expiration_date, "max_profit": -math.inf, "max_loss": -math.inf}

    short_call_index = short_call_range_start
    short_put_index = short_put_range_end
    # Iterate through each pair of short call and short put starting at most ATM
    while short_call_index <= short_call_range_end and short_put_index >= short_put_range_start:
        short_call = call_strikes[short_call_index]
        short_put = put_strikes[short_put_index]

        if short_call - call_strikes[short_call_range_start] != put_strikes[short_put_range_end] - short_put:
            # print("CALL: {}/{}    |    PUT: {}/{}".format(
            #     short_call,
            #     call_strikes[short_call_range_start],
            #     short_put,
            #     put_strikes[short_put_range_end]
            # ))
            # Strike diff are different between calls and puts
            if short_call - call_strikes[short_call_range_start] < put_strikes[short_put_range_end] - short_put:
                short_call_index += 1
            else:
                short_put_index -= 1

        short_call_premium = calls.get_option_for_strike(short_call).get_price()
        short_put_premium = puts.get_option_for_strike(short_put).get_price()
        # print("[{}] CALL {}: ${}    |    [{}] PUT {}: ${}".format(
        #     short_call_index, short_call, short_call_premium,
        #     short_put_index, short_put, short_put_premium
        # ))

        long_call_index = short_call_range_end + 1
        long_put_index = short_put_range_start - 1
        while True:
            # Check if index is out of range
            if long_call_index >= len(call_strikes) or long_put_index < 0:
                break

            long_call = call_strikes[long_call_index]
            long_put = put_strikes[long_put_index]
            # If strike difference does not match, increase interval accordingly
            if long_call - short_call != short_put - long_put:
                if long_call - short_call < short_put - long_put:
                    long_call_index += 1
                    continue
                else:
                    long_put_index -= 1
                    continue

            # Strike difference matches, calculate
            long_call_premium = calls.get_option_for_strike(long_call).get_price()
            long_put_premium = puts.get_option_for_strike(long_put).get_price()
            net_premium = short_call_premium + short_put_premium - long_call_premium - long_put_premium
            call_breakeven = short_call + net_premium
            put_breakeven = short_put - net_premium
            call_loss = net_premium - (long_call - short_call)
            put_loss = net_premium - (short_put - long_put)
            max_loss = max(call_loss, put_loss)

            # Check if breakevens and risk is within acceptable range
            if (abs(call_breakeven - upper_bound) <= breakeven_acceptable_range and
                abs(put_breakeven - lower_bound) <= breakeven_acceptable_range and
                max_loss > -risk):
                # Check for max_gain and max_loss
                if net_premium > max_gain["max_profit"]:
                    max_gain["max_profit"] = net_premium
                    max_gain["max_loss"] = max_loss
                    max_gain["call_loss"] = call_loss
                    max_gain["put_loss"] = put_loss
                    max_gain["short_call"] = short_call
                    max_gain["short_put"] = short_put
                    max_gain["long_call"] = long_call
                    max_gain["long_put"] = long_put
                    max_gain["call_breakeven"] = call_breakeven
                    max_gain["put_breakeven"] = put_breakeven
                if max_loss > min_loss["max_loss"]:
                    min_loss["max_profit"] = net_premium
                    min_loss["max_loss"] = max_loss
                    min_loss["call_loss"] = call_loss
                    min_loss["put_loss"] = put_loss
                    min_loss["short_call"] = short_call
                    min_loss["short_put"] = short_put
                    min_loss["long_call"] = long_call
                    min_loss["long_put"] = long_put
                    min_loss["call_breakeven"] = call_breakeven
                    min_loss["put_breakeven"] = put_breakeven

            # Update long indexes
            long_call_index += 1
            long_put_index -= 1

        # Update short indexes
        short_call_index += 1
        short_put_index -= 1

    return {
        "data": {"max_gain": max_gain, "min_loss": min_loss},
        "graph": {
            "price_limit": call_strikes[-1],
            "coordinate_lists": [
                {"name": "Iron Condor Max Gain", "coordinates": [(0, max_gain["max_loss"]),
                                                                 (max_gain["long_put"], max_gain["max_loss"]),
                                                                 (max_gain["short_put"], max_gain["max_profit"]),
                                                                 (max_gain["short_call"], max_gain["max_profit"]),
                                                                 (max_gain["long_call"], max_gain["max_loss"]),
                                                                 (call_strikes[-1], max_gain["max_loss"])]},
                {"name": "Iron Condor Min Loss", "coordinates": [(0, min_loss["max_loss"]),
                                                                 (min_loss["long_put"], min_loss["max_loss"]),
                                                                 (min_loss["short_put"], min_loss["max_profit"]),
                                                                 (min_loss["short_call"], min_loss["max_profit"]),
                                                                 (min_loss["long_call"], min_loss["max_loss"]),
                                                                 (call_strikes[-1], min_loss["max_loss"])]}
                ],
            "graph": draw_graph(price_limit=call_strikes[-1], coordinate_lists=[
                {"name": "Iron Condor Max Gain", "coordinates": [(0, max_gain["max_loss"]),
                                                                 (max_gain["long_put"], max_gain["max_loss"]),
                                                                 (max_gain["short_put"], max_gain["max_profit"]),
                                                                 (max_gain["short_call"], max_gain["max_profit"]),
                                                                 (max_gain["long_call"], max_gain["max_loss"]),
                                                                 (call_strikes[-1], max_gain["max_loss"])]},
                {"name": "Iron Condor Min Loss", "coordinates": [(0, min_loss["max_loss"]),
                                                                 (min_loss["long_put"], min_loss["max_loss"]),
                                                                 (min_loss["short_put"], min_loss["max_profit"]),
                                                                 (min_loss["short_call"], min_loss["max_profit"]),
                                                                 (min_loss["long_call"], min_loss["max_loss"]),
                                                                 (call_strikes[-1], min_loss["max_loss"])]}
                ])
        }
    }


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


def adjust_collar(ticker, day, month, year, stock_entry, net_premium, put_strike, short_call_strike, outlook, target_price, risk):
    puts = Put(ticker, day, month, year)
    put_strikes = puts.get_strikes
    
    calls = Call(ticker, day, month, year)
    call_strikes = calls.get_strikes()

    # roll up short call
    if outlook == BULL:
        new_short_call_price = call_strikes[bin_search_closest(target_price, call_strikes)]
        new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()
        old_short_call_premium = calls.get_option_for_strike(short_call_strike).get_price()

        net_debit = old_short_call_premium - new_short_call_premium

        new_premium = net_premium + net_debit
        roll_up_max_profit = new_short_call_price - stock_entry  - new_premium
        roll_up_breakeven = stock_entry + new_premium
        roll_up_max_loss = stock_entry - put_strike - new_premium
        
        return {
            "Close trade" : "close trade",
            "Roll short call up" : {
                "net_debit" : net_debit,
                "strike_price" : new_short_call_price,
                "strike_premium" : new_short_call_premium,
                "max_profit" : roll_up_max_profit,
                "breakeven" : roll_up_breakeven,
                "max_loss" : roll_up_max_loss
            }
        }


    # roll down short call short call have to be < old shortr call
    elif outlook == BEAR:
        new_short_call_price = call_strikes[bin_search_closest(target_price, call_strikes)]
        new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()
        old_short_call_premium = calls.get_option_for_strike(short_call_strike).get_price()

        net_credit = new_short_call_premium - old_short_call_premium

        new_premium = net_premium - net_credit
        roll_up_max_profit = new_short_call_price - stock_entry  - new_premium
        roll_up_breakeven = stock_entry + new_premium
        roll_up_max_loss = stock_entry - put_strike - new_premium
        
        return {
            "Close trade" : "close trade",
            "Roll short call up" : {
                "net_credit" : net_credit,
                "strike_price" : new_short_call_price,
                "strike_premium" : new_short_call_premium,
                "max_profit" : roll_up_max_profit,
                "breakeven" : roll_up_breakeven,
                "max_loss" : roll_up_max_loss
            }
        }


def adjust_condor(ticker, day, month, year, credit, short_call_strike, long_call_strike, short_put_strike, long_put_strike, moneyness, outlook, target_price, risk):
    puts = Put(ticker, day, month, year)
    put_strikes = puts.get_strikes
    
    calls = Call(ticker, day, month, year)
    call_strikes = calls.get_strikes()

    # roll up bull spread
    if outlook == BULL:
        diff = short_put_strike - long_put_strike
        
        old_short_put_premium = puts.get_option_for_strike(short_put_strike).get_price()
        old_long_put_premium = puts.get_option_for_strike(long_put_strike).get_price()
        cost_to_close = old_short_put_premium - old_long_put_premium      

        # butterfly since target more than bear threshhold
        if target_price > short_call_strike:
            new_short_put_price = short_call_strike
            new_short_put_premium = puts.get_option_for_strike(new_short_put_price).get_price()

            new_long_put_price = put_strikes[bin_search_closest((new_short_put_price - diff), put_strikes)[1]]
            new_long_put_premium = puts.get_option_for_strike(new_long_put_price).get_price()
        # condor
        else:
            new_short_put_price = put_strikes[bin_search_closest(target_price, put_strikes)[0]]
            new_short_put_premium = puts.get_option_for_strike(new_short_put_price).get_price()

            new_long_put_price = put_strikes[bin_search_closest((new_short_put_price - diff), put_strikes)[1]]
            new_long_put_premium = puts.get_option_for_strike(new_long_put_price).get_price()

        credit_to_open = new_short_put_premium - new_long_put_premium

        net_credit = credit_to_open - cost_to_close      
        
        new_credit =  credit + net_credit
        roll_up_breakeven_bear = new_short_put_price - new_credit
        roll_up_breakeven_bull = short_call_strike + new_credit
        roll_up_max_loss = diff - new_credit

        return {
            "Roll bull spread up" : {
                "long_put_strike" : new_long_put_price,
                "long_put_premium" : new_long_put_premium,
                "short_put_strike" : new_short_put_price,
                "short_put_premium" : new_short_put_premium,

                "net_credit" : net_credit,
                "max_profit" : new_credit,
                "breakeven_bear" : roll_up_breakeven_bear,
                "breakeven_bull" : roll_up_breakeven_bull,
                "max_loss" : roll_up_max_loss
            }
        }    

    #roll in bear spread 
    elif outlook == BEAR:
        diff = long_call_strike - short_call_strike
        
        old_short_call_premium = calls.get_option_for_strike(short_call_strike).get_price()
        old_long_call_premium = calls.get_option_for_strike(long_call_strike).get_price()
        cost_to_close = old_short_call_premium - old_long_call_premium      

        # butterfly since target more than bear threshhold
        if target_price < short_put_strike:
            new_short_call_price = short_put_strike
            new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()

            new_long_call_price = put_strikes[bin_search_closest((new_short_call_price + diff), put_strikes)[1]]
            new_long_call_premium = puts.get_option_for_strike(new_long_call_price).get_price()
        # condor
        else:
            new_short_call_price = call_strikes[bin_search_closest(target_price, put_strikes)[0]]
            new_short_call_premium = calls.get_option_for_strike(new_short_call_price).get_price()

            new_long_call_price = put_strikes[bin_search_closest((new_short_call_price + diff), put_strikes)[1]]
            new_long_call_premium = puts.get_option_for_strike(new_long_call_price).get_price()

        credit_to_open = new_short_call_premium - new_long_call_premium
        net_credit = credit_to_open - cost_to_close      
        
        new_credit =  credit + net_credit
        roll_up_breakeven_bear = short_put_strike - new_credit
        roll_up_breakeven_bull = new_short_call_price + new_credit
        roll_up_max_loss = diff - new_credit

        return {
            "Roll bull spread up" : {
                "long_call_strike" : new_long_call_price,
                "long_call_premium" : new_long_call_premium,
                "short_call_strike" : new_short_call_price,
                "short_call_premium" : new_short_call_premium,

                "net_credit" : net_credit,
                "max_profit" : new_credit,
                "breakeven_bear" : roll_up_breakeven_bear,
                "breakeven_bull" : roll_up_breakeven_bull,
                "max_loss" : roll_up_max_loss
            }
        }  

# print(bull_debit_spread("aapl", 30, 140, 150, 30))

# print(bear_credit_spread("aapl", 30, 130, 120, 80))
# print(iron_condor("aapl", 30, 135, 155, 20)["data"])


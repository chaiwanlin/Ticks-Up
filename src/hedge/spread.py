import math
from utility.search import bin_search_closest
from utility.graphs import draw_graph
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

    max_gain = {"max_profit": -math.inf, "max_loss": -math.inf}
    min_loss = {"max_profit": -math.inf, "max_loss": -math.inf}

    short_call_index = short_call_range_start
    short_put_index = short_put_range_end
    # Iterate through each pair of short call and short put starting at most ATM
    while short_call_index <= short_call_range_end and short_put_index >= short_put_range_start:
        short_call = call_strikes[short_call_index]
        short_put = put_strikes[short_put_index]

        if (short_call - call_strikes[short_call_range_start] != put_strikes[short_put_range_end] - short_put):
            # print("CALL: {}/{}    |    PUT: {}/{}".format(
            #     short_call,
            #     call_strikes[short_call_range_start],
            #     short_put,
            #     put_strikes[short_put_range_end]
            # ))
            # Strike diff are different between calls and puts
            if (short_call - call_strikes[short_call_range_start] < put_strikes[short_put_range_end] - short_put):
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

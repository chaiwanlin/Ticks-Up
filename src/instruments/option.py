import math
from utility.search import  bin_search_closest
from instruments.instrument import Instrument
from instruments.stock import Stock
from instruments.constants import YAHOO_OPTION
from utility.graphs import draw_graph
import urllib.request
import urllib.response
import json
import datetime

# nearest date problem

class Option(Instrument):

    today = datetime.datetime.now(datetime.timezone.utc)

    def __init__(self, ticker, 
        year = today.year , month = today.month , day = today.day):

        epoch = int(datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc).timestamp())

        url = f"{YAHOO_OPTION}{ticker}?date={epoch}"

        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        result = data["optionChain"]["result"]
        # print(result)

        if not result:
            raise LookupError("invalid ticker :D")
        else:
            data = result[0]

            self.expiration = data["expirationDates"]

            # for expiration in data["expirationDates"]:
            #     date = datetime.fromtimestamp(expiration)

        if epoch not in self.expiration:
            closest_date = bin_search_closest(epoch, self.expiration)
            date_before = self.expiration[closest_date[0]]
            date_after = self.expiration[closest_date[1]]
            status = closest_date[2]
            print(date_before, date_after, status)

            url = f"{YAHOO_OPTION}{ticker}?date={date_after}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())["optionChain"]["result"][0]

        self.data = data
        self.options = data["options"][0]
        self.strikes = data["strikes"]

        # print(data["optionChain"]["result"][0])
        super().__init__(ticker, Stock(ticker))

    def get_strikes(self):
        return self.strikes
    
    def get_data(self):
        return self.data

class Call(Option):
    today = datetime.datetime.now(datetime.timezone.utc)

    def __init__(self, ticker,
        year = today.year , month = today.month , day = today.day):
        super().__init__(ticker, year, month, day)

        self.data = self.options["calls"]
        self.strikes = []

        for strike in self.data:
            self.strikes.append(strike["strike"])

    def get_option_for_strike(self, strike_price):
        try:
            for strike in self.data:
                if strike_price == strike["strike"]:
                    data = strike 
            return CallOption(self.ticker, self.underlying, data)
        except UnboundLocalError:
            print("no availible data")

    def get_nearest_day(self, day):
        next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=day)
        return Call(self.ticker, next_date.year, next_date.month, next_date.day)

    def get_open_interest_count(self):
        sum = 0
        for strike in self.data:
            sum += strike["openInterest"]
        return sum    

    def aggregated_iv(self):
        result = bin_search_closest(self.underlying.get_price(), self.strikes)
        itm = self.strikes[result[0]]
        otm = self.strikes[result[1]]
        itm = self.get_option_for_strike(itm)
        otm = self.get_option_for_strike(otm)

        itm_iv = itm.get_iv()
        itm_vol = itm.get_interest()
        otm_iv = otm.get_iv()
        otm_vol = otm.get_interest()

        total = itm_vol + otm_vol
        agg_iv = itm_vol/total * itm_iv + otm_vol/total * otm_iv
        
        return (agg_iv, total)

    def get_strike_for_breakeven_debit(self, breakeven_point, short_call_strike, short_call_premium,  risk = math.inf, threshold = 1):
        max_premium = risk - short_call_premium

        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_threshold = -threshold

        min_cost_net_value = None
        min_cost_strike = breakeven_point
        min_cost_premium = breakeven_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price < breakeven_point:
                net_value = breakeven_point - strike_price + short_call_premium - strike_premium

                if strike_premium < max_premium:
                    if net_value > max_gain_net_value:
                        max_gain_net_value = net_value
                        max_gain_strike = strike_price
                        max_gain_premium = strike_premium
                    
                    if min_threshold <= net_value <= threshold and strike_premium < min_cost_premium: 
                        min_cost_net_value = net_value
                        min_cost_strike = strike_price
                        min_cost_premium = strike_premium 

        if not min_cost_net_value:
            threshold += 1
            return self.get_strike_for_breakeven_debit(breakeven_point, short_call_strike, short_call_premium, risk,  threshold)
        else:
            max_gain_loss = short_call_premium - max_gain_premium
            max_gain_profit = short_call_strike - max_gain_strike - max_gain_loss
            max_gain_breakeven = max_gain_loss + max_gain_strike

            min_cost_loss = short_call_premium - min_cost_premium 
            min_cost_profit = short_call_strike - min_cost_strike - min_cost_loss
            min_cost_breakeven = min_cost_loss + min_cost_strike

            return {
                "data": {
                    "short_call" : {
                        "strike_strike" : short_call_strike,
                        "strike_premium" : short_call_premium
                    },
                    "max_gain" : {
                        "strike_price" : max_gain_strike,
                        "strike_premium" : max_gain_premium,
                        "net_value_at_breakeven" : max_gain_net_value,
                        "max_profit" : max_gain_profit,
                        "breakeven" : max_gain_breakeven,
                        "max_loss" : max_gain_loss
                    },
                    "min_cost": {
                        "strike_price" : min_cost_strike,
                        "strike_premium" : min_cost_premium,
                        "net_value_at_breakeven" : min_cost_net_value,
                        "max_profit" : min_cost_profit,
                        "breakeven" : min_cost_breakeven,
                        "max_loss" : min_cost_loss
                    }
                },
                "graph": {
                    "price_limit": self.strikes[-1],
                    "coordinate_lists": [
                        {"name": "Debit Max Gain", "coordinates": [(0, max_gain_loss),
                                                             (max_gain_strike, max_gain_loss),
                                                             (short_call_strike, max_gain_profit),
                                                             (self.strikes[-1], max_gain_profit)]},
                        {"name": "Debit Min Cost", "coordinates": [(0, min_cost_loss),
                                                             (min_cost_strike, min_cost_loss),
                                                             (short_call_strike, min_cost_profit),
                                                             (self.strikes[-1], min_cost_profit)]},
                    ],
                    "graph": draw_graph(price_limit=self.strikes[-1], coordinate_lists=[
                        {"name": "Debit Max Gain", "coordinates": [(0, max_gain_loss),
                                                             (max_gain_strike, max_gain_loss),
                                                             (short_call_strike, max_gain_profit),
                                                             (self.strikes[-1], max_gain_profit)]},
                        {"name": "Debit Min Cost", "coordinates": [(0, min_cost_loss),
                                                             (min_cost_strike, min_cost_loss),
                                                             (short_call_strike, min_cost_profit),
                                                             (self.strikes[-1], min_cost_profit)]},
                    ])
                }
            }

    def adjust_bull_spread(self, long_call, short_call, short_call_premium, breakeven_point, target_price, net_premium, risk, threshold = 1):
        
        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_threshold = -threshold

        min_cost_net_value = None
        min_cost_strike = breakeven_point
        min_cost_premium = breakeven_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price < short_call:
                net_cost = short_call_premium - strike_premium
                net_value = breakeven_point - long_call + net_cost
                max_loss = net_premium + net_cost

                if risk < max_loss:
                    if net_value > max_gain_net_value:
                        max_gain_net_value = net_value
                        max_gain_strike = strike_price
                        max_gain_premium = strike_premium 
                    
                    if min_threshold <= net_value <= threshold and strike_premium < min_cost_premium: 
                        min_cost_net_value = net_value
                        min_cost_strike = strike_price
                        min_cost_premium = strike_premium 


    def get_strike_for_breakeven_credit(self, breakeven_point, short_call_strike, short_call_premium, risk = math.inf):
        net_breakeven_value = short_call_premium - (breakeven_point - short_call_strike)

        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_risk_net_value = None
        min_risk_strike = breakeven_point
        min_risk_premium = breakeven_point
        min_risk_max_loss = breakeven_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price > breakeven_point:
                net_value = net_breakeven_value - strike_premium
                max_loss = strike_price - short_call_strike - short_call_premium + strike_premium

                if max_loss < risk:
                    if strike_premium < max_gain_premium:
                        max_gain_net_value = net_value
                        max_gain_strike = strike_price
                        max_gain_premium = strike_premium 
                    
                    if max_loss < min_risk_max_loss: 
                        min_risk_net_value = net_value
                        min_risk_strike = strike_price
                        min_risk_premium = strike_premium 
                        min_risk_max_loss = max_loss

        
        max_gain_profit = short_call_premium - max_gain_premium
        max_gain_loss = max_gain_strike - short_call_strike - max_gain_profit
        max_gain_breakeven = short_call_strike + max_gain_profit

        min_risk_profit = short_call_premium - min_risk_premium
        min_risk_loss = min_risk_strike - short_call_strike - min_risk_profit
        min_risk_breakeven = short_call_strike + min_risk_profit
        return {
            "data": {
                "short_call": {
                    "strike_strike": short_call_strike,
                    "strike_premium": short_call_premium
                },
                "max_gain": {
                    "strike_price": max_gain_strike,
                    "strike_premium": max_gain_premium,
                    "net_value_at_breakeven": max_gain_net_value,
                    "max_profit": max_gain_profit,
                    "breakeven": max_gain_breakeven,
                    "max_loss": max_gain_loss
                },
                "min_loss": {
                    "strike_price": min_risk_strike,
                    "strike_premium": min_risk_premium,
                    "net_value_at_breakeven": min_risk_net_value,
                    "max_profit": min_risk_profit,
                    "breakeven": min_risk_breakeven,
                    "max_loss": min_risk_loss
                }
            },
            "graph": {
                "price_limit": self.strikes[-1],
                "coordinate_lists": [
                    {"name": "Credit Max Gain", "coordinates": [(0, max_gain_profit),
                                                         (short_call_strike, max_gain_profit),
                                                         (max_gain_strike, -max_gain_loss),
                                                         (self.strikes[-1], -max_gain_loss)]},
                    {"name": "Credit Min Cost", "coordinates": [(0, min_risk_profit),
                                                         (short_call_strike, min_risk_profit),
                                                         (min_risk_strike, -min_risk_loss),
                                                         (self.strikes[-1], -min_risk_loss)]},
                ],
                "graph": draw_graph(price_limit=self.strikes[-1], coordinate_lists=[
                    {"name": "Credit Max Gain", "coordinates": [(0, max_gain_profit),
                                                         (short_call_strike, max_gain_profit),
                                                         (max_gain_strike, -max_gain_loss),
                                                         (self.strikes[-1], -max_gain_loss)]},
                    {"name": "Credit Min Cost", "coordinates": [(0, min_risk_profit),
                                                         (short_call_strike, min_risk_profit),
                                                         (min_risk_strike, -min_risk_loss),
                                                         (self.strikes[-1], -min_risk_loss)]},
                ])
            }
        }


class CallOption:
    def __init__(self, ticker, underlying, data):
        self.ticker = ticker
        self.underlying = underlying
        self.price = data["lastPrice"]
        try:
            self.volume = data["volume"]
        except KeyError:
            self.volume = None
        self.interest = data["openInterest"]
        self.bid = data["bid"]
        self.ask = data["ask"]
        self.implied_volatility = data["impliedVolatility"]

    def get_ticker(self):
        return self.ticker
    
    def get_underlying(self):
        return self.underlying

    def get_price(self):
        return self.price
    
    def get_volume(self):
        return self.volume
    
    def get_interest(self):
        return self.interest
    
    def get_bid(self):
        return self.bid
    
    def get_ask(self):
        return self.ask
        
    def get_iv(self):
        return self.implied_volatility


class Put(Option):
    today = datetime.datetime.now(datetime.timezone.utc)
    
    def __init__(self, ticker,
        year = today.year , month = today.month , day = today.day):
        super().__init__(ticker, year, month, day)

        self.data = self.options["puts"]
        self.strikes = []

        for strike in self.data:
            self.strikes.append(strike["strike"])

    def get_option_for_strike(self, strike_price):
        try:
            for strike in self.data:
                if strike_price == strike["strike"]:
                    data = strike 
            return PutOption(self.ticker, self.underlying, data)
        except UnboundLocalError:
            print("no availible data")
    
    def get_nearest_day(self, day):
        next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=day)
        print(next_date)
        return Put(self.ticker, next_date.year, next_date.month, next_date.day)
    
    def aggregated_iv(self):
        result = bin_search_closest(self.underlying.get_price(), self.strikes)
        itm = self.strikes[result[1]]
        otm = self.strikes[result[0]]
        itm = self.get_option_for_strike(itm)
        otm = self.get_option_for_strike(otm)

        itm_iv = itm.get_iv()
        itm_vol = itm.get_interest()
        otm_iv = otm.get_iv()
        otm_vol = otm.get_interest()
        total = itm_vol + otm_vol
        agg_iv = itm_vol/total * itm_iv + otm_vol/total * otm_iv

        return (agg_iv, total)

    def get_open_interest_count(self):
        sum = 0
        for strike in self.data:
            sum += strike["openInterest"]
        return sum

    def get_hedge_stike(self, risk, entry_point):
       
        min_cost_strike_price = entry_point
        min_cost_strike_premium = entry_point
        min_cost_risk = entry_point

        min_loss_strike_price = entry_point
        min_loss_strike_premium = entry_point
        min_loss_risk = entry_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]
            max_loss = entry_point - strike_price + strike_premium 

            if max_loss < risk and strike["strike"] <= entry_point:
                if strike_premium < min_cost_strike_premium:
                    min_cost_risk = max_loss
                    min_cost_strike_price = strike_price
                    min_cost_strike_premium = strike_premium

                if max_loss < min_loss_risk:
                    min_loss_risk = max_loss
                    min_loss_strike_price = strike_price
                    min_loss_strike_premium = strike_premium
                    
            
        return { 
            "stock" : entry_point, 
            "min_cost" : {
                "strike_price" : min_cost_strike_price,
                "strike_premium" : min_cost_strike_premium,
                "risk" : min_cost_risk
            },
            "min_loss": {
                "strike_price" : min_loss_strike_price,
                "strike_premium" : min_loss_strike_premium,
                "risk" : min_loss_risk
            }
        }
        # ideally do a graph for best strike price to buy from current price to break point in a graph or wtv

    def get_strike_for_breakeven_debit(self, breakeven_point, short_put_strike, short_put_premium, risk = math.inf, threshold = 1):
        max_premium = risk - short_put_premium

        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_threshold = -threshold

        min_cost_net_value = None
        min_cost_strike = breakeven_point
        min_cost_premium = breakeven_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price > breakeven_point:
                net_value = strike_price - breakeven_point + short_put_premium - strike_premium 
                print(net_value)

                if strike_premium  < max_premium:
                    if net_value > max_gain_net_value:
                        max_gain_net_value = net_value
                        max_gain_strike = strike_price
                        max_gain_premium = strike_premium 
                    
                    if min_threshold <= net_value <= threshold and strike_premium < min_cost_premium: 
                        min_cost_net_value = net_value
                        min_cost_strike = strike_price
                        min_cost_premium = strike_premium 


        if not min_cost_net_value:
            threshold += 1
            return self.get_strike_for_breakeven_debit(breakeven_point, short_put_strike, short_put_premium, risk, threshold)
        else:
            max_gain_loss = short_put_premium - max_gain_premium 
            max_gain_profit = max_gain_strike - short_put_strike - max_gain_loss
            max_gain_breakeven = max_gain_strike - max_gain_loss

            min_cost_loss = short_put_premium - min_cost_premium
            min_cost_profit = min_cost_strike - short_put_strike - min_cost_loss
            min_cost_breakeven = min_cost_strike - min_cost_loss 

            return {
                "data": {
                    "short_put" : {
                        "strike_strike" : short_put_strike,
                        "strike_premium" : short_put_premium
                    },
                    "max_gain" : {
                        "strike_price" : max_gain_strike,
                        "strike_premium" : max_gain_premium,
                        "net_value_at_breakeven" : max_gain_net_value,
                        "max_profit" : max_gain_profit,
                        "breakeven" : max_gain_breakeven,
                        "max_loss" : max_gain_loss,
                    },
                    "min_cost": {
                        "strike_price" : min_cost_strike,
                        "strike_premium" : min_cost_premium,
                        "net_value_at_breakeven" : min_cost_net_value,
                        "max_profit" : min_cost_profit,
                        "breakeven" : min_cost_breakeven,
                        "max_loss" : min_cost_loss
                    }
                },
                "graph": {
                    "price_limit": self.strikes[-1],
                    "coordinate_lists": [
                        {"name": "Debit Max Gain", "coordinates": [(0, max_gain_profit),
                                                             (short_put_strike, max_gain_profit),
                                                             (max_gain_strike, -max_gain_loss),
                                                             (self.strikes[-1], -max_gain_loss)]},
                        {"name": "Debit Min Cost", "coordinates": [(0, min_cost_profit),
                                                             (short_put_strike, min_cost_profit),
                                                             (min_cost_strike, -min_cost_loss),
                                                             (self.strikes[-1], -min_cost_loss)]},
                    ],
                    "graph": draw_graph(price_limit=self.strikes[-1], coordinate_lists=[
                        {"name": "Debit Max Gain", "coordinates": [(0, max_gain_profit),
                                                             (short_put_strike, max_gain_profit),
                                                             (max_gain_strike, -max_gain_loss),
                                                             (self.strikes[-1], -max_gain_loss)]},
                        {"name": "Debit Min Cost", "coordinates": [(0, min_cost_profit),
                                                             (short_put_strike, min_cost_profit),
                                                             (min_cost_strike, -min_cost_loss),
                                                             (self.strikes[-1], -min_cost_loss)]},
                    ])
                    }
            }

    def get_strike_for_breakeven_credit(self, breakeven_point, short_put_strike, short_put_premium, risk = math.inf, threshold = 1):
        net_breakeven_value = short_put_premium - (short_put_strike - breakeven_point)

        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_risk_net_value = None
        min_risk_strike = breakeven_point
        min_risk_premium = breakeven_point
        min_risk_max_loss = breakeven_point

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price < breakeven_point:
                net_value = net_breakeven_value - strike_premium
                max_loss = short_put_strike - strike_price + strike_premium - short_put_premium

                if max_loss  < risk:
                    if strike_premium < max_gain_premium:
                        max_gain_net_value = net_value
                        max_gain_strike = strike_price                        
                        max_gain_premium = strike_premium 
                    
                    if max_loss < min_risk_max_loss: 
                        min_risk_net_value = net_value
                        min_risk_strike = strike_price
                        min_risk_premium = strike_premium 
                        min_risk_max_loss = max_loss

        max_gain_profit = short_put_premium - max_gain_premium
        max_gain_loss = short_put_strike - max_gain_strike - max_gain_profit
        max_gain_breakeven = short_put_strike - max_gain_profit

        min_risk_profit = short_put_premium - min_risk_premium
        min_risk_loss = short_put_strike - min_risk_strike - min_risk_profit
        min_risk_breakeven = short_put_strike - min_risk_profit

        return {
            "data": {
                "short_put" : {
                    "strike_strike" : short_put_strike,
                    "strike_premium" : short_put_premium
                },
                "max_gain" : {
                    "strike_price" : max_gain_strike,
                    "strike_premium" : max_gain_premium,
                    "net_value_at_breakeven" : max_gain_net_value,
                    "max_profit" : max_gain_profit,
                    "breakeven" : max_gain_breakeven,
                    "max_loss" : max_gain_loss
                },
                "min_loss": {
                    "strike_price" : min_risk_strike,
                    "strike_premium" : min_risk_premium,
                    "net_value_at_breakeven" : min_risk_net_value,
                    "max_profit" : min_risk_profit,
                    "breakeven" : min_risk_breakeven,
                    "max_loss" : min_risk_loss
                }
            },
            "graph": {
                "price_limit": self.strikes[-1],
                "coordinate_lists": [
                    {"name": "Credit Max Gain", "coordinates": [(0, -max_gain_loss),
                                                         (max_gain_strike, -max_gain_loss),
                                                         (short_put_strike, max_gain_profit),
                                                         (self.strikes[-1], max_gain_profit)]},
                    {"name": "Credit Min Cost", "coordinates": [(0, -min_risk_loss),
                                                         (min_risk_strike, -min_risk_loss),
                                                         (short_put_strike, min_risk_profit),
                                                         (self.strikes[-1], min_risk_profit)]},
                ],
                "graph": draw_graph(price_limit=self.strikes[-1], coordinate_lists=[
                    {"name": "Credit Max Gain", "coordinates": [(0, -max_gain_loss),
                                                         (max_gain_strike, -max_gain_loss),
                                                         (short_put_strike, max_gain_profit),
                                                         (self.strikes[-1], max_gain_profit)]},
                    {"name": "Credit Min Cost", "coordinates": [(0, -min_risk_loss),
                                                         (min_risk_strike, -min_risk_loss),
                                                         (short_put_strike, min_risk_profit),
                                                         (self.strikes[-1], min_risk_profit)]},
                ])
            }
        }


    def get_strike_for_breakeven_collar(self, entry_price, breakeven_point, short_call_strike, short_call_premium, risk = math.inf, threshold = 1):
        breakeven_net_value = breakeven_point - entry_price + short_call_premium

        max_gain_net_value = -math.inf
        max_gain_strike = breakeven_point
        max_gain_premium = breakeven_point

        min_risk_net_value = None
        min_risk_strike = breakeven_point
        min_risk_premium = breakeven_point
        min_risk_max_loss = math.inf

        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]

            if strike_price < short_call_strike:
                if strike_price < breakeven_point:
                    max_loss = entry_price - strike_price + strike_premium - short_call_premium
                    net_value = breakeven_net_value - strike_premium 

                    if max_loss < risk:
                        if net_value > max_gain_net_value:
                            max_gain_net_value = net_value
                            max_gain_strike = strike_price
                            max_gain_premium = strike_premium 
                        
                        if max_loss < min_risk_max_loss: 
                            min_risk_net_value = net_value
                            min_risk_strike = strike_price
                            min_risk_premium = strike_premium
                            min_risk_max_loss = max_loss

        max_gain_cost = short_call_premium - max_gain_premium
        max_gain_loss = entry_price - max_gain_strike + max_gain_cost
        max_gain_profit = short_call_strike - entry_price - max_gain_cost
        max_gain_breakeven = entry_price + max_gain_cost

        min_risk_cost = short_call_premium - min_risk_premium
        min_risk_loss = entry_price - max_gain_strike + min_risk_cost
        min_risk_profit = short_call_strike - entry_price - max_gain_cost
        min_risk_breakeven = entry_price + min_risk_cost
        return {
            "short_call" : {
                "strike_strike" : short_call_strike,
                "strike_premium" : short_call_premium
            },
            "max_gain" : {
                "strike_price" : max_gain_strike,
                "strike_premium" : max_gain_premium,
                "net_value_at_breakeven" : max_gain_net_value,
                "cost" : max_gain_cost,
                "max_profit" : max_gain_profit,
                "breakeven" : max_gain_breakeven,
                "max_loss" : max_gain_loss
            },
            "min_loss": {
                "strike_price" : min_risk_strike,
                "strike_premium" : min_risk_premium,
                "net_value_at_breakeven" : min_risk_net_value,
                "cost" : min_risk_cost,
                "max_profit" : min_risk_profit,
                "breakeven" : min_risk_breakeven,
                "max_loss" : min_risk_loss
            }
        }

class PutOption:
    def __init__(self, ticker, underlying, data):
        self.ticker = ticker
        self.underlying = underlying
        self.price = data["lastPrice"]
        self.volume = data["volume"]
        self.interest = data["openInterest"]
        self.bid = data["bid"]
        self.ask = data["ask"]
        self.implied_volatility = data["impliedVolatility"]

    def get_ticker(self):
        return self.ticker
    
    def get_underlying(self):
        return self.underlying

    def get_price(self):
        return self.price
    
    def get_volume(self):
        return self.volume
    
    def get_interest(self):
        return self.interest
    
    def get_bid(self):
        return self.bid
    
    def get_ask(self):
        return self.ask
        
    def get_iv(self):
        return self.implied_volatility


# print(Call("aapl", month = 8, day = 20).get_strike_for_breakeven_credit(120, 110, 24.2, 40))
# print(Put("aapl", month = 8, day = 20).get_strike_for_breakeven_credit(140, 160, 27.25, 10))
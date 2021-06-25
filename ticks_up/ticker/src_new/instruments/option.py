import math
from ..utility.search import  bin_search_closest
from .instrument import Instrument
from .stock import Stock
from .constants import YAHOO_OPTION
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

    def get_implied_iv(self):
        call = Call(self.ticker).get_implied_iv()
        put = Put(self.ticker).get_implied_iv()
    
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
    
    def implied_price_range(self):
        result = bin_search_closest(self.underlying.get_price(), self.strikes)
        itm = self.strikes[result[0]]
        otm = self.strikes[result[1]]
        itm = self.get_option_for_strike(itm).get_iv()
        otm = self.get_option_for_strike(otm).get_iv()

        itm_iv = itm.get_iv()
        itm_vol = itm.get_interest()
        otm_iv = otm.get_iv()
        otm_vol = otm.get_interest()
        return (itm, otm)

    def get_strike_for_breakeven_debit(self, breakeven_point, risk = math.inf, offset = 0, threshold = 1):
        max_premium = risk - offset
        ideal_diff = 0
        ideal_strike = breakeven_point
        ideal_premium = breakeven_point

        min_threshold = -threshold
        min_diff = None
        min_strike = breakeven_point
        min_premium = breakeven_point
        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]
            if strike_price < breakeven_point:
                sum = breakeven_point -strike_price + offset - strike_premium 
                if strike_premium  < max_premium:
                    if sum > ideal_diff:
                        ideal_strike = strike_price
                        ideal_diff = sum
                        ideal_premium = strike_premium 
                    
                    if min_threshold <= sum <= threshold and strike_premium < min_premium: 
                        min_diff = sum
                        min_strike = strike_price
                        min_premium = strike_premium 

        if not min_diff:
            threshold += 1
            return self.get_strike_for_breakeven_debit(breakeven_point, risk, offset, threshold)
        else:
            return(ideal_strike, ideal_premium, ideal_diff, min_strike, min_premium, min_diff)

    def get_strike_for_breakeven_credit(self, breakeven_point, short_call_strike, offset, risk = math.inf, threshold = 1):
        diff = offset - (breakeven_point - short_call_strike)
        ideal_diff = -math.inf
        ideal_strike = breakeven_point
        ideal_premium = breakeven_point

        min_threshold = -threshold
        min_diff = None
        min_strike = breakeven_point
        min_premium = breakeven_point
        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]
            if strike_price > breakeven_point:
                sum = diff - strike_premium
                max_loss = strike_price - short_call_strike - offset + strike_premium
                if max_loss < risk:
                    if sum > ideal_diff:
                        ideal_strike = strike_price
                        ideal_diff = sum
                        ideal_premium = strike_premium 
                    
                    if min_threshold <= sum <= threshold and strike_premium < min_premium: 
                        min_diff = sum
                        min_strike = strike_price
                        min_premium = strike_premium 

        if not min_diff:
            threshold += 1
            return self.get_strike_for_breakeven_credit(breakeven_point, short_call_strike, offset, risk, threshold)
        else:
            return(ideal_strike, ideal_premium, ideal_diff, min_strike, min_premium, min_diff)


class CallOption:
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
    
    def implied_price_range(self):
        result = bin_search_closest(self.underlying.get_price(), self.strikes)
        itm = self.strikes[result[1]]
        otm = self.strikes[result[0]]
        itm = self.get_option_for_strike(itm)
        otm = self.get_option_for_strike(otm)

        itm_iv = itm.get_iv()
        itm_vol = itm.get_interest()
        otm_iv = otm.get_iv()
        otm_vol = otm.get_interest()
        return (itm, otm)
    
    def get_hedge_stike(self, risked_amount, entry_point, break_point):
        break_point_difference = entry_point - break_point
        break_amount = entry_point

        for strike in self.data:
            max_loss = entry_point - strike["strike"] + strike["lastPrice"]
            break_point_loss = break_point_difference + strike["lastPrice"]
            if break_point_loss < break_amount and strike["strike"] <= entry_point and max_loss < risked_amount:
                break_amount = break_point_loss
                strike_price2 = strike["strike"]
            if max_loss < risked_amount and strike["strike"] <= entry_point:
                risked_amount = max_loss
                strike_price = strike["strike"]
            
        return (risked_amount, strike_price, break_amount, strike_price2)

        # ideally do a graph for best strike price to buy from current price to break point in a graph or wtv

    def get_strike_for_breakeven_debit(self, breakeven_point, risk = math.inf, offset = 0, threshold = 1):
        max_premium = risk - offset
        ideal_diff = 0
        ideal_strike = breakeven_point
        ideal_premium = breakeven_point

        min_threshold = -threshold
        min_diff = None
        min_strike = breakeven_point
        min_premium = breakeven_point
        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]
            if strike_price > breakeven_point:
                sum = strike_price - breakeven_point  + offset - strike_premium 
                if strike_premium  < max_premium:
                    if sum > ideal_diff:
                        ideal_strike = strike_price
                        ideal_diff = sum
                        ideal_premium = strike_premium 
                    
                    if min_threshold <= sum <= threshold and strike_premium < min_premium: 
                        min_diff = sum
                        min_strike = strike_price
                        min_premium = strike_premium 

        if not min_diff:
            threshold += 1
            return self.get_strike_for_breakeven_debit(breakeven_point, risk, offset, threshold)
        else:
            return(ideal_strike, ideal_premium, ideal_diff, min_strike, min_premium, min_diff)

    def get_strike_for_breakeven_credit(self, breakeven_point, short_put_strike, offset, risk = math.inf, threshold = 1):
        diff = offset - (short_put_strike - breakeven_point)
        ideal_diff = -math.inf
        ideal_strike = breakeven_point
        ideal_premium = breakeven_point

        min_threshold = -threshold
        min_diff = None
        min_strike = breakeven_point
        min_premium = breakeven_point
        for strike in self.data:
            strike_price = strike["strike"]
            strike_premium = strike["lastPrice"]
            max_loss = short_put_strike - strike_price + strike_premium - offset
            if strike_price < breakeven_point:
                sum = diff - strike_premium
                if max_loss  < risk:
                    if sum > ideal_diff:
                        ideal_strike = strike_price
                        ideal_diff = sum
                        ideal_premium = strike_premium 
                    
                    if min_threshold <= sum <= threshold and strike_premium < min_premium: 
                        min_diff = sum
                        min_strike = strike_price
                        min_premium = strike_premium 

        if not min_diff:
            threshold += 1
            return self.get_strike_for_breakeven_credit(breakeven_point, short_put_strike, offset, risk, threshold)
        else:
            return(ideal_strike, ideal_premium, ideal_diff, min_strike, min_premium, min_diff)

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


print(Call("aapl", month = 8, day = 20).get_strike_for_breakeven_credit(120, 110, 24.2, 40))
print(Put("aapl", month = 8, day = 20).get_strike_for_breakeven_credit(140, 160, 27.25, 10))
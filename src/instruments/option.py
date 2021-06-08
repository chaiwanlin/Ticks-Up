from utility.search import  bin_search_closest
from instruments.instrument import Instrument
from instruments.stock import Stock
from instruments.constants import YAHOO_OPTION
import urllib.request
import urllib.response
import json
import datetime


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

        self.options = data["options"][0]
        self.strikes = data["strikes"]

        # print(data["optionChain"]["result"][0])
        super().__init__(ticker, Stock(ticker))

    def get_strikes(self):
        return self.strikes

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
            return CallOption(self.ticker, self.underlying, data)
        except UnboundLocalError:
            print("no availible data")


class PutOption:
    def init(self, ticker, underlying, data):
        self.ticker = ticker
        self.underlying = underlying
        self.price = data["lastPrice"]
        self.volume = data["volume"]
        self.interest = data["openInterest"]
        self.bid = data["bid"]
        self.ask = data["ask"]
        self.implied_volatility = data["1.46875265625"]

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


print(Call("aapl").get_option_for_strike(120).get_interest())
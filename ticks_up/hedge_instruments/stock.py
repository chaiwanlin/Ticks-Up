from .constants import YAHOO_STOCK
from .instrument import Instrument
import urllib.request
import urllib.response
import urllib.error
import json
from bs4 import BeautifulSoup 
import urllib.request as rq

class Stock(Instrument):

    # urllib.error.URLError if unconnectable/no such site
    def __init__(self, ticker):
        url = f"{YAHOO_STOCK}{ticker}?modules=price%2CsummaryDetail"
        try:
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            result = data["quoteSummary"]["result"][0]
            
            self.price = float(result["price"]["regularMarketPrice"]["fmt"].replace(",", ""))

            self.dividend = 0
            dividend = result["summaryDetail"]["dividendRate"]
            if dividend:
                self.dividend = dividend["raw"]/100

            # Assigns name of exchange in uppercase (only considering NYSE and NASDAQ)
            exchange_name = result["price"]["exchangeName"]
            if exchange_name == 'NasdaqGS':
                self.exchange = 'NASDAQ'
            else:
                self.exchange = exchange_name
        except (IndexError, urllib.error.HTTPError):
            raise LookupError("invalid ticker :D")

        super().__init__(ticker, self)

    def get_price(self):
        return self.price

    def get_exchange(self):
        return self.exchange

    def parse_stock(ticker):
        ticker = ticker.upper()
        request = rq.urlopen(f"https://www.tradingview.com/symbols/{ticker}/")
        soup = BeautifulSoup(request.read(), 'html.parser')

        result = soup.find("span", class_ = "tv-symbol-header__exchange").text.replace(" ", "")

        try:
            f = open('index.json', "r")
            data = json.load(f)
            result = ticker + data[result]
            return result
        except KeyError:
            raise LookupError("invalid ticker :D")

        
# Stock("S68.SI")
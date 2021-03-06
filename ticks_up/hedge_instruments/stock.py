from .constants import YAHOO_STOCK
from .instrument import Instrument
import urllib.request
import urllib.response
import urllib.error
import json
from bs4 import BeautifulSoup 
import urllib.request as rq
from pathlib import Path
import os

class Stock(Instrument):

    # urllib.error.URLError if unconnectable/no such site
    def __init__(self, ticker):
        ticker_html = Stock.parse_stock_for_yahoo(ticker)
        url = f"{YAHOO_STOCK}{ticker_html}?modules=price%2CsummaryDetail"
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

    def get_stock_exchange(ticker):
        try:
            ticker = ticker.upper()
            request = rq.urlopen(f"https://www.tradingview.com/symbols/{ticker}/")
            soup = BeautifulSoup(request.read(), 'html.parser')

            return soup.find("span", class_ = "tv-symbol-header__exchange").text.replace(" ", "")
        except Exception as e:
            print(e)
            raise LookupError("invalid ticker :D")
        
    def parse_stock_for_yahoo(ticker):
        try:
            result = Stock.get_stock_exchange(ticker)
            f = open(os.path.join(Path(__file__).resolve().parent.parent, './static/json_files/index.json'), "r")
            data = json.load(f)
            result = ticker + data[result]
            return result
        except KeyError:
            raise LookupError("invalid ticker :D")



        


        
# Stock("S68.SI")
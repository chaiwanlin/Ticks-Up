from instruments.constants import YAHOO_STOCK
from instruments.instrument import Instrument
import urllib.request
import urllib.response
import json


class Stock(Instrument):

    def __init__(self, ticker):
        url = f"{YAHOO_STOCK}{ticker}?modules=price%2CsummaryDetail"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        result = data["quoteSummary"]["result"][0]
        self.price = result["price"]["regularMarketPrice"]

        # Assigns name of exchange in uppercase (only considering NYSE and NASDAQ)
        exchange_name = result["price"]["exchangeName"]
        if exchange_name == 'NasdaqGS':
            self.exchange = 'NASDAQ'
        else:
            self.exchange = exchange_name

        super().__init__(ticker, self)

    def get_price(self):
        return float(self.price["fmt"])

    def get_exchange(self):
        return self.exchange
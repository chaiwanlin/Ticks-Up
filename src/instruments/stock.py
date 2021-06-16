from instruments.constants import YAHOO_STOCK
from instruments.instrument import Instrument
import urllib.request
import urllib.response
import json

class Stock(Instrument):

    def init(self, ticker):

        url = f"{YAHOO_STOCK}{ticker}?modules=price%2CsummaryDetail"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        result = data["quoteSummary"]["result"][0]
        self.price = result["price"]["regularMarketPrice"]

        super().init(ticker, self)

    def get_price(self):
        return float(self.price["fmt"])
from portfolio.portfolio_constants import BEAR, BULL, LONG, SHORT, STRADDLE, CREDIT, DEBIT
from portfolio.portfolio_instrument import Instrument, Stock, Put, Call
from instruments.stock import Stock as Stock_Data

class Overall_Position:

    def __init__(self, ticker, sector, stocks, options):
        self.sector = sector
        self.ticker = ticker
        self.stocks = stocks
        self.options = options

    
    def get_overall_position(self):
        overall_capital_invested = self.stocks.capital_invested + self.options.capital_invested
        overall_capital_collateral = self.stocks.capital_collateral + self.options.capital_collateral
        

class Stock_Position:

    def __init__(self, ticker, long_positions, short_positions, margin, margin_value = 0):
        self.ticker = ticker
        self.long_positions = long_positions
        self.short_positions = short_positions
        self.margin = margin
        self.margin_amount = margin_value

        price = Stock_Data(ticker).get_price()

        self.capital_invested = 0
        self.capital_collateral = 0

        for e in self.long_positions:
            self.capital_invested += e.cost
        
        if margin:
            for e in self.short_positions:
                self.capital_invested += e.cost + margin_value * price

class Option_Position:

    def __init__(self, ticker, short_call, long_call, short_puts, long_puts, spreads, margin, margin_value = 0):
        self.ticker = ticker
        self.short_calls = short_call
        self.long_calls = long_call
        self.short_puts = short_puts
        self.long_puts = long_puts
        self.spreads = spreads
        self.margin = margin
        self.margin_amount = margin_value

        price = Stock_Data(ticker).get_price()

        self.get_option_positions()
        
        self.capital_invested = 0
        self.capital_collateral = 0

        for e in self.long_calls:
            self.capital_invested += e.cost

        for e in self.long_puts:
            self.capital_invested += e.cost   

        for e in self.spreads:
            if e.type == CREDIT:
                self.capital_collateral += e.risk 

            if e.type == DEBIT:
                self.capital_invested += e.cost 
        
        if margin:
            for e in self.short_calls:
                otm = e.strike - price if e.strike - price else 0
                self.capital_collateral += max(0.2 * price - otm, 0.1 * price) * 100

            for e in self.short_puts:
                otm = e.strike - price if e.strike - price else 0
                self.capital_collateral += max(0.2 * price - otm, 0.1 * price) * 100
        else:
            for e in self.short_calls:
                self.capital_collateral += e.strike * 100

    def get_option_positions(self):

        self.short_puts.sort(key = lambda x : x.strike)
        self.long_puts.sort(key = lambda x : x.strike, reversed = True)
        self.short_calls.sort(key = lambda x : x.strike)
        self.long_calls.sort(key = lambda x : x.strike) 

        # for put in self.long_puts:
        #     count = put.quantity
        #     if not self.short_puts:
        #         index = 0
        #         for sput in self.short_puts:
        #             if count == 0:
        #                 break
        #             if put < sput:
        #                 if count < sput.quantity:
        #                 elif sput.quantity < count:
        #                 else:

        

lst = [Stock(LONG, 3), Stock(LONG, 5), Stock(LONG, 2)]

Overall_Position("AAPL", lst).get_overall_position()
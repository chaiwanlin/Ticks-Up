from portfolio_constants import BEAR, BULL, LONG, SHORT, STRADDLE, CREDIT, DEBIT
from portfolio_instrument import Instrument, Stock, Put, Call
from ticks_up.hedge_instruments.stock import Stock as Stock_Data

class Overall_Position:

    def __init__(self, ticker, sector, industry, stocks, options):
        self.sector = sector
        self.industry = industry
        self.ticker = ticker
        self.stocks = stocks
        self.options = options

        self.capital_invested = self.stocks.capital_invested + self.options.capital_invested
        self.capital_collateral = self.stocks.capital_collateral + self.options.capital_collateral
        self.value = self.stocks.value + self.options.value
        self.cost_to_cover = self.stocks.cost_to_cover + self.options.cost_to_cover
        self.short_PL = self.stocks.short_PL + self.options.short_PL
          
class Stock_Position:

    def __init__(self, ticker, long_positions, short_positions, margin, margin_value = 0.2):
        self.ticker = ticker
        self.long_positions = long_positions
        self.short_positions = short_positions
        self.margin = margin
        self.margin_amount = margin_value

        price = Stock_Data(ticker).get_price()

        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0

        for e in self.long_positions:
            self.capital_invested += e.cost
            self.value += e.value
        
        if margin:
            for e in self.short_positions:
                self.capital_invested += e.cost + margin_value * price
                self.cost_to_cover += price
                self.short_PL += e.cost - price

class Option_Position:

    def __init__(self, ticker, short_call, long_call, short_puts, long_puts, spreads, margin, margin_value = 0.2):
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
        self.cost_to_cover = 0
        self.short_PL = 0

        for e in self.long_calls:
            self.capital_invested += e.cost
            self.value += e.value

        for e in self.long_puts:
            self.capital_invested += e.cost   
            self.value += e.value

        for e in self.spreads:
            if e.type == CREDIT:
                self.capital_collateral += e.risk 
                self.cost_to_cover += e.value
                self.short_PL += e.cost - e.value

            if e.type == DEBIT:
                self.capital_invested += e.cost 
                self.value += e.value
        
        if margin:
            for e in self.short_calls:
                otm = e.strike - price if e.strike - price else 0
                self.capital_collateral += max(0.2 * price - otm, 0.1 * price) * 100
                self.cost_to_cover += e.value
                self.short_PL += e.cost - e.value

            for e in self.short_puts:
                otm = e.strike - price if e.strike - price else 0
                self.capital_collateral += max(0.2 * price - otm, 0.1 * price) * 100
                self.cost_to_cover += e.value
                self.short_PL += e.cost - e.value
        else:
            for e in self.short_puts:
                self.capital_collateral += e.strike * 100
                self.cost_to_cover += e.value
                self.short_PL += e.cost - e.value

    def get_option_positions(self):

        self.short_puts.sort(key = lambda x : x.strike, reversed = True)
        self.long_puts.sort(key = lambda x : x.strike, reversed = True)
        self.short_calls.sort(key = lambda x : x.strike)
        self.long_calls.sort(key = lambda x : x.strike) 

        # for call in self.short_calls:
        #     count = call.quantity
        #     if not self.short_puts:
        #         index = 0
        #         for scall in self.short_calls:
        #             if count == 0:
        #                 break
        #             if call < scall:
        #                 if count < scall.quantity:
        #                 elif scall.quantity < count:
        #                 else:   

# lst = [Stock(LONG, 3), Stock(LONG, 5), Stock(LONG, 2)]

# Overall_Position("AAPL", lst)
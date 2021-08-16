from .portfolio_constants import CREDIT, DEBIT, UNKNOWN
from .portfolio_instrument import Bear, Bull
from hedge_instruments.stock import Stock as Stock_Data


class OverallPosition:
    # ticker: string (e.g. "AMC")
    # sector: string choice
    # industry: string choice
    # stocks: StockPosition
    # options: OptionPosition
    def __init__(self, ticker, stocks, options, sector = UNKNOWN, industry = UNKNOWN):
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

        self.total_cost = self.capital_invested + self.capital_collateral
        self.total_value = self.value + self.capital_collateral + self.short_PL


class StockPosition:

    # ticker: string (e.g. "AMC")
    # long_positions: list of "LONG" Stock objects
    # short_positions: list of "SHORT" Stock objects
    # margin: Boolean
    # margin_value: float (0 <= x)
    def __init__(self, ticker, long_positions, short_positions, margin = False, margin_value = 0.2):
        self.ticker = ticker
        self.long_positions = long_positions
        self.short_positions = short_positions
        self.margin = margin
        self.margin_amount = margin_value

        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0

        for e in self.long_positions:
            self.capital_invested += e.lot_cost
            self.value += e.lot_value
        
        if margin:
            for e in self.short_positions:
                self.capital_collateral += e.lot_cost + margin_value * e.lot_value
                self.cost_to_cover += e.lot_value
                self.short_PL += e.short_PL

        self.total_cost = self.capital_invested + self.capital_collateral
        self.total_value = self.value + self.capital_collateral + self.short_PL


class OptionPosition:

    # ticker: string (e.g. "AMC")
    # short_call: list of "SHORT" Call objects
    # long_call: list of "LONG" Call objects
    # short_puts: list of "SHORT" Put objects
    # long_puts: list of "LONG" Put objects
    # spreads: list of Spread object
    # margin: Boolean
    # margin_value: float (0 <= x)
    def __init__(self, ticker, short_call, long_call, short_puts, long_puts, spreads, margin = False, margin_value = 0.2):
        self.ticker = ticker
        self.short_calls = short_call
        self.long_calls = long_call
        self.short_puts = short_puts
        self.long_puts = long_puts
        self.spreads = spreads
        self.margin = margin
        self.margin_amount = margin_value

        price = Stock_Data(ticker).get_price()

        self.get_option_positions_spread()
        
        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0

        for e in self.long_calls:
            self.capital_invested += e.lot_cost
            self.value += e.lot_value

        for e in self.long_puts:
            self.capital_invested += e.lot_cost   
            self.value += e.lot_value

        for e in self.spreads:
            if e.type == CREDIT:
                self.capital_collateral += e.lot_risk 
                self.cost_to_cover += e.lot_value
                self.short_PL += e.short_PL

            if e.type == DEBIT:
                self.capital_invested += e.lot_cost
                self.value += e.lot_value
        
        if margin:
            for e in self.short_calls:
                otm = e.strike_price - price if e.strike_price - price else 0
                self.capital_collateral += max(0.2 * (price - otm), 0.1 * price) * e.leveraged_quantity
                self.cost_to_cover += e.lot_value
                self.short_PL += e.short_PL

            for e in self.short_puts:
                otm = e.strike_price - price if e.strike_price - price else 0
                self.capital_collateral += max(0.2 * (price - otm), 0.1 * price) * e.leveraged_quantity
                self.cost_to_cover += e.lot_value
                self.short_PL += e.short_PL
        else:
            for e in self.short_puts:
                self.capital_collateral += e.strike_price * e.leveraged_quantity
                self.cost_to_cover += e.lot_value
                self.short_PL += (e.cost - e.value) * e.leveraged_quantity

        self.total_cost = self.capital_invested + self.capital_collateral
        self.total_value = self.value + self.capital_collateral + self.short_PL

    def get_option_positions_spread(self):
        self.short_puts.sort(key = lambda x : x.strike_price, reverse = True)
        self.long_puts.sort(key = lambda x : x.strike_price, reverse = True)
        self.short_calls.sort(key = lambda x : x.strike_price)
        self.long_calls.sort(key = lambda x : x.strike_price)

        short_puts = self.short_puts
        long_puts = self.long_puts
        short_calls = self.short_calls
        long_calls = self.long_calls

        spreads = []

        short_empty = True
        long_empty = True

        while short_calls and long_calls:
            if short_empty:
                short_call = short_calls.pop(0)
                short_empty = False
            if long_empty:
                long_call = long_calls.pop(0)
                long_empty = False

            if short_call.strike < long_call.strike:
                if short_call.quantity < long_call.quantity:
                    n = short_call.quantity
                    extracted_long_call = long_call.extract_quantity(n)
                    spreads.append(Bear(CREDIT, short_call, extracted_long_call)) 
                    short_empty = True
                    
                elif short_call.quantity > long_call.quantity:
                    n = long_call.quantity
                    extracted_short_call = short_call.extract_quantity(n)
                    spreads.append(Bear(CREDIT, extracted_short_call, long_call))
                    long_empty = True

                else:
                    spreads.append(Bear(CREDIT, short_call, long_call))  
                    short_empty = True
                    long_empty = True      
                
                    # bull debit spread
            elif short_call.strike > long_call.strike:
                if short_call.quantity < long_call.quantity:
                    n = short_call.quantity
                    extracted_long_call = long_call.extract_quantity(n)
                    spreads.append(Bull(DEBIT, short_call, extracted_long_call))
                    short_empty = True 

                elif short_call.quantity > long_call.quantity:
                    n = long_call.quantity
                    extracted_short_call = short_call.extract_quantity(n)
                    spreads.append(Bull(DEBIT, extracted_short_call, long_call)) 
                    long_empty = True
                    
                else:
                    spreads.append(Bull(DEBIT, short_call, long_call))
                    short_empty = True
                    long_empty = True
            # cancels out
            else:
                if short_call.quantity < long_call.quantity:
                    n = short_call.quantity
                    extracted_long_call = long_call.extract_quantity(n)
                    short_empty = True 

                elif short_call.quantity > long_call.quantity:
                    n = long_call.quantity
                    extracted_short_call = short_call.extract_quantity(n)
                    long_empty = True
                    
                else:
                    short_empty = True
                    long_empty = True

        short_empty = True
        long_empty = True
            
        while short_puts and long_puts:
            if short_empty:
                short_put = short_puts.pop(0)
                short_empty = False
            if long_empty:
                long_put = long_calls.pop(0)
                long_empty = False

                # bear debit 
            if short_put.strike < long_put.strike:
                if short_put.quantity < long_put.quantity:
                    n = short_put.quantity
                    extracted_long_put = long_put.extract_quantity(n)
                    spreads.append(Bear(DEBIT, short_put, extracted_long_put)) 
                    short_empty = True
                    
                elif short_put.quantity > long_put.quantity:
                    n = short_put.quantity
                    extracted_short_put = short_put.extract_quantity(n)
                    spreads.append(Bear(DEBIT, extracted_short_put, long_put))
                    long_empty = True

                else:
                    spreads.append(Bear(DEBIT, short_put, long_put))  
                    short_empty = True
                    long_empty = True      
                
                    # bull credit spread
            elif short_put.strike > long_put.strike:
                if short_put.quantity < long_put.quantity:
                    n = short_put.quantity
                    extracted_long_put = long_put.extract_quantity(n)
                    spreads.append(Bull(CREDIT, short_put, extracted_long_put))
                    short_empty = True 

                elif short_put.quantity > long_put.quantity:
                    n = long_put.quantity
                    extracted_short_put = short_put.extract_quantity(n)
                    spreads.append(Bull(CREDIT, extracted_short_put, long_put)) 
                    long_empty = True
                    
                else:
                    spreads.append(Bull(CREDIT, short_call, long_put))
                    short_empty = True
                    long_empty = True
            # cancels out
            else:
                if short_put.quantity < long_put.quantity:
                    n = short_put.quantity
                    extracted_long_put = long_put.extract_quantity(n)
                    short_empty = True 

                elif short_put.quantity > long_put.quantity:
                    n = long_put.quantity
                    extracted_short_call = short_put.extract_quantity(n)
                    long_empty = True
                    
                else:
                    short_empty = True
                    long_empty = True

        self.short_puts = short_puts
        self.long_puts = long_puts
        self.short_calls = short_calls
        self.long_calls = long_calls
        self.spreads.extend(spreads)


# scalls = [Stock(LONG, 3), Stock(LONG, 5), Stock(LONG, 2)]
# lcalls = []


# Overall_Position("AAPL", lst)
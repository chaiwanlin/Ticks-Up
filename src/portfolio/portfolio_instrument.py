from portfolio.portfolio_constants import SHORT, LONG, BEAR, BULL, STRADDLE, NEUTRAL
from instruments.stock import Stock as Stock_Data
import math

class Asset:
    def __init__(self, quantity, cost, value):
        self.quantity = quantity
        self.cost = cost
        self.value = value

    def get_quantity(self):
        return self.quantity    

class Cash(Asset):
    def __init__(self, quantity):
        super().__init__(quantity)

class Instrument(Asset):

    def __init__(self, position, quantity, cost, value):
        super().__init__(quantity, cost, value)
        self.position = position
        self.cost = cost
        self.leveraged_quantity = -math.inf
        self.outlook = None
        
    def get_position(self):
        return self.position

    def get_cost(self):
        return self.cost

    def get_leveraged_quantity(self):
        return self.leveraged_quantity
  
class Stock(Instrument):

    def __init__(self, position, quantity, cost, value):
        super().__init__(position, quantity, cost, value)
        self.leveraged_quantity = quantity

        if position == LONG:
            self.outlook = BULL
            self.risk = cost
        elif position == SHORT:
            self.outlook ==  BEAR
            self.risk = math.inf
    
class Option(Instrument):

    def __init__(self, position, quantity, cost, strike_price, expiry, value):
        super().__init__(position, quantity, cost, value)
        self.expiry = expiry
        self.leveraged_quantity = quantity * 100
        self.strike_price = strike_price

class Put(Option):

    def __init__(self, position, quantity, cost, strike_price, expiry, value):
        super().__init__(position, quantity, cost, strike_price, expiry, value)
        if position == LONG:
            self.outlook = BEAR
        elif position == SHORT:
            self.outlook ==  BULL

class Call(Option):

    def __init__(self, position, quantity, cost, strike_price, expiry, value):
        super().__init__(position, quantity, cost, strike_price, expiry, value)
        if position == LONG:
            self.outlook = BULL
        elif position == SHORT:
            self.outlook ==  BEAR

class Spread(Instrument):

    def __init__(self, type, quantity, cost, profit, value):
        super().__init__(LONG, quantity, cost, value)
        self.type = type
        self.profit = profit
        self.leveraged_quantity = quantity * 100

class Bear(Spread):
    
    def __init__(self, type, quantity, cost, profit, breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Bull(Spread):

    def __init__(self, type, quantity, cost, profit, breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Neutral(Spread):

    def __init__(self, type, quantity, cost, profit, lower_breakeven, upper_breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.lower_breakeven = lower_breakeven
        self.upper_breakeven = upper_breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Straddle(Spread):
    
    def __init__(self, type, quantity, cost, profit, lower_breakeven, upper_breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.lower_breakeven = lower_breakeven
        self.upper_breakeven = upper_breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Collar(Spread): 
    
    def __init__(self, type, quantity, cost, profit, breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Hedged_stock(Spread):
    def __init__(self, type, quantity, cost, profit, breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Covered_Call(Spread):
    def __init__(self, type, quantity, cost, profit, breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper
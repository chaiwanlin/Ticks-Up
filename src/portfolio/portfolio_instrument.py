from datetime import datetime
from numpy import short
from src.portfolio.portfolio_constants import CREDIT, DEBIT
from portfolio.portfolio_constants import SHORT, LONG, BEAR, BULL, STRADDLE, NEUTRAL
from instruments.stock import Stock as Stock_Data
import instruments.option as op
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
        self.risk = None
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
            self.risk = cost
        elif position == SHORT:
            self.outlook ==  BULL
            self.risk = math.inf

class Call(Option):

    def __init__(self, position, quantity, cost, strike_price, expiry, value):
        super().__init__(position, quantity, cost, strike_price, expiry, value)
        if position == LONG:
            self.outlook = BULL
            self.risk = cost
        elif position == SHORT:
            self.outlook ==  BEAR
            self.risk = cost

class Spread(Instrument):

    def __init__(self, type, quantity, cost, profit, value):
        super().__init__(LONG, quantity, cost, value)
        self.type = type
        self.profit = profit
        self.leveraged_quantity = quantity * 100

class Bear(Spread):
    
    def __init__(self, type, short_leg, long_leg):
        quantity = short_leg.quantity
        expiry = short_leg.expiry
        if type == CREDIT:
            calls = op.Call(expiry.day, expiry.month, expiry.year)

            credit = short_leg.cost - long_leg.cost
            max_loss = long_leg.strike_price - short_leg.strike_price - credit
            long_premium = calls.get_option_for_strike(long_leg.strike_price).get_price()
            short_premium = calls.get_option_for_strike(short_leg.strike_price).get_price()

            cost = max_loss
            profit = credit
            breakeven = short_leg + credit
            lower_leg = short_leg.strike_price
            upper_leg = long_leg.strike_price
            # cost to cover
            value = short_premium - long_premium
            risk = max_loss
        elif type == DEBIT:
            puts = op.Put(date.day, date.month, date.year)

            debit = long_leg.cost - short_leg.cost
            max_profit = long_leg.strike_price - short_leg.strike_price - debit
            long_premium = puts.get_option_for_strike(long_leg.strike_price).get_price()
            short_premium = puts.get_option_for_strike(short_leg.strike_price).get_price()

            cost = debit
            profit = max_profit
            breakeven = long_leg.strike_price + debit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            value = long_premium - short_premium
            risk = debit
        else:
            raise ValueError("Not valid spread type: Bear")

        super().__init__(type, quantity, cost, profit, value)
        self.risk = risk
        self.expiry = expiry
        self.breakeven = breakeven
        self.lower_leg = lower_leg
        self.upper_leg = upper_leg

class Bull(Spread):

    def __init__(self, type, short_leg, long_leg):
        quantity = short_leg.quantity
        expiry = short_leg.expiry

        if type == CREDIT:
            puts = op.Put(expiry.day, expiry.month, expiry.year)

            credit = short_leg.cost - long_leg.cost
            max_loss =  short_leg.strike_price - long_leg.strike_price - credit
            long_premium = puts.get_option_for_strike(long_leg.strike_price).get_price()
            short_premium = puts.get_option_for_strike(short_leg.strike_price).get_price()

            cost = max_loss
            profit = credit
            breakeven = short_leg - credit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            # cost to cover
            value = short_premium - long_premium
            risk = max_loss
        elif type == DEBIT:
            puts = op.Put(expiry.day, expiry.month, expiry.year)

            debit = long_leg.cost - short_leg.cost
            max_profit = long_leg.strike_price - short_leg.strike_price - debit
            long_premium = puts.get_option_for_strike(long_leg.strike_price).get_price()
            short_premium = puts.get_option_for_strike(short_leg.strike_price).get_price()

            cost = debit
            profit = max_profit
            breakeven = long_leg.strike_price + debit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            value = long_premium - short_premium
            risk = debit
        else:
            raise ValueError("Not valid spread type: Bear")

        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
        self.breakeven = breakeven
        self.lower_bound = lower
        self.upper_bound = upper

class Neutral(Spread):

    def __init__(self, type, quantity, cost, profit, lower_breakeven, upper_breakeven, lower, upper, expiry, value):
        super().__init__(type, quantity, cost, profit, value)
        self.expiry = expiry
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
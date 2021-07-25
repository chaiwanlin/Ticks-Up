from datetime import datetime
from numpy import short
from portfolio_constants import *
from ticks_up.hedge_instruments.stock import Stock as Stock_Data
import ticks_up.hedge_instruments.option as op
import math

class Asset:
    def __init__(self, quantity, cost, value):
        self.quantity = quantity
        self.cost = cost
        self.value = value

    def get_quantity(self):
        return self.quantity    

    def reduce_quantity(self, n):
        self.quanity -= n


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

    def __init__(self, ticker, position, quantity, cost):
        value = Stock_Data(ticker).get_price()
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

    def __init__(self, ticker, position, quantity, cost, strike_price, expiry):
        puts = op.Put(ticker, expiry.day, expiry.month, expiry.year)
        value = puts.get_option_for_strike(strike_price)
        super().__init__(position, quantity, cost, strike_price, expiry, value)

        self.ticker = ticker
        if position == LONG:
            self.outlook = BEAR
            self.risk = cost
        elif position == SHORT:
            self.outlook ==  BULL
            self.risk = math.inf

    def extract_quantity(self, n):
        self.quantity -= n
        return self.__init__(self.ticker, self.position, n, self.cost, self.strike_price, self.expiry)


class Call(Option):

    def __init__(self, ticker, position, quantity, cost, strike_price, expiry):
        calls = op.Call(ticker, expiry.day, expiry.month, expiry.year)
        value = calls.get_option_for_strike(strike_price)
        super().__init__(position, quantity, cost, strike_price, expiry, value)
        
        self.ticker = ticker
        if position == LONG:
            self.outlook = BULL
            self.risk = cost
        elif position == SHORT:
            self.outlook ==  BEAR
            self.risk = cost
    
    def extract_quantity(self, n):
        self.quantity -= n
        return self.__init__(self.ticker, self.position, n, self.cost, self.strike_price, self.expiry)

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
            credit = short_leg.cost - long_leg.cost
            max_loss = long_leg.strike_price - short_leg.strike_price - credit
            long_premium = long_leg.value
            short_premium = short_leg.value

            cost = max_loss
            profit = credit
            breakeven = short_leg + credit
            lower_leg = short_leg.strike_price
            upper_leg = long_leg.strike_price
            # cost to cover
            value = short_premium - long_premium
            risk = max_loss
        elif type == DEBIT:
            debit = long_leg.cost - short_leg.cost
            max_profit = long_leg.strike_price - short_leg.strike_price - debit
            long_premium = long_leg.value
            short_premium = short_leg.value

            cost = debit
            profit = max_profit
            breakeven = long_leg.strike_price - debit
            lower_leg = short_leg.strike_price
            upper_leg = long_leg.strike_price
            value = long_premium - short_premium
            risk = debit
        else:
            raise ValueError("Not valid spread type: Bear")

        super().__init__(type, quantity, cost, profit, value)
        self.risk = risk
        self.expiry = expiry
        self.breakeven = breakeven
        self.lower_bound = lower_leg
        self.upper_bound = upper_leg


class Bull(Spread):

    def __init__(self, type, short_leg, long_leg):
        quantity = short_leg.quantity
        expiry = short_leg.expiry

        if type == CREDIT:
            credit = short_leg.cost - long_leg.cost
            max_loss =  short_leg.strike_price - long_leg.strike_price - credit
            long_premium = long_leg.value
            short_premium = short_leg.value

            cost = max_loss
            profit = credit
            breakeven = short_leg - credit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            # cost to cover
            value = short_premium - long_premium
            risk = max_loss
        elif type == DEBIT:
            calls = op.Put(expiry.day, expiry.month, expiry.year)

            debit = long_leg.cost - short_leg.cost
            max_profit = short_leg.strike_price - long_leg.strike_price - debit
            long_premium = calls.get_option_for_strike(long_leg.strike_price).get_price()
            short_premium = calls.get_option_for_strike(short_leg.strike_price).get_price()

            cost = debit
            profit = max_profit
            breakeven = long_leg.strike_price + debit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            value = long_premium - short_premium
            risk = debit
        else:
            raise ValueError("Not valid spread type: Bull")

        super().__init__(type, quantity, cost, profit, value)
        self.risk = risk
        self.expiry = expiry
        self.breakeven = breakeven
        self.lower_bound = lower_leg
        self.upper_bound = upper_leg

class Condor(Spread):

    def __init__(self, type, bear_spread, bull_spread):
        quantity = bear_spread.quantity
        expiry = bear_spread.expiry

        if type == PUT:
            return None
        elif type == CALL:
            return None
        elif type == IRON:
            credit = bear_spread.profit + bull_spread.profit
            max_loss = bear_spread.cost - bull_spread.profit

            cost = max_loss
            profit = credit
            breakeven_bear = bull_spread.upper_bound - credit
            breakeven_bull = bear_spread.lower_bound + credit
            # cost to cover
            value = bear_spread.value + bull_spread.value
        else:
            raise ValueError("Condor")

        super().__init__(type, quantity, cost, profit, value)
        self.risk = max_loss
        self.expiry = expiry
        self.breakeven_bear = breakeven_bear
        self.breakeven_bull = breakeven_bull
        self.bear_spread = bear_spread
        self.bull_spread = bull_spread


class Straddle(Spread):
    
    def __init__(self, type, bear_spread, bull_spread):
        quantity = bear_spread.quantity
        expiry = bear_spread.expiry

        if type == PUT:
            return None
        elif type == CALL:
            return None
        elif type == IRON:
            debit = bear_spread.cost + bear_spread.cost

            cost = debit
            profit = bear_spread.profit - bull_spread.cost
            breakeven_bear = bear_spread.upper_bound - debit
            breakeven_bull = bull_spread.lower_bound + debit
            value = bear_spread.value + bull_spread.value
        else:
            raise ValueError("Not valid spread type: Straddle")

        super().__init__(type, quantity, cost, profit, value)
        self.risk = debit
        self.expiry = expiry
        self.breakeven_bear = breakeven_bear
        self.breakeven_bull = breakeven_bull
        self.bear_spread = bear_spread
        self.bull_spread = bull_spread

class Collar(Spread): 
    
    def __init__(self, stock, long_put, short_call):
        quantity = long_put.quantity
        expiry = long_put.expiry

        cost = long_put.cost - short_call.cost
        max_loss = stock.cost - long_put.strike_price + cost
        
        profit = short_call.strike_price - stock.cost - cost
        breakeven = stock.cost + cost
        value = long_put.value - short_call.cost

        type = DEBIT if cost > 0 else CREDIT

        super().__init__(type, quantity, cost, profit, value)
        self.risk = max_loss
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = long_put.strike_price
        self.upper_bound = short_call.strike_price

class Hedged_stock(Spread):    
    def __init__(self, stock, long_put):
        quantity = long_put.quantity
        expiry = long_put.expiry

        cost = long_put.cost
        max_loss = stock.cost - long_put.strike_price + cost
        
        profit = math.inf
        breakeven = stock.cost + cost
        value = long_put.value

        super().__init__(DEBIT, quantity, cost, profit, value)
        self.risk = max_loss
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = long_put.strike_price
        self.upper_bound = math.inf

class Covered_Call(Spread):
    def __init__(self, stock, short_call):
        quantity = short_call.quantity
        expiry = short_call.expiry

        cost = short_call.cost
        
        profit = short_call.strike_price - stock.cost + cost
        breakeven = stock.cost - cost
        value = short_call.value

        super().__init__(CREDIT, quantity, cost, profit, value)
        self.risk = stock.cost
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = 0
        self.upper_bound = short_call.strike_price
from datetime import datetime
from numpy import short
from portfolio_constants import *
from hedge_instruments.stock import Stock as Stock_Data
import hedge_instruments.option as op
import math


class Asset:
    def __init__(self, quantity, cost, value):
        self.quantity = quantity
        self.cost = cost
        self.value = value

    def reduce_quantity(self, n):
        if self.quantity >= n:
            self.quantity -= n
        else:
            raise ValueError(f"asset has {self.quantity} left")


class Cash(Asset):
    def __init__(self, quantity):
        super().__init__(quantity)


class Instrument(Asset):

    def __init__(self, position, quantity, cost, value, leveraged_quantity):
        super().__init__(quantity, cost, value)
        self.position = position
        self.leveraged_quantity = leveraged_quantity
        self.risk = None
        self.outlook = None
        self.lot_value = self.leveraged_quantity * value
        self.lot_cost = self.leveraged_quantity * cost


class Stock(Instrument):

    # ticker: string (e.g. "AMC")
    # position: "LONG" or "SHORT"
    # quantity: float
    # cost: float
    def __init__(self, ticker, position, quantity, cost):
        if position == LONG or position == SHORT:
            self.ticker = ticker
            try:
                value = Stock_Data(ticker).get_price()
            except LookupError:
                value = cost
            super().__init__(position, quantity, cost, value, quantity)

            if position == LONG:
                self.outlook = BULL
                self.risk = cost
            elif position == SHORT:
                self.outlook ==  BEAR
                self.risk = math.inf
        else:
            raise ValueError("enter a valid position: LONG/SHORT")


class Option(Instrument):

    def __init__(self, position, quantity, cost, strike_price, expiry, value):
        super().__init__(position, quantity, cost, value, 100 * quantity)
        self.expiry = expiry
        self.strike_price = strike_price
    
    def get_expiry(self):
        return self.expiry.strftime('%Y-%m-%d')

class Call(Option):

    def __init__(self, ticker, position, quantity, cost, strike_price, expiry):
        if position == LONG or position == SHORT:
            try:
                calls = op.Call(ticker, expiry.year, expiry.month, expiry.day)
                value = calls.get_option_for_strike(strike_price).get_price()
            except LookupError:
                value = cost
            super().__init__(position, quantity, cost, strike_price, expiry, value)
            
            self.ticker = ticker
            if position == LONG:
                self.outlook = BULL
                self.risk = cost
            elif position == SHORT:
                self.outlook ==  BEAR
                self.risk = math.inf
        else:
            raise ValueError("enter a valid position: LONG/SHORT")

    
    def extract_quantity(self, n):
        self.reduce_quantity(n)
        return Call(self.ticker, self.position, n, self.cost, self.strike_price, self.expiry)

class Put(Option):

    # ticker: string (e.g. "AMC")
    # position: "LONG" or "SHORT"
    # quantity: int
    # cost: float
    # strike_price: float
    # expiry: python datetime object
    def __init__(self, ticker, position, quantity, cost, strike_price, expiry):
        if position == LONG or position == SHORT:
            try:
                puts = op.Put(ticker, expiry.year, expiry.month, expiry.day)
                value = puts.get_option_for_strike(strike_price).get_price()
            except LookupError:
                value = cost
            
            super().__init__(position, quantity, cost, strike_price, expiry, value)

            self.ticker = ticker
            if position == LONG:
                self.outlook = BEAR
                self.risk = cost
            elif position == SHORT:
                self.outlook ==  BULL
                self.risk = math.inf
        else:
            raise ValueError("enter a valid position: LONG/SHORT")
        
    def extract_quantity(self, n):
        self.reduce_quantity(n)
        return Put(self.ticker, self.position, n, self.cost, self.strike_price, self.expiry)


class Spread(Instrument):

    def __init__(self, type, quantity, cost, profit, value):
        if type == DEBIT:
            position = LONG
        else:
            position = SHORT
        super().__init__(position, quantity, cost, value, 100)
        self.type = type
        self.profit = profit

class Bear(Spread):

    # type: # "DEBIT" or "CREDIT"
    # short_leg/long_leg: Call/Put object
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
            breakeven = short_leg.strike_price - credit
            lower_leg = long_leg.strike_price
            upper_leg = short_leg.strike_price
            # cost to cover
            value = short_premium - long_premium
            risk = max_loss
        elif type == DEBIT:
            calls = op.Put(short_leg.ticker, expiry.year, expiry.month, expiry.day)

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

    # type: # "PUT" or "CALL" or "IRON"
    # bull_spread/bear_spread: Bull/Bear object
    def __init__(self, type, bear_spread, bull_spread):
        quantity = bear_spread.quantity
        expiry = bear_spread.expiry

        if type == PUT:
            return None
        elif type == CALL:
            return None
            # iron
        elif type == CREDIT:
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

    # type: # "PUT" or "CALL" or "IRON"
    # bull_spread/bear_spread: Bull/Bear object
    def __init__(self, type, bear_spread, bull_spread):
        quantity = bear_spread.quantity
        expiry = bear_spread.expiry

        if type == PUT:
            return None
        elif type == CALL:
            return None
            # debit
        elif type == DEBIT:
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

    # stock: Stock class
    # long_put/short_call: Put/Call object
    def __init__(self, stock, long_put, short_call):
        quantity = long_put.quantity
        expiry = long_put.expiry

        cost = long_put.cost - short_call.cost
        print(isinstance(stock.cost, float))
        max_loss = stock.cost - long_put.strike_price + cost
        
        profit = short_call.strike_price - stock.cost - cost
        breakeven = stock.cost + cost
        value = long_put.value - short_call.value

        type = DEBIT if cost > 0 else CREDIT

        super().__init__(type, quantity, cost, profit, value)
        self.risk = max_loss
        self.expiry = expiry
        self.profit = profit
        self.breakeven = breakeven
        self.lower_bound = long_put.strike_price
        self.upper_bound = short_call.strike_price

class HedgedStock(Spread):

    # stock: Stock class
    # long_put: Put object
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

class CoveredCall(Spread):

    # stock: Stock class
    # short_call: Call object
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
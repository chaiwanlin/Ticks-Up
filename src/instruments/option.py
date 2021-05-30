from instruments.instrument import Instrument


class Option(Instrument):

    def __init__(self, ticker, price, underlying, type, strike_price):
        super().__init__(ticker, price, underlying)
        self.type = type
        self.strike_price = strike_price

##consider future implementation of greeks

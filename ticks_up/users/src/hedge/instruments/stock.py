from .instrument import Instrument


class Stock(Instrument):
    def __init__(self, ticker, price):
        super().__init__(ticker, price, ticker)
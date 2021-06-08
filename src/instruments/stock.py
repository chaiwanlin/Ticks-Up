from instruments.instrument import Instrument


class Stock(Instrument):

    def __init__(self, ticker):
        super().__init__(ticker, self)
    
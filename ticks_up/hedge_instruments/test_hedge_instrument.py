import unittest
from instrument import Instrument
from stock import Stock
from option import Option, CallOption, PutOption

class TestInstrument(unittest.TestCase):

    def setUp(self):
        self.instrument = Instrument("^GSPC", None)

    def test_ticker(self):
        self.assertEqual(self.instrument.ticker, "^GSPC")

    def test_underlying(self):
        result =  Instrument("^GSPC", self.instrument)
        self.assertEqual(result.underlying, self.instrument)

class TestStockInit(unittest.TestCase):
    
    def test_init(self):
        with self.assertRaises(LookupError):
            Stock("hehexd")

class TestStock(unittest.TestCase):

    def setUp(self):
        self.stock = Stock("^GSPC")

    def test_exchange(self):
        self.assertEqual(self.stock.exchange, "SNP")

    def test_price(self):
        self.assertIsInstance(self.stock.price, float)

class TestOptionInit(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(LookupError):
            Option("hehexd")

# class TestCallOption(unittest.TestCase):

#     def setUp(self):
        
#         data = {
#             "strike" : 100,
#             "lastPrice" : 1.5,
#             "volume" : 1000,
#             "openInterest" : 1000,
#             "bid" : 1.4,
#             "ask" : 1.6, 
#             "impliedVolatility" : 0.2,
#             "expiration" : 1637280000
#         }

#         self.underlying = Instrument("TEST", None)
#         self.option = CallOption("TEST", self.underlying, data)

#     def test_underlying(self):
#         self.assertEqual(self.option.underlying, self.underlying)

#     def test_ticker(self):
#         self.assertEqual(self.option.ticker, "TEST")

#     def test_strike(self):
#         self.assertEqual(self.option.strike, 100)

#     def test_price(self):
#         self.assertEqual(self.option.price, 1.5)
    
#     def test_volume(self):
#         self.assertEqual(self.option.volume, 1000)
    
#     def test_interest(self):
#         self.assertEqual(self.option.interest, 1000)
    
#     def test_bid(self):
#         self.assertEqual(self.option.bid, 1.4)

#     def test_ask(self):
#         self.assertEqual(self.option.ask, 1.6)

#     def test_implied_volatility(self):
#         self.assertEqual(self.option.implied_volatility, 0.2)

#     def test_expiry(self):
#         self.assertEqual(self.option.expiry, 1637280000)

#     def test_get_expiration(self):
#         self.assertEqual(self.option.get_expiration(), "2021-11-19")

# class TestPutOption(unittest.TestCase):


#     def setUp(self):
        
#         data = {
#             "strike" : 100,
#             "lastPrice" : 1.5,
#             "volume" : 1000,
#             "openInterest" : 1000,
#             "bid" : 1.4,
#             "ask" : 1.6, 
#             "impliedVolatility" : 0.2,
#             "expiration" : 1637280000
#         }

#         self.underlying = Instrument("TEST", None)
#         self.option = PutOption("TEST", self.underlying, data)

#     def test_underlying(self):
#         self.assertEqual(self.option.underlying, self.underlying)

#     def test_ticker(self):
#         self.assertEqual(self.option.ticker, "TEST")

#     def test_strike(self):
#         self.assertEqual(self.option.strike, 100)

#     def test_price(self):
#         self.assertEqual(self.option.price, 1.5)
    
#     def test_volume(self):
#         self.assertEqual(self.option.volume, 1000)
    
#     def test_interest(self):
#         self.assertEqual(self.option.interest, 1000)
    
#     def test_bid(self):
#         self.assertEqual(self.option.bid, 1.4)

#     def test_ask(self):
#         self.assertEqual(self.option.ask, 1.6)

#     def test_implied_volatility(self):
#         self.assertEqual(self.option.implied_volatility, 0.2)

#     def test_expiry(self):
#         self.assertEqual(self.option.expiry, 1637280000)

#     def test_get_expiration(self):
#         self.assertEqual(self.option.get_expiration(), "2021-11-19")

    
if __name__ == "__main__":
    unittest.main()
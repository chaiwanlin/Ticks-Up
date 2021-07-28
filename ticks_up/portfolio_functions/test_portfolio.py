from datetime import date
import unittest
from portfolio_instrument import *

class TestAsset(unittest.TestCase):

    def setUp(self):
        self.asset = Asset(1, 100, 90)

    def test_quantity(self):
        self.assertEqual(self.asset.quantity, 1)

    def test_cost(self):
        self.assertEqual(self.asset.cost, 100)

    def test_value(self):
        self.assertEqual(self.asset.value, 90)

class TestInstrument(unittest.TestCase):
    def setUp(self):
        self.long = Instrument(LONG, 1, 100, 90, 1)
        self.short = Instrument(SHORT, 1, 100, 90, 1)

    def test_position(self):
        self.assertEqual(self.long.position, LONG)
        self.assertEqual(self.short.position, SHORT)

    def test_leveraged_quantity(self):
        self.assertEqual(self.long.leveraged_quantity, 1)
    
    def test_lot_cost(self):
        self.assertEqual(self.short.lot_cost, 100)
        self.assertEqual(self.long.lot_cost, 100)
    
    def test_lot_value(self):
        self.assertEqual(self.short.lot_value, 90)
        self.assertEqual(self.long.lot_value, 90)
   
class TestStockInit(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            Stock("TEST", "hehexd", 1 , 100)

class TestStock(unittest.TestCase):

    def setUp(self):
        self.long = Stock("TEST", LONG, 1 , 100)
        self.short = Stock("TEST", SHORT, 1 , 100)
    
    def test_risk(self):
        self.assertEqual(self.short.risk, math.inf)
        self.assertEqual(self.long.risk, 100)

class TestOption(unittest.TestCase):

    def setUp(self):
        expiry = datetime.fromtimestamp(1637280000)
        self.long = Option(LONG, 2 ,10, 150, expiry, 9)
        self.short = Option(SHORT, 2 ,10,  150, expiry, 9)
    
    def test_leveraged_quantity(self):
        self.assertEqual(self.short.leveraged_quantity, 200)
        self.assertEqual(self.long.leveraged_quantity, 200)

    def test_lot_value(self):
        self.assertEqual(self.short.lot_value, 1800)
        self.assertEqual(self.long.lot_value, 1800)

    def test_lot_cost(self):
        self.assertEqual(self.short.lot_cost, 2000)
        self.assertEqual(self.long.lot_cost, 2000)

    def test_get_expiry(self):
        self.assertEqual(self.short.get_expiry(), "2021-11-19")
        self.assertEqual(self.long.get_expiry(), "2021-11-19")

class TestCallInit(unittest.TestCase):
    def test_init(self):
        expiry = datetime.fromtimestamp(1637280000)
        with self.assertRaises(ValueError):
            Call("TEST", "TEST", 10 ,10, 150, expiry)

class TestCall(unittest.TestCase):

    def setUp(self):
        expiry = datetime.fromtimestamp(1637280000)
        self.long = Call("TEST", LONG, 10 ,10, 150, expiry)
        self.short = Call("TEST", SHORT, 10 ,10,  150, expiry)

    def test_extract_quantity(self):
        long = self.long.extract_quantity(3)
        self.assertEqual(long.quantity, 3)
        self.assertEqual(self.long.quantity, 7)

        short = self.short.extract_quantity(4)
        self.assertEqual(short.quantity, 4)
        self.assertEqual(self.short.quantity, 6)

        with self.assertRaises(ValueError):
            self.long.extract_quantity(8)
            self.short.extract_quantity(7)
    
    def test_leveraged_quantity(self):
        self.assertEqual(self.short.leveraged_quantity, 1000)
        self.assertEqual(self.long.leveraged_quantity, 1000)

    def test_lot_value(self):
        self.assertEqual(self.short.lot_value, 10000)
        self.assertEqual(self.long.lot_value, 10000)

    def test_lot_cost(self):
        self.assertEqual(self.short.lot_cost, 10000)
        self.assertEqual(self.long.lot_cost, 10000)

    def test_get_expiry(self):
        self.assertEqual(self.short.get_expiry(), "2021-11-19")
        self.assertEqual(self.long.get_expiry(), "2021-11-19")

class TestPutInit(unittest.TestCase):
    def test_init(self):
        expiry = datetime.fromtimestamp(1637280000)
        with self.assertRaises(ValueError):
            Put("TEST", "TEST", 10 ,10, 150, expiry)
    
class TestPut(unittest.TestCase):

    def setUp(self):
        expiry = datetime.fromtimestamp(1637280000)
        self.long = Put("TEST", LONG, 10 ,10, 150, expiry)
        self.short = Put("TEST", SHORT, 10 ,10,  150, expiry)

    def test_extract_quantity(self):
        long = self.long.extract_quantity(3)
        self.assertEqual(long.quantity, 3)
        self.assertEqual(self.long.quantity, 7)

        short = self.short.extract_quantity(4)
        self.assertEqual(short.quantity, 4)
        self.assertEqual(self.short.quantity, 6)

        with self.assertRaises(ValueError):
            self.long.extract_quantity(8)
            self.short.extract_quantity(7)
    
    def test_leveraged_quantity(self):
        self.assertEqual(self.short.leveraged_quantity, 1000)
        self.assertEqual(self.long.leveraged_quantity, 1000)

    def test_lot_value(self):
        self.assertEqual(self.short.lot_value, 10000)
        self.assertEqual(self.long.lot_value, 10000)

    def test_lot_cost(self):
        self.assertEqual(self.short.lot_cost, 10000)
        self.assertEqual(self.long.lot_cost, 10000)

    def test_get_expiry(self):
        self.assertEqual(self.short.get_expiry(), "2021-11-19")
        self.assertEqual(self.long.get_expiry(), "2021-11-19")

class TestSpread(unittest.TestCase):
    def setUp(self):
        self.credit = Spread(CREDIT, 2, 40, 20, 15)
        self.debit = Spread(DEBIT, 2, 20, 40, 25)

    def test_position(self):
        self.assertEqual(self.credit.position, SHORT)
        self.assertEqual(self.debit.position, LONG)



if __name__ == "__main__":
    unittest.main()
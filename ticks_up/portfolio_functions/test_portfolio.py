import unittest
from portfolio_instrument import *

class TestAsset(unittest.TestCase):

    def setUp(self):
        self.asset = Asset(1, 100, 90)

    def test_quantity(self):
        self.assertEqual(self.asset.quantity, 1)

if __name__ == "__main__":
    unittest.main()
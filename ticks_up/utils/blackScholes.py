from math import log, sqrt
import math
from typing import Sequence
from statistics import NormalDist
from bs4 import BeautifulSoup
import urllib.request as rq
from scipy.optimize import fsolve
import numpy as np
from hedge_instruments.constants import *

class BlackScholes:
    def __init__(self, type, underlying, strike, volatility, dividend, maturity, price):
        try:
            request = rq.urlopen("https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield")
            soup = BeautifulSoup(request.read(), 'html.parser')

            tr = soup.find("table", class_ = "t-chart").find_all("tr")
            last_tr = tr[len(tr) - 1]
            td = last_tr.find_all("td")
            risk_free_rate = int(td[10].get_text()) / 100
        except Exception:
            risk_free_rate = 0.02
        
        self.type = type
        self.underlying = underlying
        self.strike = strike
        self.risk_free_rate = risk_free_rate
        self.dividend = dividend
        self.maturity = maturity
        self.price = price
        if volatility > 0.001:
            self.volatility = volatility
        else:
            self.volatility = self.iv()
        
        self.eqt = (math.e ** (-self.dividend * self.maturity))
        self.ert = (math.e ** (-risk_free_rate  * self.maturity))
        self.normal = NormalDist(0,1)
        
        self.d1 = (log(underlying / strike) + maturity * (risk_free_rate - dividend + (self.volatility ** 2)/2)) / (self.volatility * sqrt(maturity))
        self.d2 = self.d1 - (self.volatility * sqrt(maturity))

    def get_price(self):
        if self.type == CALL:
            return self.underlying * self.eqt * self.normal.cdf(self.d1) - self.ert * self.strike * self.normal.cdf(self.d2)
        else:
            return -self.underlying * self.eqt * self.normal.cdf(-self.d1) + self.ert * self.strike * self.normal.cdf(-self.d2)
       
    def delta(self):
        delta = self.eqt * self.normal.cdf(self.d1)
        return delta

    def gamma(self):
        gamma = self.eqt * (self.normal.pdf(self.d1)/(self.underlying * self.volatility * sqrt(self.maturity)))
        return gamma

    def theta(self):
        first_term = -self.eqt * ((self.underlying * self.normal.pdf(self.d1) * self.volatility) / (2 * sqrt(self.maturity)))
        call_terms = -(self.risk_free_rate * self.strike * self.ert * self.normal.cdf(self.d2)) \
            + (self.dividend * self.underlying * self.eqt * self.normal.cdf(self.d1))
        put_terms = (self.risk_free_rate * self.strike * self.ert * self.normal.cdf(-self.d2)) \
            - (self.dividend * self.underlying * self.eqt * self.normal.cdf(-self.d1))
        
        theta = first_term
        if self.type == CALL:
            theta = theta + call_terms
        else:
            theta = theta + put_terms
        
        return theta / 365.25

    def vega(self):
        vega = self.underlying * self.eqt * self.normal.pdf(self.d1) * sqrt(self.maturity)
        return vega / 100

    def rho(self):
        rho_call = self.strike * self.maturity * self.ert * self.normal.cdf(self.d2)
        rho_put = -self.strike * self.maturity * self.ert * self.normal.cdf(-self.d2)
        if self.type == CALL:
            return rho_call / 100
        else:
            return rho_put / 100

    def iv(self):
        fn = lambda x : BlackScholes(self.type, self.underlying, self.strike, x, self.dividend, self.maturity, self.price).get_price() - self.price
        return fsolve(fn, 0.3, xtol = 1.e-6)[0]

# print(BlackScholes(36.07, 35, 0.4825, 0, 0.0712,50).delta())
# print(BlackScholes(36.07, 35, 0.4825, 0,0,0.0712).gamma())
# print(BlackScholes(36.07, 35, 0.4825, 0, 0,0.0712).theta("CALL"))
# print(BlackScholes(36.07, 35, 0.4825, 0, 0, 0.0712).vega())
# print(BlackScholes(36.07, 35, 0.4825, 0, 0,0.0712).rho("CALL"))
# print(BlackScholes("PUT", 36.07, 35, 0.000001,  0, 0.0712, 1.317).get_price())


    
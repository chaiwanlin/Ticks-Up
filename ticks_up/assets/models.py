from django.db import models
from django.contrib.auth.models import User
from portfolio.industry import *

# # Model 1
#
# # User ---|one-to-many|---> Portfolio
# # Each user able to save multiple portfolios (e.g. for short-term positions, long-term positions)
# class Portfolio(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=128)
#     # date_created = models.DateTimeField()     # required? useful to sort
#
#     def __str__(self):
#         return self.name
#
# # Portfolio ---|one-to-many|---> Ticker
# # To store tickers under a specified portfolio
# class Ticker(models.Model):
#     portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
#     name = models.CharField(max_length=7)
#
#     def __str__(self):
#         return self.name
#
#
# # Portfolio ---|one-to-many|---> StockPosition
# # Ticker ---|one-to-one|---> StockPosition
# # To store stock position(s) under a specified portfolio
# class StockPosition(models.Model):
#     portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
#     ticker = models.OneToOneField(Ticker, on_delete=models.CASCADE)
#     total_cost = models.DecimalField(max_digits=19, decimal_places=4)
#     total_shares = models.DecimalField(max_digits=19, decimal_places=4)
#
#     def __str__(self):
#         return "[STOCK] {ticker} | Total Cost: {total_cost} | Total Shares: {total_shares}".format(
#             ticker=self.ticker,
#             total_cost=self.total_cost,
#             total_shares=self.total_shares,
#         )
#
#     def save(self, *args, **kwargs):
#         try:
#             stock = StockPosition.objects.get(portfolio=self.portfolio, ticker=self.ticker)
#             stock.total_cost += self.total_cost
#             stock.total_shares += self.total_shares
#             if stock.total_shares < 0:
#                 raise ValueError('You cannot sell more shares than you own!')
#             elif stock.total_shares == 0:
#                 if stock.ticker.optionposition_set.all():
#                     stock.delete()
#                 else:
#                     stock.ticker.delete()
#             else:
#                 super(StockPosition, stock).save()
#         except StockPosition.DoesNotExist:
#             super().save(*args, **kwargs)
#
#     def average_cost(self):
#         return self.total_cost / self.total_shares
#
#
# # Portfolio ---|one-to-many|---> OptionPosition
# # Ticker ---|one-to-many|---> OptionPosition
# # To store option position(s) under a specified portfolio
# class OptionPosition(models.Model):
#     portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
#     ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
#
#     CALL_OR_PUT = [
#         ('CALL', 'Call'),
#         ('PUT', 'Put'),
#     ]
#     call_or_put = models.CharField(max_length=4, choices=CALL_OR_PUT)
#
#     BUY_OR_SELL = [
#         ('BUY', 'Buy'),
#         ('SELL', 'Sell'),
#     ]
#     buy_or_sell = models.CharField(max_length=4, choices=BUY_OR_SELL)
#
#     expiration_date = models.DateField()
#     strike_price = models.DecimalField(max_digits=10, decimal_places=1)
#     total_cost = models.DecimalField(max_digits=19, decimal_places=4)
#     total_contracts = models.PositiveIntegerField()
#
#     def __str__(self):
#         return "{expiration_date} {strike_price}{call_or_put} {buy_or_sell}".format(
#             strike_price=self.strike_price,
#             call_or_put=self.call_or_put,
#             expiration_date=self.expiration_date,
#             buy_or_sell=self.buy_or_sell,
#         )
#
#     def save(self, *args, **kwargs):
#         try:
#             option = OptionPosition.objects.get(
#                 portfolio=self.portfolio,
#                 ticker=self.ticker,
#                 call_or_put=self.call_or_put,
#                 buy_or_sell=self.buy_or_sell,
#                 expiration_date=self.expiration_date,
#                 strike_price=self.strike_price,
#             )
#             option.total_cost += self.total_cost
#             option.total_contracts += self.total_contracts
#             if option.total_contracts < 0:
#                 raise ValueError('You cannot sell more contracts than you own!')
#             elif option.total_contracts == 0:
#                 try:
#                     option.ticker.stockposition
#                     self.delete()
#                 except StockPosition.DoesNotExist:
#                     option.ticker.delete()
#             else:
#                 super(OptionPosition, option).save()
#         except OptionPosition.DoesNotExist:
#             super().save(*args, **kwargs)
#
#     def average_cost(self):
#         return self.total_cost / self.total_contracts

# Model 2


# User ---|one-to-many|---> Portfolio
# Each user able to save multiple portfolios (e.g. for short-term positions, long-term positions)
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    margin = models.DecimalField(max_digits=4, decimal_places=2)
    # date_created = models.DateTimeField()     # required? useful to sort

    def __str__(self):
        return self.name


# Ticker ---|many-to-many|---> Sector
# To store sectors of tickers
class Sector(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Sector ---|many-to-many|---> Industry
# Ticker ---|many-to-many|---> Industry
# To store sectors of tickers
class Industry(models.Model):
    name = models.CharField(max_length=50)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Portfolio ---|many-to-many|---> Ticker
# StockPosition ---|many-to-many|---> Ticker
# OptionPosition ---|many-to-many|---> Ticker
# To store tickers
class Ticker(models.Model):
    name = models.CharField(max_length=7)
    portfolio = models.ManyToManyField(Portfolio)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Portfolio ---|one-to-many|---> StockPosition
# Ticker ---|one-to-one|---> StockPosition
# To store stock position(s) under a specified portfolio
class StockPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=19, decimal_places=4)
    total_shares = models.DecimalField(max_digits=19, decimal_places=4)

    def __str__(self):
        return "[STOCK] {ticker} | Total Cost: {total_cost} | Total Shares: {total_shares}".format(
            ticker=self.ticker,
            total_cost=self.total_cost,
            total_shares=self.total_shares,
        )

    def save(self, *args, **kwargs):
        try:
            stock = StockPosition.objects.get(portfolio=self.portfolio, ticker=self.ticker)
            stock.total_cost += self.total_cost
            stock.total_shares += self.total_shares
            if stock.total_shares < 0:
                raise ValueError('You cannot sell more shares than you own!')
            elif stock.total_shares == 0:
                if stock.ticker.optionposition_set.all():
                    stock.delete()
                else:
                    stock.ticker.delete()
            else:
                super(StockPosition, stock).save()
        except StockPosition.DoesNotExist:
            super().save(*args, **kwargs)

    def average_cost(self):
        return self.total_cost / self.total_shares


# Portfolio ---|one-to-many|---> OptionPosition
# Ticker ---|one-to-many|---> OptionPosition
# To store option position(s) under a specified portfolio
class OptionPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    CALL_OR_PUT = [
        ('CALL', 'Call'),
        ('PUT', 'Put'),
    ]
    call_or_put = models.CharField(max_length=4, choices=CALL_OR_PUT)

    LONG_OR_SHORT = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    long_or_short = models.CharField(max_length=5, choices=LONG_OR_SHORT)

    expiration_date = models.DateField()
    strike_price = models.DecimalField(max_digits=10, decimal_places=1)
    total_cost = models.DecimalField(max_digits=19, decimal_places=4)
    total_contracts = models.PositiveIntegerField()

    def __str__(self):
        return "{expiration_date} {strike_price}{call_or_put} {buy_or_sell}".format(
            strike_price=self.strike_price,
            call_or_put=self.call_or_put,
            expiration_date=self.expiration_date,
            buy_or_sell=self.buy_or_sell,
        )

    def save(self, *args, **kwargs):
        try:
            option = OptionPosition.objects.get(
                portfolio=self.portfolio,
                ticker=self.ticker,
                call_or_put=self.call_or_put,
                buy_or_sell=self.buy_or_sell,
                expiration_date=self.expiration_date,
                strike_price=self.strike_price,
            )
            option.total_cost += self.total_cost
            option.total_contracts += self.total_contracts
            if option.total_contracts < 0:
                raise ValueError('You cannot sell more contracts than you own!')
            elif option.total_contracts == 0:
                try:
                    option.ticker.stockposition
                    self.delete()
                except StockPosition.DoesNotExist:
                    option.ticker.delete()
            else:
                super(OptionPosition, option).save()
        except OptionPosition.DoesNotExist:
            super().save(*args, **kwargs)

    def average_cost(self):
        return self.total_cost / self.total_contracts


# Portfolio ---|one-to-many|---> VerticalSpread
# Ticker ---|one-to-many|---> VerticalSpread
# To store vertical spread(s) under a specified portfolio
class VerticalSpread(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)

    TYPES = [
        ('BULL', 'Bull'),
        ('BEAR', 'Bear'),
    ]
    types = models.CharField(max_length=10, choices=TYPES)

    CREDIT_OR_DEBIT = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
        ('NA', 'Not Applicable'),
    ]
    credit_or_debit = models.CharField(max_length=20, choices=CREDIT_OR_DEBIT)

    short_leg = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="short_leg")
    long_leg = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="long_leg")


# Portfolio ---|one-to-many|---> ButterflySpread
# Ticker ---|one-to-many|---> ButterflySpread
# To store butterfly spread(s) under a specified portfolio
class ButterflySpread(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)

    TYPES = [
        ('IRON CONDOR', 'Iron Condor'),
    ]
    types = models.CharField(max_length=20, choices=TYPES)

    bull_spread = models.OneToOneField(VerticalSpread, on_delete=models.CASCADE, related_name="bull_spread")
    bear_spread = models.OneToOneField(VerticalSpread, on_delete=models.CASCADE, related_name="bear_spread")
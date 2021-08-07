from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from hedge_instruments.option import Call, Put
import datetime
from portfolio_functions.industry import Industry as Classification


# Portfolio ---|many-to-one|---> User
# Each user able to save multiple portfolios (e.g. for short-term positions, long-term positions)
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    cash = models.DecimalField(max_digits=19, decimal_places=2)
    margin = models.DecimalField(max_digits=4, decimal_places=2, help_text='Leave blank if not margin account', blank=True, null=True)
    # date_created = models.DateTimeField()     # required? useful to sort

    def __str__(self):
        return self.name


# To store sectors of tickers
class Sector(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Industry ---|many-to-one|---> Sector
# To store sectors of tickers
class Industry(models.Model):
    name = models.CharField(max_length=50)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Ticker ---|many-to-many|---> Portfolio
# Ticker ---|many-to-one|---> Sector
# Ticker ---|many-to-one|---> Industry
# To store tickers
class Ticker(models.Model):
    name = models.CharField(max_length=7)
    portfolio = models.ManyToManyField(Portfolio)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     try:
    #         Ticker.objects.get(portfolio=self.portfolio, ticker=self.ticker)
    #     except Ticker.DoesNotExist:
    #         classification = Classification(self.name)
    #         sector = Sector(name=classification.get_sector())
    #         sector.save()
    #         self.sector = sector
    #         industry = Industry(name=classification.get_sector(), sector=sector)
    #         industry.save()
    #         self.industry = industry
    #         super().save(*args, **kwargs)


# StockPosition ---|many-to-one|---> Portfolio
# StockPosition ---|many-to-one|---> Ticker
# To store stock position(s) under a specified portfolio
class StockPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    LONG_OR_SHORT = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    long_or_short = models.CharField(max_length=5, choices=LONG_OR_SHORT, default='LONG')

    average_price = models.DecimalField(max_digits=19, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_shares = models.DecimalField(max_digits=19, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return "[STOCK] {ticker} | Total Cost: {total_cost} | Total Shares: {total_shares}".format(
            ticker=self.ticker,
            total_cost=self.average_price,
            total_shares=self.total_shares,
        )

    def save(self, *args, **kwargs):
        try:
            # Check if stock position already exists
            stock = StockPosition.objects.get(portfolio=self.portfolio, ticker=self.ticker)

            # Calculate aggregate
            if self.total_shares > 0:
                self.average_price = ((stock.average_price * stock.total_shares) + (self.average_price * self.total_shares)) / (self.total_shares + stock.total_shares)
            else:
                self.average_price = stock.average_price
            self.total_shares += stock.total_shares

            if self.total_shares < 0:
                # Trying to delete more shares than own, illegal
                raise ValueError('You cannot sell more shares than you own!')
            elif self.total_shares == 0:
                stock.delete()
                # Check if there are options for this ticker
                if not self.portfolio.optionposition_set.filter(ticker=self.ticker):
                    self.portfolio.ticker_set.remove(self.ticker)
            else:
                # Valid edit, update stock position
                stock.delete()
                super().save(*args, **kwargs)
        except StockPosition.DoesNotExist:
            # Stock position does not exist yet, create
            super().save(*args, **kwargs)

    def total_cost(self):
        return round(self.average_price * self.total_shares, 4)


# OptionPosition ---|many-to-one|---> Portfolio
# OptionPosition ---|many-to-one|---> Ticker
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

    expiration_date = models.DateField(default=datetime.date.today)
    strike_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    average_price = models.DecimalField(max_digits=19, decimal_places=2)
    total_contracts = models.PositiveIntegerField()

    def __str__(self):
        return "{expiration_date} {strike_price}{call_or_put} {long_or_short}".format(
            strike_price=self.strike_price,
            call_or_put=self.call_or_put,
            expiration_date=self.expiration_date,
            long_or_short=self.long_or_short,
        )

    def save(self, *args, **kwargs):
        # Validate option position (Does not work because Option instrument classes do not validate)
        try:
            if self.call_or_put == 'CALL':
                option_instr = Call(self.ticker.name,
                                      self.expiration_date.year,
                                      self.expiration_date.month,
                                      self.expiration_date.day)
            else:
                option_instr = Put(self.ticker.name,
                                    self.expiration_date.year,
                                    self.expiration_date.month,
                                    self.expiration_date.day)
            option_instr.get_option_for_strike(self.strike_price)
        except LookupError:
            raise LookupError("Option position is invalid!")

        try:
            # Check if stock position already exists
            option = OptionPosition.objects.get(
                portfolio=self.portfolio,
                ticker=self.ticker,
                call_or_put=self.call_or_put,
                long_or_short=self.long_or_short,
                expiration_date=self.expiration_date,
                strike_price=self.strike_price,
            )

            # Calculate aggregate
            if self.total_contracts > 0:
                self.average_price = ((option.average_price * option.total_contracts) + (self.average_price * self.total_contracts)) / (self.total_contracts + option.total_contracts)
            else:
                self.average_price = option.average_price
            self.total_contracts += option.total_contracts

            if self.total_contracts < 0:
                # Trying to remove more contracts than own, illegal
                raise ValueError('You cannot sell more contracts than you own!')
            elif self.total_contracts == 0:
                option.delete()
                if not self.portfolio.stockposition_set.filter(ticker=self.ticker):
                    self.portfolio.ticker_set.remove(self.ticker)
            else:
                # Valid edit, update option position
                option.delete()
                super().save(*args, **kwargs)
        except OptionPosition.DoesNotExist:
            # Stock position does not exist yet, create
            super().save(*args, **kwargs)

    def total_cost(self):
        return self.average_price * self.total_contracts


# VerticalSpread ---|many-to-one|---> Portfolio
# VerticalSpread ---|many-to-one|---> Ticker
# VerticalSpread ---|one-to-one|---> OptionPosition (short_leg)
# VerticalSpread ---|one-to-one|---> OptionPosition (long_leg)
# To store vertical spread(s) under a specified portfolio
class VerticalSpread(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    TYPES = [
        ('BULL', 'Bull'),
        ('BEAR', 'Bear'),
    ]
    types = models.CharField(max_length=10, choices=TYPES)

    CREDIT_OR_DEBIT = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]
    credit_or_debit = models.CharField(max_length=20, choices=CREDIT_OR_DEBIT)

    short_leg = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="short_leg")
    long_leg = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="long_leg")

    def __str__(self):
        return "{types} {credit_or_debit} SPREAD".format(
            types=self.types,
            credit_or_debit=self.credit_or_debit,
        )


# ButterflySpread ---|many-to-one|---> Portfolio
# ButterflySpread ---|many-to-one|---> Ticker
# ButterflySpread ---|one-to-one|---> VerticalSpread (bull_spread)
# ButterflySpread ---|one-to-one|---> VerticalSpread (bear_spread)
# To store butterfly spread(s) under a specified portfolio
class ButterflySpread(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    TYPES = [
        ('CREDIT', 'Iron Condor (Credit)'),
    ]
    types = models.CharField(max_length=25, choices=TYPES)

    bull_spread = models.OneToOneField(VerticalSpread, on_delete=models.CASCADE, related_name="bull_spread")
    bear_spread = models.OneToOneField(VerticalSpread, on_delete=models.CASCADE, related_name="bear_spread")

    def __str__(self):
        return "{types} SPREAD".format(
            types=self.types,
        )


# Collar ---|many-to-one|---> Portfolio
# Collar ---|many-to-one|---> Ticker
# Collar ---|one-to-one|---> StockPosition
# Collar ---|one-to-one|---> OptionPosition (long_put)
# Collar ---|one-to-one|---> OptionPosition (short_call)
# To store collar under a specified portfolio
class Collar(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    stock_position = models.OneToOneField(StockPosition, on_delete=models.CASCADE)

    long_put = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="long_put")
    short_call = models.OneToOneField(OptionPosition, on_delete=models.CASCADE, related_name="short_call")

    def __str__(self):
        return "COLLAR".format(
        )


# ProtectivePut ---|many-to-one|---> Portfolio
# ProtectivePut ---|many-to-one|---> Ticker
# ProtectivePut ---|one-to-one|---> StockPosition
# ProtectivePut ---|one-to-one|---> OptionPosition (long_put)
# To store a protective put hedge position under a specified portfolio
class ProtectivePut(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    stock_position = models.OneToOneField(StockPosition, on_delete=models.CASCADE)

    long_put = models.OneToOneField(OptionPosition, on_delete=models.CASCADE)

    def __str__(self):
        return "ProtectivePut".format(
        )
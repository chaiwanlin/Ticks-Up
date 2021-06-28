from django.db import models
from django.contrib.auth.models import User


# User ---|one-to-many|---> Portfolio
# Each user able to save multiple portfolios (e.g. for short-term positions, long-term positions)
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    # date_created = models.DateTimeField()     # required? useful to sort

    def __str__(self):
        return self.name


# # Abstract class to store common info between Stock and Option models
# class PositionInfo(models.Model):
#     portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
#     ticker = models.CharField(max_length=10)    # need to make custom field for ticker?
#     # date_created = models.DateTimeField()  # required? useful to sort
#
#     class Meta:
#         abstract = True
#         # ordering = ?
#         # managed = ?

# Portfolio ---|one-to-many|---> Ticker
# To store tickers under a specified portfolio
class Ticker(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    name = models.CharField(max_length=7)

    def __str__(self):
        return self.name


# Portfolio ---|one-to-many|---> StockPosition
# Ticker ---|one-to-one|---> StockPosition
# To store stock position(s) under a specified portfolio
class StockPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.OneToOneField(Ticker, on_delete=models.CASCADE)
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

    BUY_OR_SELL = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    buy_or_sell = models.CharField(max_length=4, choices=BUY_OR_SELL)

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
            super(OptionPosition, option).save()
        except OptionPosition.DoesNotExist:
            super().save(*args, **kwargs)

    def average_cost(self):
        return self.total_cost / self.total_contracts

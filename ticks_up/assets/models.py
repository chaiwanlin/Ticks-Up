from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


# User ---|one-to-many|---> Portfolio
# Each user able to save multiple portfolios (e.g. for short-term positions, long-term positions)
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    # date_created = models.DateTimeField()     # required? useful to sort

    def __str__(self):
        return self.name


# Abstract class to store common info between Stock and Option models
class PositionInfo(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)    # need to make custom field for ticker?
    # date_created = models.DateTimeField()  # required? useful to sort

    class Meta:
        abstract = True
        # ordering = ?
        # managed = ?


# Portfolio ---|one-to-many|---> StockPosition
# To store stock position(s) under a specified portfolio
class StockPosition(PositionInfo):
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
        except ObjectDoesNotExist:
            super().save(*args, **kwargs)


# Portfolio ---|one-to-many|---> OptionPosition
# To store option position(s) under a specified portfolio
class OptionPosition(PositionInfo):
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
        return "[OPTION] {ticker} {strike_price}{call_or_put} {expiration_date} {buy_or_sell}" \
               " | Total Cost: {total_cost} | Total Contracts: {total_contracts}".format(
                ticker=self.ticker,
                strike_price=self.strike_price,
                call_or_put=self.call_or_put,
                expiration_date=self.expiration_date,
                buy_or_sell=self.buy_or_sell,
                total_cost=self.total_cost,
                total_contracts=self.total_contracts,
        )

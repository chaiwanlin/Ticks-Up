from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    shares = models.FloatField()
    average_price = models.FloatField()

    def __str__(self):
        return self.ticker
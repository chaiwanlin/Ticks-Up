from django.contrib import admin
from .models import Portfolio, Ticker, StockPosition, OptionPosition

admin.site.register(Portfolio)
admin.site.register(Ticker)
admin.site.register(StockPosition)
admin.site.register(OptionPosition)
from django.contrib import admin
from .models import Portfolio, StockPosition, OptionPosition

admin.site.register(Portfolio)
admin.site.register(StockPosition)
admin.site.register(OptionPosition)
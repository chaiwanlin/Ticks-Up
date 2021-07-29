from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('search-ticker/', search_ticker, name='search_ticker'),
    path('<str:ticker>/option-strategies', option_strategies, name='option_strategies'),
    path('<str:ticker>/<str:sector_or_industry>/view-similar-tickers', view_similar_tickers, name='view_similar_tickers'),
]
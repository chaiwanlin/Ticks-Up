from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search-ticker/', views.search_ticker, name='search_ticker'),
    path('<str:ticker>/vertical-spreads', views.vertical_spreads, name='vertical_spreads')
]
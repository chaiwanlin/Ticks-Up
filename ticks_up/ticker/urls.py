from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-<str:ticker>/', views.ticker, name='ticker'),
    path('get-<str:ticker>/vertical-spreads', views.vertical_spreads, name='vertical_spreads')
]
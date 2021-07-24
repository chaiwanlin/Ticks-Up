from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search-ticker/', views.search_ticker, name='search_ticker'),
    path('<str:ticker>/option-strategies', views.option_strategies, name='option_strategies')
]
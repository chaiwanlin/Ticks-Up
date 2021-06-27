from django.urls import path
from . import views

urlpatterns = [
    path('', views.assets, name='assets'),
    path('add-portfolio', views.add_portfolio, name='add_portfolio'),
    path('<int:portfolio_id>', views.view_portfolio, name='view_portfolio'),
    path('<int:portfolio_id>/add-stock-position', views.add_stock_position, name='add_stock_position'),
    path('<int:portfolio_id>/add-option-position', views.add_option_position, name='add_option_position'),
    path('<int:portfolio_id>/hedge-<str:ticker_name>-stock-position', views.hedge_stock_position, name='hedge_stock_position'),
]
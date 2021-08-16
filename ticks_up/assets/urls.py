from django.urls import path
from .views import *

urlpatterns = [
    path('', assets, name='assets'),
    path('add-portfolio', add_portfolio, name='add_portfolio'),
    path('remove-portfolio-<int:portfolio_id>', remove_portfolio, name='remove_portfolio'),
    path('<int:portfolio_id>', view_portfolio, name='view_portfolio'),
    path('<int:portfolio_id>/<str:add_or_remove>-cash', edit_cash, name='edit_cash'),
    path('<int:portfolio_id>/add-stock-position', add_stock_position, name='add_stock_position'),
    path('<int:portfolio_id>/add-option-position', add_option_position, name='add_option_position'),
    path('<int:portfolio_id>/add-vertical-spread', add_vertical_spread, name='add_vertical_spread'),
    path('<int:portfolio_id>/add-butterfly-spread', add_butterfly_spread, name='add_butterfly_spread'),
    path('<int:portfolio_id>/add-collar-<str:ticker_name>', add_collar, name='add_collar'),
    path('<int:portfolio_id>/add-protective-put-<str:ticker_name>', add_protective_put, name='add_protective_put'),
    path('<int:portfolio_id>/OPTION-<str:ticker_name>-<str:add_or_remove>', edit_option_position, name='edit_option_position'),
    path('<int:portfolio_id>/STOCK-<str:ticker_name>-<str:add_or_remove>', edit_stock_position, name='edit_stock_position'),
    path('<int:portfolio_id>/hedge-<str:ticker_name>-stock-position', hedge_stock_position, name='hedge_stock_position'),
    path('<int:portfolio_id>/add-hedge-<str:ticker_name>-stock-position/', add_hedge_stock_position, name='add_hedge_stock_position'),
    path('<int:portfolio_id>/<str:ticker_name>-delete-spread/', delete_spread, name='delete_spread'),
]
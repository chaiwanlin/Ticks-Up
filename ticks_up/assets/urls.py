from django.urls import path
from .views import assets, add_portfolio, view_portfolio

urlpatterns = [
    path('', assets, name='assets'),
    path('add-portfolio', add_portfolio, name='add_portfolio'),
    path('<int:portfolio_id>', view_portfolio, name='view_portfolio'),
]
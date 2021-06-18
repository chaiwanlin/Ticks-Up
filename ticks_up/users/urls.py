from django.urls import path, include
from .views import home, register, ticker

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('<ticker>-<target_price>/', ticker, name='ticker'),
]
from django.urls import path

from .views import StockAPI

urlpatterns = [
    path('investment/',StockAPI.as_view(), name='investment'),
]

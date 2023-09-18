from django.urls import path

from .views import StockAPI

urlpatterns = [
    path('',StockAPI.as_view()),
]

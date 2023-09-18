from django.urls import path

from . import views

urlpatterns = [
    path('', views.ClientAPI.as_view(), name='index'),
]

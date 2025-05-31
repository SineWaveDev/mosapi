from django.urls import path
from .views import TDSFileDownloadView

urlpatterns = [
    path('26as/download/', TDSFileDownloadView.as_view(), name='tds_file_download'),
]
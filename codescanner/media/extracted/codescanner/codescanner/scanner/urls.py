from django.urls import path
from . import views

urlpatterns = [
    path('scan/folder/<uuid:folder_id>/', views.scan_folder, name='scan_folder'),
    path('scan_result', views.scan_result, name='scanResult'),
]

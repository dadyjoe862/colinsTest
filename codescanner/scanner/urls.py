from django.urls import path
from . import views

urlpatterns = [
    path('render_scan_results', views.display_scan_results, name="render_scan_results"),
    path('scan_folder_and_store_results/<str:folder_id>/', views.scan_folder_and_store_results, name="scan_folder_and_store_results"),

]

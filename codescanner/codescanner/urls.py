from django.contrib import admin
from django.urls import path, include
from users import views as user_views 
# from scanner import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('register/', user_views.register, name='users-register'),
    path('', user_views.loginForm, name='users-login' ),
    path('logout/', user_views.logoutUser, name='users-logout' ),
    path('dashboard/', user_views.dashboard, name='users-dashboard'),
    path('profile/', user_views.profile, name="users-profile"), 
    path('', include('blog.urls')),
    # path('scanner/', include('scanner.urls')),
    path('accounts/', include('allauth.urls')),
    path('uploads/', user_views.upload_view, name='upload_view'),
    path('folder-data/', user_views.folder_data, name='folder_data'),
    path('folder-data/<int:folder_id>/', user_views.folder_data, name='folder_data_with_id'),
    path('folder-files/<int:folder_id>/', user_views.folder_files, name='folder_files'),
    path('folder/', user_views.folder, name="folder"),
    path('file-content/<int:file_id>/', user_views.file_content_view, name='file_content'),
    path('delete-folder/<int:folder_id>/', user_views.delete_folder_view, name='delete_folder'),
    path('repos/', user_views.repos, name="repos"),

    path('render_scan_results', user_views.display_scan_results, name="render_scan_results"),
    path('scan_folder_and_store_results/<str:folder_id>/', user_views.scan_folder_and_store_results, name="scan_folder_and_store_results"),

    path('folder_selection_and_report/', user_views.folder_selection_and_report, name='folder_selection_and_report'),
    path('report/', user_views.report, name="report"),
    path('generate_pdf/', user_views.generate_pdf, name='generate_pdf'),

    path('code_analysis/', user_views.code_analysis, name="code_analysis"),
#   path('vulnerability_chart/', user_views.vulnerability_chart, name='vulnerability_chart'),

] 
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
from django.urls import path
from . import views

app_name = 'downloader'

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.download_history, name='history'),
    path('status/<int:download_id>/', views.download_status, name='download_status'),
    path('info/', views.video_info, name='video_info'),
    path('download/<int:download_id>/', views.download_file, name='download_file'),
    path('delete/<int:download_id>/', views.delete_download, name='delete_download'),
]
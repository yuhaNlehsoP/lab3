from django.urls import path
from . import views

app_name = 'movie_app'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('add/', views.add_movie, name='add_movie'),
    path('upload/', views.upload_json, name='upload_json'),
    path('export/', views.export_all_movies, name='export_all_movies'),
    path('json/<str:filename>/', views.view_json_file, name='view_json_file'),
    path('movie/<str:file_id>/edit/', views.edit_movie, name='edit_movie'),
    path('movie/<str:file_id>/delete/', views.delete_movie, name='delete_movie'),
]
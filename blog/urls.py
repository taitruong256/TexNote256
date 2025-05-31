from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    # Overleaf-style editor
    path('latex/', views.latex_editor, name='latex_editor'),
    path('latex/load_file/', views.latex_load_file, name='latex_load_file'),
    path('latex/save_file/', views.latex_save_file, name='latex_save_file'),
    path('latex/upload_image/', views.latex_upload_image, name='latex_upload_image'),
    path('latex/render_html/', views.latex_render_html, name='latex_render_html'),
]

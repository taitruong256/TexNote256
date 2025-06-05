from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),  
    path('post/<int:pk>/', login_required(views.post_detail), name='post_detail'),
    path('post/new/', login_required(views.post_create), name='post_create'),
    path('user/<str:username>/', login_required(views.user_profile), name='user_profile'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    # Overleaf-style editor
    path('latex/', login_required(views.latex_editor), name='latex_editor'),
    path('latex/load_file/', login_required(views.latex_load_file), name='latex_load_file'),
    path('latex/save_file/', login_required(views.latex_save_file), name='latex_save_file'),
    path('latex/upload_image/', login_required(views.latex_upload_image), name='latex_upload_image'),
    path('latex/render_html/', login_required(views.latex_render_html), name='latex_render_html'),
]

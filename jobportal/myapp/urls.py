from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('post-job/', views.post_job, name='post_job'),
    path('apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('delete/<int:job_pk>/', views.delete_job, name='delete_job'),
    path('edit/<int:pk>/', views.edit_job, name='edit_job'),
]
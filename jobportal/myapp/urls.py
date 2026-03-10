from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('post-job/', views.post_job, name='post_job'),
    path('apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('delete/<int:pk>/', views.delete_job, name='delete_job'),
    path('edit/<int:pk>/', views.edit_job, name='edit_job'),
    path('applications/<int:pk>/', views.view_applicants, name='view_applicants'),
    path('application/status/<int:pk>/<str:status>/',views.update_status,name='update_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
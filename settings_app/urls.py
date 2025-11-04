from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.get_admin_settings, name='get_admin_settings'),
    path('update/', views.update_admin_settings, name='update_admin_settings'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('user/<str:user_id>/', views.user_dashboard, name='user_dashboard'),
    path('tests/user/<str:user_id>/', views.user_tests, name='user_tests'),
]

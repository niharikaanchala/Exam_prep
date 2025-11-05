from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.user_dashboard, name='user_dashboard'),
    path('tests/', views.user_tests, name='user_tests'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('create/', views.category_create, name='category_create'),
    path('<str:category_id>/update/', views.category_update, name='category_update'),
    path('<str:category_id>/delete/', views.category_delete, name='category_delete'),
    path('analytics/', views.analytics_overview, name='analytics_overview'),

    path('<str:category_id>/', views.category_detail, name='category_detail'),

    path('<str:id>/', views.get_category_by_id, name='get_category_by_id'),  # <- must exist\
    # path('analytics/', views.analytics_overview, name='analytics_overview'),
    
]


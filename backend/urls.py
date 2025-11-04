from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    
    path('api/categories/', include('categories.urls')),
    path('api/tests/', include('practice_tests.urls')),
    path('api/exams/', include('exams.urls')),
    path('api/', include('exams.urls')),
    # path('api/', include('exams.urls')), 
    # path('api/tests/', include('exams.urls')), 
    path('api/admin/', include('exams.urls')), 
    path('api/enrollments/', include('enrollments.urls')), 
    path("api/settings/", include("settings_app.urls")),   
    path("api/home/", include("home.urls")),
    path("api/blogs/", include("blog.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]

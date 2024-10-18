from django.contrib import admin
from django.urls import path, include
from monitoring import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'), 
    path('accounts/', include('django.contrib.auth.urls')),  # For login/logout views
    path('', include('users.urls')),
]

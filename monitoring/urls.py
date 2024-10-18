from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notification/', views.notification, name='notification'),
    path('page-status/', views.page_status, name='page_status'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout_view, name='logout'),
]

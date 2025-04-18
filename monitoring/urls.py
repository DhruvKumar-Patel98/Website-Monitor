from django.urls import path
from . import views
from .views import get_or_update_check_data, port_ping_status_data, ssl_domain_status_data

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notification/', views.notification, name='notification'),
    path('page-status/', views.page_status, name='page_status'),
    path('settings/', views.settings, name='settings'),
    path('account/', views.account, name='account'),
    path('api/chart-data/<int:check_id>/', views.chart_data, name='chart_data'),
    path('edit_check/', views.edit_check, name='edit_check'),
    path('api/check/<int:id>/', get_or_update_check_data, name='get_check_data'),
    path('api/port-ping-data/<int:check_id>/', port_ping_status_data, name='port_ping_data'),
    path('api/ssl-domain-data/<int:check_id>/', ssl_domain_status_data, name='ssl_domain_data'),

]
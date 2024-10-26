from django.urls import path
from . import views
from .views import AllChartDataView

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notification/', views.notification, name='notification'),
    path('page-status/', views.page_status, name='page_status'),
    path('settings/', views.settings, name='settings'),
    path('account/', views.account, name='account'),
    path('api/chart-data/<int:check_id>/', views.chart_data, name='chart_data'),
    path('api/all-chart-data/', AllChartDataView.as_view(), name='all_chart_data'),  # Ensure this path exists
]

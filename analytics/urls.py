# analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # API Endpoints - Dashboard Summary
    path('api/summary/', views.DashboardSummaryAPIView.as_view(), name='api_summary'),
    path('api/today/', views.TodaySummaryAPIView.as_view(), name='api_today'),
    path('api/alerts/', views.AlertsAPIView.as_view(), name='api_alerts'),

    # API Endpoints - Sample Statistics
    path('api/samples/', views.SampleStatisticsAPIView.as_view(), name='api_samples'),
    path('api/samples/status/', views.SamplesByStatusAPIView.as_view(), name='api_samples_status'),
    path('api/samples/tat/', views.TATDistributionAPIView.as_view(), name='api_tat'),
    path('api/samples/trends/', views.MonthlyTrendsAPIView.as_view(), name='api_monthly_trends'),

    # API Endpoints - QC Statistics
    path('api/qc/', views.QCStatisticsAPIView.as_view(), name='api_qc'),

    # API Endpoints - Equipment Metrics
    path('api/equipment/', views.EquipmentMetricsAPIView.as_view(), name='api_equipment'),

    # API Endpoints - Reagent Metrics
    path('api/reagents/', views.ReagentMetricsAPIView.as_view(), name='api_reagents'),

    # API Endpoints - Storage Metrics
    path('api/storage/', views.StorageMetricsAPIView.as_view(), name='api_storage'),

    # API Endpoints - Chart Data
    path('api/charts/<str:chart_type>/', views.ChartDataAPIView.as_view(), name='api_chart'),

    # Widget endpoints for AJAX loading
    path('widgets/sample-status/', views.SampleStatusWidgetView.as_view(), name='widget_sample_status'),
    path('widgets/qc-status/', views.QCStatusWidgetView.as_view(), name='widget_qc_status'),
    path('widgets/alerts/', views.AlertsWidgetView.as_view(), name='widget_alerts'),
]

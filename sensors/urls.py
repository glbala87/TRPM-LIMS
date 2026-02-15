# sensors/urls.py

from django.urls import path
from . import views

app_name = 'sensors'

urlpatterns = [
    # Sensor Types
    path('types/', views.SensorTypeListView.as_view(), name='type_list'),

    # Monitoring Devices
    path('devices/', views.MonitoringDeviceListView.as_view(), name='device_list'),
    path('devices/<int:pk>/', views.MonitoringDeviceDetailView.as_view(), name='device_detail'),
    path('devices/<int:pk>/readings/', views.DeviceReadingsView.as_view(), name='device_readings'),

    # Readings
    path('readings/', views.SensorReadingListView.as_view(), name='reading_list'),

    # Alerts
    path('alerts/', views.SensorAlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/', views.SensorAlertDetailView.as_view(), name='alert_detail'),
    path('alerts/<int:pk>/acknowledge/', views.acknowledge_alert, name='alert_acknowledge'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='alert_resolve'),

    # Dashboard
    path('dashboard/', views.SensorDashboardView.as_view(), name='dashboard'),

    # API endpoints for sensor data
    path('api/readings/', views.submit_reading, name='api_submit_reading'),
]

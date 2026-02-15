# instruments/urls.py

from django.urls import path
from . import views

app_name = 'instruments'

urlpatterns = [
    # Connection management
    path('connections/', views.ConnectionListView.as_view(), name='connection_list'),
    path('connections/<int:pk>/', views.ConnectionDetailView.as_view(), name='connection_detail'),
    path('connections/<int:pk>/start/', views.start_connection, name='connection_start'),
    path('connections/<int:pk>/stop/', views.stop_connection, name='connection_stop'),
    path('connections/<int:pk>/test/', views.test_connection, name='connection_test'),

    # Message logs
    path('messages/', views.MessageLogListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', views.MessageLogDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/reprocess/', views.reprocess_message, name='message_reprocess'),

    # Worklists
    path('worklists/', views.WorklistListView.as_view(), name='worklist_list'),
    path('worklists/create/', views.create_worklist, name='worklist_create'),
    path('worklists/<int:pk>/', views.WorklistDetailView.as_view(), name='worklist_detail'),
    path('worklists/<int:pk>/send/', views.send_worklist, name='worklist_send'),

    # Dashboard
    path('dashboard/', views.InstrumentDashboardView.as_view(), name='dashboard'),

    # API endpoints for instrument communication
    path('api/status/', views.api_connection_status, name='api_status'),
    path('api/send-message/', views.api_send_message, name='api_send_message'),
]

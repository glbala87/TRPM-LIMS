# audit/urls.py

from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Audit log views
    path('', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('<int:pk>/', views.AuditLogDetailView.as_view(), name='audit_log_detail'),
    path('trail/<str:content_type>/<int:object_id>/', views.audit_trail_view, name='audit_trail'),
    path('dashboard/', views.AuditDashboardView.as_view(), name='audit_dashboard'),

    # API endpoints
    path('api/recent/', views.api_recent_activity, name='api_recent_activity'),
    path('api/stats/', views.api_audit_stats, name='api_audit_stats'),
]

# analytics/admin.py

from django.contrib import admin
from .models import DashboardWidget, SavedQuery, Report, KPIMetric, Alert, ScheduledReport


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'widget_type', 'size', 'position', 'is_active']
    list_filter = ['widget_type', 'size', 'is_active']
    list_editable = ['position', 'is_active']
    search_fields = ['name']


@admin.register(SavedQuery)
class SavedQueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'query_type', 'created_by', 'is_public', 'updated_at']
    list_filter = ['query_type', 'is_public']
    search_fields = ['name', 'description']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'output_format', 'status', 'generated_by', 'created_at']
    list_filter = ['report_type', 'status', 'output_format']
    search_fields = ['name']
    date_hierarchy = 'created_at'


@admin.register(KPIMetric)
class KPIMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'value', 'unit', 'date']
    list_filter = ['category', 'date']
    search_fields = ['name']
    date_hierarchy = 'date'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'category', 'status', 'created_at']
    list_filter = ['severity', 'status', 'category']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'frequency', 'is_active', 'last_run', 'next_run']
    list_filter = ['report_type', 'frequency', 'is_active']
    search_fields = ['name']

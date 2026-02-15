# sensors/admin.py

from django.contrib import admin
from .models import (
    SensorType, MonitoringDevice, SensorReading,
    SensorAlert, AlertNotificationRule
)


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_type', 'unit', 'min_value', 'max_value', 'is_active']
    list_filter = ['measurement_type', 'is_active']
    search_fields = ['name']


class SensorReadingInline(admin.TabularInline):
    model = SensorReading
    extra = 0
    fields = ['timestamp', 'value', 'status']
    readonly_fields = ['timestamp', 'value', 'status']
    max_num = 10
    ordering = ['-timestamp']


class SensorAlertInline(admin.TabularInline):
    model = SensorAlert
    extra = 0
    fields = ['severity', 'status', 'triggered_at', 'acknowledged_at']
    readonly_fields = ['triggered_at']
    max_num = 5
    ordering = ['-triggered_at']


@admin.register(MonitoringDevice)
class MonitoringDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'name', 'sensor_type', 'status',
        'last_reading_value', 'last_reading', 'alert_enabled'
    ]
    list_filter = ['sensor_type', 'status', 'alert_enabled']
    search_fields = ['device_id', 'name', 'location_description']
    readonly_fields = ['created_at', 'last_reading', 'last_reading_value']
    inlines = [SensorReadingInline, SensorAlertInline]

    fieldsets = (
        (None, {
            'fields': ('device_id', 'name', 'sensor_type', 'status')
        }),
        ('Network', {
            'fields': ('mac_address', 'ip_address')
        }),
        ('Location', {
            'fields': ('storage_unit', 'location_description')
        }),
        ('Configuration', {
            'fields': ('reading_interval_minutes', 'alert_enabled')
        }),
        ('Thresholds', {
            'fields': ('warning_min', 'warning_max', 'critical_min', 'critical_max')
        }),
        ('Current Reading', {
            'fields': ('last_reading', 'last_reading_value'),
            'classes': ('collapse',)
        }),
        ('Calibration', {
            'fields': ('installed_date', 'calibration_date', 'next_calibration_date'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'timestamp', 'value', 'status']
    list_filter = ['status', 'device__sensor_type', 'device']
    search_fields = ['device__name', 'device__device_id']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False  # Readings should be created by sensors, not manually


@admin.register(SensorAlert)
class SensorAlertAdmin(admin.ModelAdmin):
    list_display = [
        'device', 'severity', 'status', 'triggered_at',
        'acknowledged_by', 'resolved_by'
    ]
    list_filter = ['severity', 'status', 'device__sensor_type']
    search_fields = ['device__name', 'message']
    readonly_fields = ['triggered_at']
    raw_id_fields = ['reading']
    date_hierarchy = 'triggered_at'

    fieldsets = (
        (None, {
            'fields': ('device', 'reading', 'severity', 'status', 'message')
        }),
        ('Acknowledgement', {
            'fields': ('acknowledged_at', 'acknowledged_by')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Notification', {
            'fields': ('notification_sent', 'notification_sent_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['acknowledge_alerts', 'resolve_alerts']

    def acknowledge_alerts(self, request, queryset):
        for alert in queryset.filter(status='ACTIVE'):
            alert.acknowledge(request.user)
        self.message_user(request, f"Acknowledged {queryset.count()} alerts.")
    acknowledge_alerts.short_description = "Acknowledge selected alerts"

    def resolve_alerts(self, request, queryset):
        for alert in queryset.exclude(status='RESOLVED'):
            alert.resolve(request.user, 'Bulk resolved via admin')
        self.message_user(request, f"Resolved {queryset.count()} alerts.")
    resolve_alerts.short_description = "Resolve selected alerts"


@admin.register(AlertNotificationRule)
class AlertNotificationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    filter_horizontal = ['sensor_types', 'devices', 'notify_users']

    fieldsets = (
        (None, {
            'fields': ('name', 'is_active')
        }),
        ('Scope', {
            'fields': ('sensor_types', 'devices', 'severity_levels')
        }),
        ('Notification Targets', {
            'fields': ('notify_users', 'notify_emails', 'notify_sms')
        }),
    )

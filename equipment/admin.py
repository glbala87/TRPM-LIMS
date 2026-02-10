# equipment/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import InstrumentType, Instrument, MaintenanceRecord


class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ['maintenance_type', 'scheduled_date', 'status', 'performed_by', 'passed']
    readonly_fields = ['performed_by']
    ordering = ['-scheduled_date']
    max_num = 5


@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'manufacturer',
        'maintenance_interval_days', 'calibration_interval_days', 'is_active'
    ]
    list_filter = ['is_active', 'manufacturer']
    search_fields = ['name', 'code', 'manufacturer']
    ordering = ['name']


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'instrument_type', 'serial_number', 'status_display',
        'location', 'maintenance_status', 'calibration_status'
    ]
    list_filter = ['status', 'instrument_type', 'is_active']
    search_fields = ['name', 'serial_number', 'asset_number', 'model']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MaintenanceRecordInline]

    fieldsets = (
        ('Instrument Information', {
            'fields': ('name', 'instrument_type', 'serial_number', 'asset_number')
        }),
        ('Details', {
            'fields': ('manufacturer', 'model', 'firmware_version', 'software_version')
        }),
        ('Status & Location', {
            'fields': ('status', 'location', 'is_active')
        }),
        ('Purchase & Warranty', {
            'fields': ('purchase_date', 'installation_date', 'warranty_expiration'),
            'classes': ('collapse',)
        }),
        ('Maintenance Schedule', {
            'fields': (
                ('last_maintenance', 'next_maintenance'),
                ('last_calibration', 'next_calibration'),
            )
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Technical', {
            'fields': ('specifications', 'notes'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        colors = {
            'ACTIVE': '#38a169',
            'MAINTENANCE': '#d69e2e',
            'CALIBRATION': '#3182ce',
            'REPAIR': '#c53030',
            'RETIRED': '#718096',
            'OUT_OF_SERVICE': '#e53e3e',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def maintenance_status(self, obj):
        if obj.is_maintenance_due:
            return format_html('<span style="color: red;">DUE</span>')
        if obj.next_maintenance:
            return obj.next_maintenance
        return "-"
    maintenance_status.short_description = 'Maint.'

    def calibration_status(self, obj):
        if obj.is_calibration_due:
            return format_html('<span style="color: red;">DUE</span>')
        if obj.next_calibration:
            return obj.next_calibration
        return "-"
    calibration_status.short_description = 'Calib.'


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'instrument', 'maintenance_type', 'scheduled_date',
        'status_display', 'performed_by', 'passed', 'next_due'
    ]
    list_filter = ['maintenance_type', 'status', 'passed', 'scheduled_date']
    search_fields = ['instrument__name', 'instrument__serial_number', 'performed_by']
    readonly_fields = ['created_at']
    date_hierarchy = 'scheduled_date'

    fieldsets = (
        ('Instrument', {
            'fields': ('instrument',)
        }),
        ('Maintenance Details', {
            'fields': ('maintenance_type', 'status', 'scheduled_date')
        }),
        ('Execution', {
            'fields': (
                ('performed_at', 'completed_at'),
                'performed_by', 'performed_by_user',
                'service_provider'
            )
        }),
        ('Work Performed', {
            'fields': ('description', 'findings', 'actions_taken', 'parts_replaced')
        }),
        ('Result', {
            'fields': ('passed', 'certificate', 'certificate_number', 'next_due')
        }),
        ('Cost & Notes', {
            'fields': ('cost', 'notes'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        colors = {
            'SCHEDULED': '#3182ce',
            'IN_PROGRESS': '#d69e2e',
            'COMPLETED': '#38a169',
            'CANCELLED': '#718096',
            'FAILED': '#c53030',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

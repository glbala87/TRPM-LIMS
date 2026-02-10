# molecular_diagnostics/admin/qc.py

from django.contrib import admin
from django.utils.html import format_html
from ..models import QCMetricDefinition, ControlSample, QCRecord


@admin.register(QCMetricDefinition)
class QCMetricDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'metric_type', 'acceptable_range',
        'is_critical', 'is_active'
    ]
    list_filter = ['metric_type', 'is_critical', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

    fieldsets = (
        ('Metric Information', {
            'fields': ('name', 'code', 'description', 'metric_type', 'unit')
        }),
        ('Acceptable Range', {
            'fields': ('min_acceptable', 'max_acceptable', 'target_value')
        }),
        ('Warning Thresholds', {
            'fields': ('warning_min', 'warning_max'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('applicable_test_types', 'is_critical', 'is_active')
        }),
    )

    def acceptable_range(self, obj):
        if obj.min_acceptable is not None and obj.max_acceptable is not None:
            return f"{obj.min_acceptable} - {obj.max_acceptable} {obj.unit or ''}"
        elif obj.min_acceptable is not None:
            return f">= {obj.min_acceptable} {obj.unit or ''}"
        elif obj.max_acceptable is not None:
            return f"<= {obj.max_acceptable} {obj.unit or ''}"
        return "-"
    acceptable_range.short_description = 'Acceptable Range'


@admin.register(ControlSample)
class ControlSampleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'control_type', 'lot_number', 'expected_result',
        'expiration_status', 'is_active'
    ]
    list_filter = ['control_type', 'is_active', 'test_panel']
    search_fields = ['name', 'lot_number']
    ordering = ['control_type', 'name']

    fieldsets = (
        ('Control Information', {
            'fields': ('name', 'control_type', 'lot_number')
        }),
        ('Expected Results', {
            'fields': ('expected_result', 'expected_value_min', 'expected_value_max')
        }),
        ('Association', {
            'fields': ('target_gene', 'test_panel')
        }),
        ('Storage', {
            'fields': ('expiration_date', 'storage_temperature')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
    )

    def expiration_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">EXPIRED</span>')
        if obj.expiration_date:
            return obj.expiration_date
        return "-"
    expiration_status.short_description = 'Expiration'


@admin.register(QCRecord)
class QCRecordAdmin(admin.ModelAdmin):
    list_display = [
        'get_entity', 'metric', 'value', 'status_display',
        'recorded_at', 'recorded_by'
    ]
    list_filter = ['status', 'passed', 'metric', 'recorded_at']
    search_fields = [
        'instrument_run__run_id', 'pcr_plate__barcode',
        'metric__name', 'control_sample__name'
    ]
    readonly_fields = ['passed', 'status']
    date_hierarchy = 'recorded_at'

    fieldsets = (
        ('Entity', {
            'fields': ('instrument_run', 'pcr_plate')
        }),
        ('Metric & Value', {
            'fields': ('metric', 'control_sample', 'value', 'value_text')
        }),
        ('Result', {
            'fields': ('status', 'passed')
        }),
        ('Recording', {
            'fields': ('recorded_at', 'recorded_by')
        }),
        ('Review', {
            'fields': ('reviewed_at', 'reviewed_by', 'notes')
        }),
    )

    def get_entity(self, obj):
        if obj.instrument_run:
            return f"Run: {obj.instrument_run.run_id}"
        if obj.pcr_plate:
            return f"Plate: {obj.pcr_plate.barcode}"
        return "-"
    get_entity.short_description = 'Entity'

    def status_display(self, obj):
        colors = {
            'PENDING': '#3182ce',
            'PASSED': '#38a169',
            'FAILED': '#c53030',
            'WARNING': '#d69e2e',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

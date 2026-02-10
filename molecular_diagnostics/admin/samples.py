# molecular_diagnostics/admin/samples.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from ..models import MolecularSampleType, MolecularSample


@admin.register(MolecularSampleType)
class MolecularSampleTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'storage_temperature', 'stability_hours', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(MolecularSample)
class MolecularSampleAdmin(admin.ModelAdmin):
    list_display = [
        'sample_id', 'patient_name', 'sample_type', 'test_panel',
        'workflow_status_display', 'priority', 'received_datetime', 'tat_display'
    ]
    list_filter = [
        'workflow_status', 'priority', 'sample_type', 'test_panel',
        'is_active', 'received_datetime'
    ]
    search_fields = [
        'sample_id', 'lab_order__patient__first_name',
        'lab_order__patient__last_name', 'lab_order__patient__OP_NO'
    ]
    readonly_fields = ['sample_id', 'created_at', 'updated_at', 'tat_display']
    date_hierarchy = 'received_datetime'

    fieldsets = (
        ('Sample Information', {
            'fields': ('sample_id', 'lab_order', 'sample_type', 'test_panel')
        }),
        ('Workflow', {
            'fields': ('workflow_status', 'current_step', 'priority')
        }),
        ('Timing', {
            'fields': ('collection_datetime', 'received_datetime', 'tat_display')
        }),
        ('Storage', {
            'fields': ('storage_location',)
        }),
        ('Quality Metrics', {
            'fields': ('volume_ul', 'concentration_ng_ul', 'a260_280_ratio'),
            'classes': ('collapse',)
        }),
        ('Aliquot Information', {
            'fields': ('aliquot_of', 'aliquot_number'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    autocomplete_fields = ['lab_order', 'sample_type', 'test_panel', 'storage_location', 'aliquot_of']

    actions = ['mark_extracted', 'mark_amplified', 'mark_analyzed', 'mark_reported']

    def patient_name(self, obj):
        patient = obj.lab_order.patient
        return f"{patient.first_name} {patient.last_name}"
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'lab_order__patient__first_name'

    def workflow_status_display(self, obj):
        colors = {
            'RECEIVED': '#3182ce',
            'EXTRACTED': '#805ad5',
            'AMPLIFIED': '#d69e2e',
            'SEQUENCED': '#38a169',
            'ANALYZED': '#2f855a',
            'REPORTED': '#276749',
            'CANCELLED': '#718096',
            'FAILED': '#c53030',
        }
        color = colors.get(obj.workflow_status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_workflow_status_display()
        )
    workflow_status_display.short_description = 'Status'
    workflow_status_display.admin_order_field = 'workflow_status'

    def tat_display(self, obj):
        hours = obj.get_turnaround_time()
        if obj.test_panel and obj.test_panel.tat_hours:
            target = obj.test_panel.tat_hours
            percentage = (hours / target) * 100
            if percentage > 100:
                color = '#c53030'
            elif percentage > 75:
                color = '#d69e2e'
            else:
                color = '#38a169'
            return format_html(
                '<span style="color: {};">{:.1f}h / {}h ({:.0f}%)</span>',
                color, hours, target, percentage
            )
        return f"{hours:.1f}h"
    tat_display.short_description = 'TAT'

    @admin.action(description='Mark selected samples as Extracted')
    def mark_extracted(self, request, queryset):
        from ..services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        count, failed = engine.bulk_transition(
            queryset, 'EXTRACTED', user=request.user
        )
        self.message_user(request, f'{count} samples marked as Extracted')

    @admin.action(description='Mark selected samples as Amplified')
    def mark_amplified(self, request, queryset):
        from ..services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        count, failed = engine.bulk_transition(
            queryset, 'AMPLIFIED', user=request.user
        )
        self.message_user(request, f'{count} samples marked as Amplified')

    @admin.action(description='Mark selected samples as Analyzed')
    def mark_analyzed(self, request, queryset):
        from ..services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        count, failed = engine.bulk_transition(
            queryset, 'ANALYZED', user=request.user
        )
        self.message_user(request, f'{count} samples marked as Analyzed')

    @admin.action(description='Mark selected samples as Reported')
    def mark_reported(self, request, queryset):
        from ..services.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        count, failed = engine.bulk_transition(
            queryset, 'REPORTED', user=request.user
        )
        self.message_user(request, f'{count} samples marked as Reported')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# molecular_diagnostics/admin/workflows.py

from django.contrib import admin
from ..models import WorkflowDefinition, WorkflowStep, SampleHistory


class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 0
    fields = ['order', 'name', 'code', 'status_on_entry', 'requires_qc', 'is_terminal']
    ordering = ['order']


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'step_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    inlines = [WorkflowStepInline]

    def step_count(self, obj):
        return obj.steps.count()
    step_count.short_description = 'Steps'


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = [
        'workflow', 'order', 'name', 'code',
        'status_on_entry', 'requires_qc', 'is_terminal'
    ]
    list_filter = ['workflow', 'status_on_entry', 'requires_qc', 'is_terminal']
    search_fields = ['name', 'code', 'workflow__name']
    filter_horizontal = ['allowed_transitions', 'qc_metrics', 'required_instruments']
    ordering = ['workflow', 'order']

    fieldsets = (
        ('Step Information', {
            'fields': ('workflow', 'name', 'code', 'order', 'description')
        }),
        ('Status', {
            'fields': ('status_on_entry', 'is_terminal')
        }),
        ('Transitions', {
            'fields': ('allowed_transitions',)
        }),
        ('QC Requirements', {
            'fields': ('requires_qc', 'qc_metrics')
        }),
        ('Equipment', {
            'fields': ('required_instruments', 'estimated_duration_hours')
        }),
    )


@admin.register(SampleHistory)
class SampleHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'sample', 'from_status', 'to_status',
        'timestamp', 'user', 'qc_passed'
    ]
    list_filter = ['to_status', 'qc_passed', 'timestamp']
    search_fields = ['sample__sample_id', 'user__username', 'notes']
    readonly_fields = [
        'sample', 'from_status', 'to_status', 'from_step', 'to_step',
        'timestamp', 'user', 'instrument_run', 'qc_passed', 'qc_notes', 'notes'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

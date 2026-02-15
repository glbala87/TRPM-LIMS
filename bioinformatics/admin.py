# bioinformatics/admin.py

from django.contrib import admin
from .models import (
    Pipeline, PipelineParameter, BioinformaticsService,
    AnalysisJob, AnalysisResult, ServiceDelivery
)


class PipelineParameterInline(admin.TabularInline):
    model = PipelineParameter
    extra = 0
    fields = ['name', 'display_name', 'param_type', 'default_value', 'is_required', 'order']


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'version', 'pipeline_type', 'executor', 'is_active']
    list_filter = ['pipeline_type', 'executor', 'is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at']
    inlines = [PipelineParameterInline]

    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'version', 'description')
        }),
        ('Configuration', {
            'fields': ('pipeline_type', 'executor', 'repository_url', 'config_file')
        }),
        ('Resources', {
            'fields': ('default_cpu', 'default_memory_gb', 'default_time_hours')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PipelineParameter)
class PipelineParameterAdmin(admin.ModelAdmin):
    list_display = ['pipeline', 'name', 'display_name', 'param_type', 'is_required', 'order']
    list_filter = ['pipeline', 'param_type', 'is_required']
    search_fields = ['name', 'display_name', 'pipeline__name']


class AnalysisJobInline(admin.TabularInline):
    model = AnalysisJob
    extra = 0
    fields = ['job_id', 'sample', 'status', 'runtime_seconds']
    readonly_fields = ['job_id', 'status', 'runtime_seconds']


class ServiceDeliveryInline(admin.TabularInline):
    model = ServiceDelivery
    extra = 0
    fields = ['delivery_method', 'delivery_path', 'delivered_at', 'delivered_by']


@admin.register(BioinformaticsService)
class BioinformaticsServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_id', 'title', 'pipeline', 'status', 'priority',
        'requested_by', 'requested_at'
    ]
    list_filter = ['status', 'priority', 'pipeline']
    search_fields = ['service_id', 'title', 'requested_by__username']
    readonly_fields = ['service_id', 'requested_at', 'approved_at', 'started_at', 'completed_at', 'delivered_at']
    filter_horizontal = ['samples', 'instrument_runs']
    inlines = [AnalysisJobInline, ServiceDeliveryInline]

    fieldsets = (
        (None, {
            'fields': ('service_id', 'title', 'description', 'pipeline', 'priority', 'status')
        }),
        ('Samples & Runs', {
            'fields': ('samples', 'instrument_runs')
        }),
        ('Parameters', {
            'fields': ('parameters', 'output_directory'),
            'classes': ('collapse',)
        }),
        ('People', {
            'fields': ('requested_by', 'approved_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'approved_at', 'started_at', 'completed_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


class AnalysisResultInline(admin.TabularInline):
    model = AnalysisResult
    extra = 0
    fields = ['result_type', 'file_path', 'file_size_bytes', 'created_at']
    readonly_fields = ['created_at']


@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    list_display = [
        'job_id', 'service', 'sample', 'status',
        'runtime_seconds', 'exit_code', 'submitted_at'
    ]
    list_filter = ['status', 'service__pipeline']
    search_fields = ['job_id', 'service__service_id', 'sample__sample_id']
    readonly_fields = ['created_at', 'submitted_at', 'started_at', 'completed_at']
    inlines = [AnalysisResultInline]

    fieldsets = (
        (None, {
            'fields': ('job_id', 'service', 'sample', 'status')
        }),
        ('Execution', {
            'fields': ('cluster_job_id', 'work_directory', 'log_file')
        }),
        ('Resources', {
            'fields': ('cpu_hours', 'memory_peak_gb', 'runtime_seconds', 'exit_code')
        }),
        ('Errors', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'submitted_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['job', 'result_type', 'file_path', 'file_size_bytes', 'created_at']
    list_filter = ['result_type']
    search_fields = ['job__job_id', 'file_path']


@admin.register(ServiceDelivery)
class ServiceDeliveryAdmin(admin.ModelAdmin):
    list_display = ['service', 'delivery_method', 'delivered_at', 'delivered_by', 'acknowledged_at']
    list_filter = ['delivery_method']
    search_fields = ['service__service_id']

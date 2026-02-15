"""
Admin configuration for data_exchange app.
"""
from django.contrib import admin
from .models import ImportJob, ImportedRecord, ExportTemplate, ExportJob


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_type', 'status', 'total_rows', 'successful_rows', 'failed_rows', 'created_by', 'created_at')
    list_filter = ('status', 'data_type', 'created_at')
    search_fields = ('original_filename',)
    readonly_fields = ('id', 'created_at', 'started_at', 'completed_at', 'validation_errors', 'import_errors')
    date_hierarchy = 'created_at'


@admin.register(ImportedRecord)
class ImportedRecordAdmin(admin.ModelAdmin):
    list_display = ('import_job', 'row_number', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('raw_data', 'error_message')


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_type', 'output_format', 'is_public', 'created_by')
    list_filter = ('data_type', 'output_format', 'is_public')
    search_fields = ('name', 'description')


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_type', 'output_format', 'status', 'record_count', 'created_by', 'created_at')
    list_filter = ('status', 'data_type', 'output_format')
    readonly_fields = ('id', 'created_at', 'completed_at')
    date_hierarchy = 'created_at'

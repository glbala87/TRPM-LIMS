"""
Admin configuration for data_exchange app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ImportJob, ImportedRecord, ExportTemplate, ExportJob, ExternalSystem, MessageLog


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


@admin.register(ExternalSystem)
class ExternalSystemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'protocol', 'transport', 'connection_display',
        'status_badge', 'last_connection_at'
    ]
    list_filter = ['protocol', 'transport', 'status']
    search_fields = ['name', 'description', 'host']
    ordering = ['name']

    fieldsets = (
        ('System Identification', {
            'fields': ('name', 'description', 'system_type', 'status')
        }),
        ('Protocol Configuration', {
            'fields': ('protocol', 'protocol_version')
        }),
        ('Transport Configuration', {
            'fields': ('transport', 'host', 'port', 'path', 'timeout_seconds')
        }),
        ('Authentication', {
            'fields': ('credentials',),
            'classes': ('collapse',),
        }),
        ('HL7 v2 Settings', {
            'fields': (
                'hl7_sending_application', 'hl7_sending_facility',
                'hl7_receiving_application', 'hl7_receiving_facility',
                'hl7_version'
            ),
            'classes': ('collapse',),
        }),
        ('FHIR Settings', {
            'fields': ('fhir_base_url', 'fhir_client_id', 'fhir_capabilities'),
            'classes': ('collapse',),
        }),
        ('Connection Settings', {
            'fields': ('retry_attempts', 'retry_delay_seconds', 'message_encoding', 'auto_acknowledge')
        }),
        ('Status', {
            'fields': ('last_connection_at', 'last_error'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['last_connection_at', 'last_error']

    def connection_display(self, obj):
        return obj.connection_string
    connection_display.short_description = 'Connection'

    def status_badge(self, obj):
        colors = {
            'ACTIVE': '#28a745',
            'INACTIVE': '#6c757d',
            'TESTING': '#17a2b8',
            'ERROR': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['test_connection', 'activate', 'deactivate']

    @admin.action(description='Test connection')
    def test_connection(self, request, queryset):
        for system in queryset:
            try:
                # Simple connection test
                if system.transport in ['MLLP', 'HTTP']:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((system.host, system.port))
                    sock.close()
                    if result == 0:
                        system.status = 'ACTIVE'
                        self.message_user(request, f"{system.name}: Connection successful")
                    else:
                        system.status = 'ERROR'
                        system.last_error = f"Connection refused (error {result})"
                        self.message_user(request, f"{system.name}: Connection failed", level='ERROR')
                    system.save()
            except Exception as e:
                system.status = 'ERROR'
                system.last_error = str(e)
                system.save()
                self.message_user(request, f"{system.name}: {e}", level='ERROR')

    @admin.action(description='Activate selected systems')
    def activate(self, request, queryset):
        queryset.update(status='ACTIVE')

    @admin.action(description='Deactivate selected systems')
    def deactivate(self, request, queryset):
        queryset.update(status='INACTIVE')


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = [
        'message_id', 'external_system', 'message_type', 'direction',
        'status_badge', 'retry_count', 'created_at'
    ]
    list_filter = ['external_system', 'message_type', 'direction', 'status', 'created_at']
    search_fields = ['message_id', 'raw_message']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    readonly_fields = [
        'id', 'message_id', 'raw_message_preview', 'parsed_message',
        'created_at', 'sent_at', 'acknowledged_at',
        'acknowledgment_code', 'acknowledgment_message'
    ]

    fieldsets = (
        ('Message Identification', {
            'fields': ('id', 'external_system', 'direction', 'message_id', 'message_type')
        }),
        ('Message Content', {
            'fields': ('raw_message_preview', 'parsed_message'),
        }),
        ('Status', {
            'fields': ('status', 'status_message', 'retry_count', 'next_retry_at')
        }),
        ('Acknowledgment', {
            'fields': ('acknowledgment_id', 'acknowledgment_code', 'acknowledgment_message'),
            'classes': ('collapse',),
        }),
        ('Linked Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'acknowledged_at'),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'SENDING': '#17a2b8',
            'SENT': '#28a745',
            'ACKNOWLEDGED': '#28a745',
            'FAILED': '#dc3545',
            'REJECTED': '#dc3545',
            'RETRYING': '#fd7e14',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def raw_message_preview(self, obj):
        # Show first 1000 characters with scroll
        content = obj.raw_message[:2000] if obj.raw_message else ''
        return format_html(
            '<pre style="max-height: 300px; overflow: auto; white-space: pre-wrap;">{}</pre>',
            content
        )
    raw_message_preview.short_description = 'Raw Message (Preview)'

    actions = ['retry_messages', 'mark_acknowledged']

    @admin.action(description='Retry selected messages')
    def retry_messages(self, request, queryset):
        from .services import MessageRouter
        count = 0
        for log in queryset.filter(status__in=['FAILED', 'REJECTED']):
            router = MessageRouter(log.external_system)
            try:
                router._retry_message(log)
                count += 1
            except Exception as e:
                self.message_user(request, f"Retry failed for {log.id}: {e}", level='ERROR')
        self.message_user(request, f"Retried {count} messages.")

    @admin.action(description='Mark as acknowledged')
    def mark_acknowledged(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='ACKNOWLEDGED', acknowledged_at=timezone.now())

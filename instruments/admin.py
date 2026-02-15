# instruments/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import InstrumentConnection, MessageLog, WorklistExport


@admin.register(InstrumentConnection)
class InstrumentConnectionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'instrument',
        'protocol',
        'connection_type',
        'host_port_display',
        'status_badge',
        'is_active',
        'last_connection',
    ]
    list_filter = [
        'protocol',
        'connection_type',
        'connection_status',
        'is_active',
        'auto_start',
    ]
    search_fields = [
        'name',
        'instrument__name',
        'instrument__serial_number',
        'host',
    ]
    readonly_fields = [
        'connection_status',
        'last_connection',
        'last_message',
        'last_error',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        (None, {
            'fields': ('instrument', 'name', 'protocol', 'connection_type')
        }),
        ('Network Settings', {
            'fields': ('host', 'port'),
            'classes': ('collapse',),
        }),
        ('Serial Settings', {
            'fields': ('serial_port', 'baud_rate'),
            'classes': ('collapse',),
        }),
        ('Connection Parameters', {
            'fields': ('timeout', 'retry_interval', 'max_retries'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': (
                'is_active',
                'auto_start',
                'connection_status',
                'last_connection',
                'last_message',
                'last_error',
            ),
        }),
        ('Protocol Configuration', {
            'fields': ('protocol_config',),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',),
        }),
    )

    def host_port_display(self, obj):
        if obj.connection_type == 'SERIAL':
            return obj.serial_port
        return f"{obj.host}:{obj.port}"
    host_port_display.short_description = 'Address'

    def status_badge(self, obj):
        colors = {
            'CONNECTED': 'green',
            'DISCONNECTED': 'gray',
            'CONNECTING': 'orange',
            'ERROR': 'red',
        }
        color = colors.get(obj.connection_status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.connection_status
        )
    status_badge.short_description = 'Status'


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'connection',
        'direction_badge',
        'message_type',
        'status_badge',
        'related_sample_id',
        'message_preview',
    ]
    list_filter = [
        'direction',
        'message_type',
        'status',
        'connection__instrument',
        'connection__protocol',
        ('timestamp', admin.DateFieldListFilter),
    ]
    search_fields = [
        'raw_message',
        'related_sample_id',
        'related_patient_id',
        'related_order_id',
        'connection__instrument__name',
    ]
    readonly_fields = [
        'connection',
        'direction',
        'message_type',
        'raw_message',
        'parsed_data',
        'status',
        'error_message',
        'timestamp',
        'processed_at',
        'checksum',
        'checksum_valid',
    ]
    date_hierarchy = 'timestamp'

    fieldsets = (
        (None, {
            'fields': ('connection', 'direction', 'message_type', 'status')
        }),
        ('Message Content', {
            'fields': ('raw_message', 'parsed_data'),
        }),
        ('Related Records', {
            'fields': ('related_sample_id', 'related_patient_id', 'related_order_id'),
        }),
        ('Processing', {
            'fields': ('error_message', 'timestamp', 'processed_at'),
        }),
        ('Validation', {
            'fields': ('checksum', 'checksum_valid'),
            'classes': ('collapse',),
        }),
    )

    def direction_badge(self, obj):
        if obj.direction == 'INBOUND':
            return format_html(
                '<span style="color: blue;">&darr; IN</span>'
            )
        return format_html(
            '<span style="color: green;">&uarr; OUT</span>'
        )
    direction_badge.short_description = 'Dir'

    def status_badge(self, obj):
        colors = {
            'RECEIVED': 'blue',
            'PARSED': 'cyan',
            'PROCESSED': 'green',
            'SENT': 'green',
            'ACKNOWLEDGED': 'darkgreen',
            'ERROR': 'red',
            'IGNORED': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'

    def message_preview(self, obj):
        preview = obj.raw_message[:100]
        if len(obj.raw_message) > 100:
            preview += '...'
        # Escape special characters for display
        preview = preview.replace('\x02', '[STX]').replace('\x03', '[ETX]')
        preview = preview.replace('\r', '[CR]').replace('\n', '[LF]')
        return preview
    message_preview.short_description = 'Message'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WorklistExport)
class WorklistExportAdmin(admin.ModelAdmin):
    list_display = [
        'connection',
        'status',
        'sample_count',
        'created_at',
        'sent_at',
        'created_by',
    ]
    list_filter = [
        'status',
        'connection__instrument',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = [
        'connection__instrument__name',
        'samples',
    ]
    readonly_fields = [
        'created_at',
        'sent_at',
        'acknowledged_at',
        'completed_at',
    ]

    def sample_count(self, obj):
        return len(obj.samples) if obj.samples else 0
    sample_count.short_description = 'Samples'

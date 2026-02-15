"""
Admin configuration for the audit app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, AuditTrail


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for AuditLog model."""
    list_display = (
        'timestamp', 'username', 'action', 'content_type',
        'object_repr_short', 'ip_address'
    )
    list_filter = ('action', 'content_type', 'timestamp')
    search_fields = ('username', 'object_repr', 'ip_address', 'notes')
    readonly_fields = (
        'timestamp', 'user', 'username', 'action', 'content_type',
        'object_id', 'object_repr', 'changed_fields_display',
        'ip_address', 'user_agent', 'request_path', 'request_method', 'notes'
    )
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    fieldsets = (
        ('Action', {
            'fields': ('timestamp', 'action', 'user', 'username')
        }),
        ('Object', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changed_fields_display',),
        }),
        ('Request Context', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Audit logs are created automatically

    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete audit logs
        return request.user.is_superuser

    def object_repr_short(self, obj):
        """Truncate object representation for list display."""
        if len(obj.object_repr) > 50:
            return obj.object_repr[:50] + '...'
        return obj.object_repr
    object_repr_short.short_description = 'Object'

    def changed_fields_display(self, obj):
        """Display changed fields in a readable format."""
        if not obj.changed_fields:
            return '-'

        html_parts = ['<table style="border-collapse: collapse;">']
        html_parts.append('<tr><th>Field</th><th>Old Value</th><th>New Value</th></tr>')

        for field, values in obj.changed_fields.items():
            old_val = values.get('old', 'N/A')
            new_val = values.get('new', 'N/A')

            # Truncate long values
            if isinstance(old_val, str) and len(old_val) > 100:
                old_val = old_val[:100] + '...'
            if isinstance(new_val, str) and len(new_val) > 100:
                new_val = new_val[:100] + '...'

            html_parts.append(
                f'<tr><td><strong>{field}</strong></td>'
                f'<td style="color: #c00;">{old_val}</td>'
                f'<td style="color: #0a0;">{new_val}</td></tr>'
            )

        html_parts.append('</table>')
        return format_html(''.join(html_parts))
    changed_fields_display.short_description = 'Changes'


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    """Admin for AuditTrail model."""
    list_display = ('content_type', 'object_id', 'version', 'action', 'user', 'timestamp')
    list_filter = ('content_type', 'action', 'timestamp')
    search_fields = ('object_id',)
    readonly_fields = ('content_type', 'object_id', 'version', 'snapshot_display', 'user', 'timestamp', 'action')
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False  # Audit trails are created automatically

    def has_change_permission(self, request, obj=None):
        return False  # Audit trails should not be modified

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def snapshot_display(self, obj):
        """Display snapshot in a readable format."""
        if not obj.snapshot:
            return '-'

        html_parts = ['<table style="border-collapse: collapse;">']
        html_parts.append('<tr><th>Field</th><th>Value</th></tr>')

        for field, value in obj.snapshot.items():
            # Truncate long values
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + '...'
            html_parts.append(f'<tr><td><strong>{field}</strong></td><td>{value}</td></tr>')

        html_parts.append('</table>')
        return format_html(''.join(html_parts))
    snapshot_display.short_description = 'Snapshot'

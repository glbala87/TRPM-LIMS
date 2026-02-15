"""
Audit logging models for TRPM-LIMS.

Provides comprehensive tracking of all data modifications including:
- User who made the change
- Timestamp of the change
- Before/after values for changed fields
- IP address and user agent
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import json


class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all data changes in the LIMS.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('EXPORT', 'Exported'),
        ('IMPORT', 'Imported'),
        ('LOGIN', 'Logged In'),
        ('LOGOUT', 'Logged Out'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('APPROVE', 'Approved'),
        ('REJECT', 'Rejected'),
        ('TRANSITION', 'Status Transition'),
        ('PRINT', 'Printed'),
        ('EMAIL', 'Emailed'),
    ]

    # Timestamp and user
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username snapshot at time of action (in case user is deleted)"
    )

    # Action type
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)

    # Object reference using ContentType framework
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Object information snapshot
    object_repr = models.CharField(
        max_length=500,
        blank=True,
        help_text="String representation of the object"
    )

    # Change details
    changed_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary of changed fields with old and new values"
    )

    # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)

    # Additional notes
    notes = models.TextField(blank=True, help_text="Additional context or notes")

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.username or 'System'} - {self.action} - {self.object_repr}"

    @classmethod
    def log_action(cls, action, obj=None, user=None, request=None, changed_fields=None, notes=''):
        """
        Create an audit log entry.

        Args:
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            obj: The model instance being acted upon
            user: The user performing the action
            request: The HTTP request (optional, for extracting IP, etc.)
            changed_fields: Dict of {field_name: {'old': value, 'new': value}}
            notes: Additional notes
        """
        log_entry = cls(
            action=action,
            changed_fields=changed_fields or {},
            notes=notes
        )

        # Set user information
        if user:
            log_entry.user = user
            log_entry.username = user.username

        # Set object information
        if obj:
            log_entry.content_type = ContentType.objects.get_for_model(obj)
            log_entry.object_id = obj.pk
            log_entry.object_repr = str(obj)[:500]

        # Set request information
        if request:
            log_entry.ip_address = cls._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            log_entry.request_path = request.path[:500]
            log_entry.request_method = request.method

        log_entry.save()
        return log_entry

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @classmethod
    def log_create(cls, obj, user=None, request=None, notes=''):
        """Log object creation."""
        return cls.log_action('CREATE', obj, user, request, notes=notes)

    @classmethod
    def log_update(cls, obj, changed_fields, user=None, request=None, notes=''):
        """Log object update with field changes."""
        return cls.log_action('UPDATE', obj, user, request, changed_fields, notes)

    @classmethod
    def log_delete(cls, obj, user=None, request=None, notes=''):
        """Log object deletion."""
        return cls.log_action('DELETE', obj, user, request, notes=notes)

    @classmethod
    def log_login(cls, user, request=None, success=True):
        """Log user login attempt."""
        action = 'LOGIN' if success else 'LOGIN_FAILED'
        return cls.log_action(action, user=user, request=request)

    @classmethod
    def log_logout(cls, user, request=None):
        """Log user logout."""
        return cls.log_action('LOGOUT', user=user, request=request)

    def get_changed_fields_display(self):
        """Get a human-readable representation of changed fields."""
        if not self.changed_fields:
            return ""

        lines = []
        for field, values in self.changed_fields.items():
            old_val = values.get('old', 'N/A')
            new_val = values.get('new', 'N/A')
            lines.append(f"{field}: '{old_val}' → '{new_val}'")
        return "\n".join(lines)


class AuditTrail(models.Model):
    """
    Simplified audit trail for quick access to object history.
    Can be attached to any model via foreign key.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    version = models.PositiveIntegerField(default=1)
    snapshot = models.JSONField(
        default=dict,
        help_text="Complete snapshot of object state"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Audit Trail'
        verbose_name_plural = 'Audit Trails'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-version']),
        ]
        unique_together = ['content_type', 'object_id', 'version']

    def __str__(self):
        return f"{self.content_type} #{self.object_id} v{self.version}"

    @classmethod
    def create_snapshot(cls, obj, user=None, action='UPDATE'):
        """Create a new snapshot of an object's state."""
        content_type = ContentType.objects.get_for_model(obj)

        # Get the latest version number
        latest = cls.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('-version').first()

        version = (latest.version + 1) if latest else 1

        # Create snapshot from model fields
        snapshot = {}
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            # Convert non-JSON-serializable types
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            elif hasattr(value, 'pk'):
                value = value.pk
            snapshot[field.name] = value

        return cls.objects.create(
            content_type=content_type,
            object_id=obj.pk,
            version=version,
            snapshot=snapshot,
            user=user,
            action=action
        )

    @classmethod
    def get_history(cls, obj):
        """Get complete history for an object."""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('-version')

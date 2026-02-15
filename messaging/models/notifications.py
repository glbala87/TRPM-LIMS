# messaging/models/notifications.py
"""
Notification and announcement models.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid


class Notification(models.Model):
    """
    System notification sent to users, groups, or departments.
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    NOTIFICATION_TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('ACTION', 'Action Required'),
    ]

    notification_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique notification identifier"
    )

    # Title and content
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='INFO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')

    # Targets (can target users, groups, or departments)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        blank=True
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='notifications',
        blank=True
    )
    departments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of department names to notify"
    )

    # Laboratory scoping
    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    is_global = models.BooleanField(default=False, help_text="Show to all users in organization")

    # Linked object
    linked_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    linked_object_id = models.PositiveIntegerField(null=True, blank=True)
    linked_object = GenericForeignKey('linked_content_type', 'linked_object_id')

    # Action URL
    action_url = models.CharField(max_length=500, blank=True, help_text="URL for notification action")

    # Sender
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )

    # Read tracking (per user)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_notifications',
        blank=True
    )
    dismissed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='dismissed_notifications',
        blank=True
    )

    # Delivery status
    is_sent = models.BooleanField(default=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Email notification
    send_email = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['priority', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.notification_id:
            self.notification_id = self._generate_notification_id()
        super().save(*args, **kwargs)

    def _generate_notification_id(self):
        """Generate unique notification ID with format: NOT-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"NOT-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.notification_id}: {self.title}"

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def mark_as_read(self, user):
        """Mark notification as read by user."""
        self.read_by.add(user)

    def dismiss(self, user):
        """Dismiss notification for user."""
        self.dismissed_by.add(user)

    def is_read_by_user(self, user):
        """Check if notification is read by user."""
        return self.read_by.filter(id=user.id).exists()


class Notice(models.Model):
    """
    Public announcement/notice board entry.
    """
    notice_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique notice identifier"
    )

    title = models.CharField(max_length=255)
    body = models.TextField()

    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_notices'
    )

    # Laboratory scoping
    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='notices',
        null=True,
        blank=True
    )

    # Visibility
    is_pinned = models.BooleanField(default=False)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)

    # Audience
    AUDIENCE_CHOICES = [
        ('ALL', 'All Users'),
        ('LAB', 'Laboratory Staff'),
        ('MANAGERS', 'Managers Only'),
        ('CUSTOM', 'Custom Groups'),
    ]
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='ALL')
    audience_groups = models.ManyToManyField(
        'auth.Group',
        related_name='notices',
        blank=True
    )

    # Styling
    STYLE_CHOICES = [
        ('DEFAULT', 'Default'),
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('DANGER', 'Danger'),
    ]
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='DEFAULT')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        ordering = ['-is_pinned', '-publish_date']

    def save(self, *args, **kwargs):
        if not self.notice_id:
            self.notice_id = self._generate_notice_id()
        super().save(*args, **kwargs)

    def _generate_notice_id(self):
        """Generate unique notice ID with format: NTC-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"NTC-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.notice_id}: {self.title}"

    @property
    def is_published(self):
        now = timezone.now()
        if self.publish_date > now:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return self.is_active

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False

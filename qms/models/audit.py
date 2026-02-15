# qms/models/audit.py
"""
Audit and subscription models for QMS documents.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class DocumentAudit(models.Model):
    """
    Audit trail for document actions.
    Tracks views, downloads, prints, edits, and status changes.
    """
    ACTION_CHOICES = [
        ('VIEWED', 'Viewed'),
        ('DOWNLOADED', 'Downloaded'),
        ('PRINTED', 'Printed'),
        ('CREATED', 'Created'),
        ('EDITED', 'Edited'),
        ('VERSION_CREATED', 'Version Created'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('SHARED', 'Shared'),
        ('COMMENTED', 'Commented'),
        ('REVIEWED', 'Reviewed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
        ('RESTORED', 'Restored'),
        ('DELETED', 'Deleted'),
    ]

    document = models.ForeignKey(
        'qms.Document',
        on_delete=models.CASCADE,
        related_name='audit_trail'
    )
    version = models.ForeignKey(
        'qms.DocumentVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trail'
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_audit_entries'
    )

    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    session_id = models.CharField(max_length=100, blank=True)

    # Additional details
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Document Audit"
        verbose_name_plural = "Document Audits"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.document} - {self.get_action_display()} by {self.user} at {self.timestamp}"


class DocumentSubscription(models.Model):
    """
    User subscriptions to document updates.
    """
    NOTIFY_ON_CHOICES = [
        ('ALL', 'All Changes'),
        ('STATUS', 'Status Changes Only'),
        ('VERSION', 'New Versions Only'),
        ('REVIEW', 'Review Requests Only'),
    ]

    document = models.ForeignKey(
        'qms.Document',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_subscriptions'
    )

    notify_on = models.CharField(max_length=20, choices=NOTIFY_ON_CHOICES, default='ALL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document Subscription"
        verbose_name_plural = "Document Subscriptions"
        unique_together = [['document', 'user']]

    def __str__(self):
        return f"{self.user} -> {self.document}"


class DocumentComment(models.Model):
    """
    Comments on documents for discussion and feedback.
    """
    document = models.ForeignKey(
        'qms.Document',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    version = models.ForeignKey(
        'qms.DocumentVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_comments'
    )
    content = models.TextField()

    # For inline comments
    line_number = models.PositiveIntegerField(null=True, blank=True)
    selected_text = models.TextField(blank=True)

    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document Comment"
        verbose_name_plural = "Document Comments"
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.document}"

    @property
    def reply_count(self):
        return self.replies.count()

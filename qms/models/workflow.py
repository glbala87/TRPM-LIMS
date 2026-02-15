# qms/models/workflow.py
"""
Document workflow models for review and approval processes.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class DocumentStatus(models.Model):
    """
    Status history for a document.
    Tracks transitions: DRAFT -> IN_REVIEW -> APPROVED -> PUBLISHED -> ARCHIVED
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_REVIEW', 'In Review'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
        ('SUPERSEDED', 'Superseded'),
        ('ARCHIVED', 'Archived'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    document = models.ForeignKey(
        'qms.Document',
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    version = models.ForeignKey(
        'qms.DocumentVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='status_history'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_status_changes'
    )
    comment = models.TextField(blank=True)

    # For published documents
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Document Status"
        verbose_name_plural = "Document Statuses"
        ordering = ['-date']

    def __str__(self):
        return f"{self.document} - {self.get_status_display()} ({self.date})"


class DocumentReviewCycle(models.Model):
    """
    Review cycle for a document version.
    Can have multiple review steps with different reviewers.
    """
    CYCLE_STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    document = models.ForeignKey(
        'qms.Document',
        on_delete=models.CASCADE,
        related_name='review_cycles'
    )
    version = models.ForeignKey(
        'qms.DocumentVersion',
        on_delete=models.CASCADE,
        related_name='review_cycles'
    )

    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_reviews'
    )
    initiated_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=CYCLE_STATUS_CHOICES, default='IN_PROGRESS')
    completed_at = models.DateTimeField(null=True, blank=True)

    due_date = models.DateField(null=True, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = "Document Review Cycle"
        verbose_name_plural = "Document Review Cycles"
        ordering = ['-initiated_at']

    def __str__(self):
        return f"Review: {self.document} v{self.version.version_number}"

    @property
    def all_approved(self):
        """Check if all review steps are approved."""
        steps = self.steps.all()
        return steps.exists() and not steps.exclude(status='APPROVED').exists()

    @property
    def has_rejection(self):
        """Check if any review step was rejected."""
        return self.steps.filter(status='REJECTED').exists()

    @property
    def pending_reviewers(self):
        """Return list of reviewers with pending reviews."""
        return [step.reviewer for step in self.steps.filter(status='PENDING')]


class DocumentReviewStep(models.Model):
    """
    Individual review step within a review cycle.
    """
    STEP_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SKIPPED', 'Skipped'),
    ]

    review_cycle = models.ForeignKey(
        DocumentReviewCycle,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_steps'
    )

    sequence = models.PositiveSmallIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    role = models.CharField(max_length=50, blank=True, help_text="e.g., Technical Reviewer, QA Manager")

    status = models.CharField(max_length=20, choices=STEP_STATUS_CHOICES, default='PENDING')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    # Digital signature
    signature_hash = models.CharField(max_length=64, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Document Review Step"
        verbose_name_plural = "Document Review Steps"
        ordering = ['review_cycle', 'sequence']
        unique_together = [['review_cycle', 'reviewer']]

    def __str__(self):
        return f"{self.review_cycle} - {self.reviewer} ({self.get_status_display()})"

    def approve(self, comment=''):
        """Mark this step as approved."""
        self.status = 'APPROVED'
        self.reviewed_at = timezone.now()
        self.comment = comment
        self.save()

    def reject(self, comment=''):
        """Mark this step as rejected."""
        self.status = 'REJECTED'
        self.reviewed_at = timezone.now()
        self.comment = comment
        self.save()

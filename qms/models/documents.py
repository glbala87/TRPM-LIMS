# qms/models/documents.py
"""
Core document and version models for QMS.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import os


def document_file_path(instance, filename):
    """Generate file path for document uploads."""
    ext = filename.split('.')[-1]
    new_filename = f"{instance.document.document_id}_v{instance.version_number}.{ext}"
    return os.path.join('qms', 'documents', str(instance.document.laboratory_id), new_filename)


class Document(models.Model):
    """
    Core document entity in the QMS.
    Documents have versions and go through a review workflow.
    """
    EDITOR_TYPE_CHOICES = [
        ('RICHTEXT', 'Rich Text'),
        ('MARKDOWN', 'Markdown'),
        ('HTML', 'HTML'),
        ('PDF', 'PDF Upload'),
        ('EXTERNAL', 'External Link'),
    ]

    document_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique document identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # Organization
    folder = models.ForeignKey(
        'qms.DocumentFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    category = models.ForeignKey(
        'qms.DocumentCategory',
        on_delete=models.PROTECT,
        related_name='documents'
    )
    template = models.ForeignKey(
        'qms.DocumentTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    # Basic info
    title = models.CharField(max_length=255)
    document_number = models.CharField(max_length=50, blank=True, help_text="Official document number")
    description = models.TextField(blank=True)
    editor_type = models.CharField(max_length=20, choices=EDITOR_TYPE_CHOICES, default='RICHTEXT')

    # Authorship
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='authored_documents',
        blank=True
    )

    # Access control
    readers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='readable_documents',
        blank=True,
        help_text="Users with explicit read access"
    )
    is_public = models.BooleanField(default=False, help_text="Accessible to all laboratory members")

    # Tags and relations
    tags = models.ManyToManyField('qms.DocumentTag', related_name='documents', blank=True)
    related_documents = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
        help_text="Related documents"
    )

    # Review schedule
    review_interval_days = models.PositiveIntegerField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)

    # External links
    external_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_date = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='archived_documents'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_documents'
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-updated_at']
        unique_together = [['laboratory', 'document_number']]

    def save(self, *args, **kwargs):
        if not self.document_id:
            self.document_id = self._generate_document_id()
        # Set review interval from category if not specified
        if self.review_interval_days is None and self.category:
            self.review_interval_days = self.category.review_interval_days
        super().save(*args, **kwargs)

    def _generate_document_id(self):
        """Generate unique document ID with format: DOC-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"DOC-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.document_number or self.document_id} - {self.title}"

    @property
    def latest_version(self):
        """Return the latest version of this document."""
        return self.versions.order_by('-created_at').first()

    @property
    def current_status(self):
        """Return the current document status."""
        status = self.status_history.order_by('-date').first()
        return status.status if status else 'DRAFT'

    @property
    def published_version(self):
        """Return the currently published version."""
        status = self.status_history.filter(status='PUBLISHED').order_by('-date').first()
        if status and status.version:
            return status.version
        return None


class DocumentVersion(models.Model):
    """
    Immutable version of a document.
    Each edit creates a new version.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.CharField(max_length=20, help_text="e.g., 1.0, 1.1, 2.0")
    is_major_version = models.BooleanField(default=False)

    # Content
    content = models.TextField(blank=True, help_text="Document content (for text-based documents)")
    file = models.FileField(upload_to=document_file_path, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)

    # Change tracking
    change_summary = models.TextField(blank=True, help_text="Summary of changes in this version")

    # Metadata
    word_count = models.PositiveIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA-256 checksum")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_versions'
    )

    class Meta:
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        ordering = ['-created_at']
        unique_together = [['document', 'version_number']]

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

    def save(self, *args, **kwargs):
        # Calculate word count for text content
        if self.content and not self.word_count:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    @property
    def previous_version(self):
        """Return the previous version."""
        return self.document.versions.filter(
            created_at__lt=self.created_at
        ).order_by('-created_at').first()

# qms/models/folders.py
"""
Document folder hierarchy for organizing QMS documents.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class DocumentFolder(models.Model):
    """
    Hierarchical folder structure for organizing documents.
    Tenant-scoped to laboratory.
    """
    folder_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique folder identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='document_folders'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    # Access control
    is_private = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_folders'
    )
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='accessible_folders'
    )

    # Sort order
    sequence = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document Folder"
        verbose_name_plural = "Document Folders"
        ordering = ['sequence', 'name']
        unique_together = [['laboratory', 'parent', 'name']]

    def save(self, *args, **kwargs):
        if not self.folder_id:
            self.folder_id = self._generate_folder_id()
        super().save(*args, **kwargs)

    def _generate_folder_id(self):
        """Generate unique folder ID with format: FLD-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"FLD-{date_str}-{unique_suffix}"

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        """Return full folder path."""
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return f"/{self.name}"

    @property
    def depth(self):
        """Return folder depth in hierarchy."""
        if self.parent:
            return self.parent.depth + 1
        return 0

    def get_ancestors(self):
        """Return list of ancestor folders."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        """Return all descendant folders."""
        descendants = []
        for child in self.children.filter(is_active=True):
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    @property
    def document_count(self):
        """Return count of documents in this folder."""
        return self.documents.filter(is_active=True).count()

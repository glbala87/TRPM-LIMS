# qms/models/reference.py
"""
Reference data models for QMS document management.
"""

from django.db import models


class DocumentCategory(models.Model):
    """
    Category for organizing documents (e.g., SOP, Policy, Form, Manual).
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prefix = models.CharField(max_length=10, blank=True, help_text="Document numbering prefix")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    review_interval_days = models.PositiveIntegerField(
        default=365,
        help_text="Default review interval for documents in this category"
    )
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Document Category"
        verbose_name_plural = "Document Categories"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class DocumentTag(models.Model):
    """
    Tags for document classification and search.
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3182ce', help_text="Hex color code")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Document Tag"
        verbose_name_plural = "Document Tags"
        ordering = ['name']

    def __str__(self):
        return self.name


class DocumentTemplate(models.Model):
    """
    Template for creating standardized documents.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates'
    )
    content = models.TextField(help_text="Template content with placeholders")
    editor_type = models.CharField(
        max_length=20,
        choices=[
            ('RICHTEXT', 'Rich Text'),
            ('MARKDOWN', 'Markdown'),
            ('HTML', 'HTML'),
        ],
        default='RICHTEXT'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document Template"
        verbose_name_plural = "Document Templates"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

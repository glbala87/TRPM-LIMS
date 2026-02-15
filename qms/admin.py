# qms/admin.py
"""
Django admin configuration for QMS module.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DocumentCategory, DocumentTag, DocumentTemplate,
    DocumentFolder,
    Document, DocumentVersion,
    DocumentStatus, DocumentReviewCycle, DocumentReviewStep,
    DocumentAudit, DocumentSubscription, DocumentComment,
)


# Reference Models
@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'prefix', 'review_interval_days', 'requires_approval', 'is_active']
    list_filter = ['requires_approval', 'is_active', 'parent']
    search_fields = ['code', 'name']


@admin.register(DocumentTag)
class DocumentTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'editor_type', 'is_active']
    list_filter = ['category', 'editor_type', 'is_active']
    search_fields = ['code', 'name']


# Folder
@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ['folder_id', 'name', 'parent', 'laboratory', 'document_count', 'is_private', 'is_active']
    list_filter = ['laboratory', 'is_private', 'is_active']
    search_fields = ['folder_id', 'name']
    readonly_fields = ['folder_id', 'created_at', 'updated_at']
    autocomplete_fields = ['parent', 'laboratory', 'owner']
    filter_horizontal = ['allowed_groups']


# Document
class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ['version_number', 'created_at', 'created_by', 'word_count']
    fields = ['version_number', 'is_major_version', 'change_summary', 'created_by', 'created_at']


class DocumentStatusInline(admin.TabularInline):
    model = DocumentStatus
    extra = 0
    readonly_fields = ['status', 'date', 'user', 'comment']
    fields = ['status', 'date', 'user', 'comment']
    ordering = ['-date']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_id', 'title', 'document_number', 'category', 'status_display', 'laboratory', 'updated_at']
    list_filter = ['category', 'laboratory', 'is_public', 'is_archived', 'is_active']
    search_fields = ['document_id', 'title', 'document_number']
    readonly_fields = ['document_id', 'created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    autocomplete_fields = ['folder', 'category', 'template', 'laboratory', 'created_by', 'archived_by']
    filter_horizontal = ['authors', 'readers', 'tags', 'related_documents']
    inlines = [DocumentVersionInline, DocumentStatusInline]

    fieldsets = (
        ('Identification', {
            'fields': ('document_id', 'document_number', 'title', 'description')
        }),
        ('Organization', {
            'fields': ('laboratory', 'folder', 'category', 'template', 'tags')
        }),
        ('Content', {
            'fields': ('editor_type', 'external_url')
        }),
        ('Authorship', {
            'fields': ('authors', 'created_by')
        }),
        ('Access', {
            'fields': ('is_public', 'readers')
        }),
        ('Review Schedule', {
            'fields': ('review_interval_days', 'next_review_date')
        }),
        ('Related', {
            'fields': ('related_documents',),
            'classes': ('collapse',)
        }),
        ('Archive', {
            'fields': ('is_archived', 'archived_date', 'archived_by'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def status_display(self, obj):
        status = obj.current_status
        colors = {
            'DRAFT': '#718096',
            'IN_REVIEW': '#d69e2e',
            'APPROVED': '#38a169',
            'PUBLISHED': '#276749',
            'REJECTED': '#c53030',
            'ARCHIVED': '#4a5568',
        }
        color = colors.get(status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_display.short_description = 'Status'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'is_major_version', 'word_count', 'created_by', 'created_at']
    list_filter = ['is_major_version', 'created_at']
    search_fields = ['document__title', 'document__document_number', 'version_number']
    readonly_fields = ['created_at', 'word_count', 'checksum']


# Workflow
class DocumentReviewStepInline(admin.TabularInline):
    model = DocumentReviewStep
    extra = 1
    autocomplete_fields = ['reviewer']


@admin.register(DocumentReviewCycle)
class DocumentReviewCycleAdmin(admin.ModelAdmin):
    list_display = ['document', 'version', 'status', 'initiated_by', 'initiated_at', 'due_date']
    list_filter = ['status', 'initiated_at']
    search_fields = ['document__title', 'document__document_number']
    readonly_fields = ['initiated_at', 'completed_at']
    autocomplete_fields = ['document', 'version', 'initiated_by']
    inlines = [DocumentReviewStepInline]


@admin.register(DocumentReviewStep)
class DocumentReviewStepAdmin(admin.ModelAdmin):
    list_display = ['review_cycle', 'reviewer', 'sequence', 'status', 'reviewed_at']
    list_filter = ['status', 'is_required']
    autocomplete_fields = ['review_cycle', 'reviewer']


# Audit
@admin.register(DocumentAudit)
class DocumentAuditAdmin(admin.ModelAdmin):
    list_display = ['document', 'action', 'user', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['document__title', 'user__username']
    readonly_fields = ['document', 'version', 'action', 'timestamp', 'user', 'ip_address', 'user_agent', 'details']
    date_hierarchy = 'timestamp'


@admin.register(DocumentSubscription)
class DocumentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'notify_on', 'is_active', 'created_at']
    list_filter = ['notify_on', 'is_active']
    autocomplete_fields = ['document', 'user']


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    list_display = ['document', 'author', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['document__title', 'author__username', 'content']
    autocomplete_fields = ['document', 'version', 'author', 'parent', 'resolved_by']

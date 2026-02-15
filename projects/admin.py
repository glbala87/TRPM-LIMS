# projects/admin.py

from django.contrib import admin
from .models import (
    ProjectCategory, Project, ProjectMember,
    ProjectSample, ProjectMilestone, ProjectDocument
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0
    fields = ['user', 'role', 'can_add_samples', 'can_edit_samples', 'can_view_results', 'is_active']


class ProjectSampleInline(admin.TabularInline):
    model = ProjectSample
    extra = 0
    fields = ['molecular_sample', 'external_sample_id', 'subject_id', 'consent_obtained']
    raw_id_fields = ['molecular_sample']


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0
    fields = ['name', 'target_date', 'status', 'order']


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0
    fields = ['title', 'document_type', 'file', 'version']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_id', 'name', 'category', 'status',
        'principal_investigator', 'sample_count', 'start_date', 'end_date'
    ]
    list_filter = ['status', 'category', 'consent_required']
    search_fields = ['project_id', 'name', 'short_name', 'principal_investigator__username']
    readonly_fields = ['project_id', 'created_at', 'sample_count', 'is_ethics_valid']
    inlines = [ProjectMemberInline, ProjectSampleInline, ProjectMilestoneInline, ProjectDocumentInline]

    fieldsets = (
        (None, {
            'fields': ('project_id', 'name', 'short_name', 'description', 'category', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at')
        }),
        ('People', {
            'fields': ('principal_investigator', 'created_by')
        }),
        ('Ethics & Compliance', {
            'fields': (
                'ethics_approval_number', 'ethics_approval_date', 'ethics_expiry_date',
                'ethics_document', 'is_ethics_valid', 'consent_required', 'consent_form'
            )
        }),
        ('Funding', {
            'fields': ('funding_source', 'grant_number', 'budget'),
            'classes': ('collapse',)
        }),
        ('Targets', {
            'fields': ('target_sample_count', 'target_participant_count', 'sample_count'),
            'classes': ('collapse',)
        }),
        ('Settings & Notes', {
            'fields': ('settings', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'can_add_samples', 'can_view_results', 'is_active']
    list_filter = ['role', 'is_active', 'project']
    search_fields = ['user__username', 'project__name', 'project__project_id']


@admin.register(ProjectSample)
class ProjectSampleAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'molecular_sample', 'external_sample_id',
        'subject_id', 'consent_obtained', 'added_at'
    ]
    list_filter = ['consent_obtained', 'project']
    search_fields = ['project__project_id', 'molecular_sample__sample_id', 'external_sample_id', 'subject_id']
    raw_id_fields = ['molecular_sample']
    readonly_fields = ['added_at']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'target_date', 'completed_date', 'status', 'order']
    list_filter = ['status', 'project']
    search_fields = ['name', 'project__name']
    ordering = ['project', 'order', 'target_date']


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'document_type', 'version', 'uploaded_at']
    list_filter = ['document_type', 'project']
    search_fields = ['title', 'project__name']
    readonly_fields = ['uploaded_at']

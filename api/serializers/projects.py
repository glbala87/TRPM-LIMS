"""
Serializers for projects app models.
"""
from rest_framework import serializers
from projects.models import (
    ProjectCategory, Project, ProjectMember,
    ProjectSample, ProjectMilestone, ProjectDocument
)


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Serializer for ProjectCategory model."""

    class Meta:
        model = ProjectCategory
        fields = ['id', 'code', 'name', 'description', 'is_active']


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMember model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            'id', 'project', 'user', 'user_name', 'role', 'role_display',
            'can_add_samples', 'can_edit_samples', 'can_view_results', 'can_manage_members',
            'joined_at', 'is_active'
        ]
        read_only_fields = ['id', 'joined_at']


class ProjectSampleSerializer(serializers.ModelSerializer):
    """Serializer for ProjectSample model."""
    molecular_sample_id = serializers.CharField(source='molecular_sample.sample_id', read_only=True)

    class Meta:
        model = ProjectSample
        fields = [
            'id', 'project', 'molecular_sample', 'molecular_sample_id',
            'external_sample_id', 'subject_id',
            'consent_obtained', 'consent_date', 'consent_version',
            'added_at', 'added_by', 'notes'
        ]
        read_only_fields = ['id', 'added_at']


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMilestone model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'project', 'name', 'description', 'target_date', 'completed_date',
            'status', 'status_display', 'order'
        ]


class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDocument model."""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'project', 'title', 'document_type', 'document_type_display',
            'file', 'version', 'description', 'uploaded_at', 'uploaded_by'
        ]
        read_only_fields = ['id', 'uploaded_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    pi_name = serializers.CharField(source='principal_investigator.get_full_name', read_only=True)
    sample_count = serializers.ReadOnlyField()
    is_ethics_valid = serializers.ReadOnlyField()
    members = ProjectMemberSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'name', 'short_name', 'description',
            'category', 'category_name', 'status', 'status_display',
            'start_date', 'end_date', 'principal_investigator', 'pi_name',
            'ethics_approval_number', 'ethics_approval_date', 'ethics_expiry_date',
            'ethics_document', 'is_ethics_valid', 'consent_required', 'consent_form',
            'funding_source', 'grant_number', 'budget',
            'target_sample_count', 'target_participant_count', 'sample_count',
            'settings', 'notes', 'members', 'milestones',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'project_id', 'sample_count', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Project list views."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    sample_count = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'name', 'category_name', 'status_display',
            'sample_count', 'start_date', 'end_date', 'created_at'
        ]

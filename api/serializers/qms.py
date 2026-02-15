# api/serializers/qms.py
"""
API Serializers for QMS (Quality Management System) module.
"""

from rest_framework import serializers
from qms.models import (
    DocumentCategory, DocumentTag, DocumentTemplate,
    DocumentFolder,
    Document, DocumentVersion,
    DocumentStatus, DocumentReviewCycle, DocumentReviewStep,
    DocumentAudit, DocumentSubscription, DocumentComment,
)


# Reference Serializers
class DocumentCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = DocumentCategory
        fields = '__all__'


class DocumentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTag
        fields = '__all__'


class DocumentTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Folder Serializers
class DocumentFolderSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    depth = serializers.IntegerField(read_only=True)
    document_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentFolder
        fields = '__all__'
        read_only_fields = ['folder_id', 'created_at', 'updated_at']


class DocumentFolderListSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    document_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentFolder
        fields = ['id', 'folder_id', 'name', 'full_path', 'parent', 'document_count', 'is_private', 'is_active']


class DocumentFolderTreeSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = ['id', 'folder_id', 'name', 'full_path', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return DocumentFolderTreeSerializer(children, many=True).data


# Version Serializers
class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ['created_at', 'word_count', 'checksum']


class DocumentVersionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = ['id', 'version_number', 'is_major_version', 'change_summary', 'created_by_name', 'created_at']


# Status Serializers
class DocumentStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = DocumentStatus
        fields = '__all__'


# Review Serializers
class DocumentReviewStepSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DocumentReviewStep
        fields = '__all__'


class DocumentReviewCycleSerializer(serializers.ModelSerializer):
    steps = DocumentReviewStepSerializer(many=True, read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    all_approved = serializers.BooleanField(read_only=True)
    has_rejection = serializers.BooleanField(read_only=True)

    class Meta:
        model = DocumentReviewCycle
        fields = '__all__'
        read_only_fields = ['initiated_at', 'completed_at']


class DocumentReviewCycleListSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentReviewCycle
        fields = ['id', 'document', 'document_title', 'version', 'status', 'initiated_by_name', 'initiated_at', 'due_date']


# Document Serializers
class DocumentSerializer(serializers.ModelSerializer):
    latest_version = DocumentVersionSerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    folder_path = serializers.CharField(source='folder.get_full_path', read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['document_id', 'created_at', 'updated_at']


class DocumentListSerializer(serializers.ModelSerializer):
    current_status = serializers.CharField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    latest_version_number = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'document_id', 'document_number', 'title', 'category', 'category_name',
                  'current_status', 'latest_version_number', 'updated_at', 'is_active']

    def get_latest_version_number(self, obj):
        latest = obj.latest_version
        return latest.version_number if latest else None


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['laboratory', 'folder', 'category', 'template', 'title',
                  'document_number', 'description', 'editor_type', 'is_public',
                  'review_interval_days', 'tags']


# Audit Serializers
class DocumentAuditSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = DocumentAudit
        fields = '__all__'


class DocumentSubscriptionSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentSubscription
        fields = '__all__'


class DocumentCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = DocumentComment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()
            return DocumentCommentSerializer(replies, many=True).data
        return []


# Request Serializers
class InitiateReviewSerializer(serializers.Serializer):
    version_id = serializers.IntegerField()
    reviewer_ids = serializers.ListField(child=serializers.IntegerField())
    due_date = serializers.DateField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)


class SubmitReviewSerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True)


class TransitionStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        'DRAFT', 'IN_REVIEW', 'APPROVED', 'PUBLISHED', 'ARCHIVED', 'WITHDRAWN'
    ])
    comment = serializers.CharField(required=False, allow_blank=True)
    effective_date = serializers.DateField(required=False)

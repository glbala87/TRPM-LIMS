# api/views/qms.py
"""
API Views for QMS (Quality Management System) module.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model

from qms.models import (
    DocumentCategory, DocumentTag, DocumentTemplate,
    DocumentFolder,
    Document, DocumentVersion,
    DocumentStatus, DocumentReviewCycle, DocumentReviewStep,
    DocumentAudit, DocumentSubscription, DocumentComment,
)
from qms.services import DocumentReviewWorkflow
from api.serializers import (
    DocumentCategorySerializer, DocumentTagSerializer, DocumentTemplateSerializer,
    DocumentFolderSerializer, DocumentFolderListSerializer, DocumentFolderTreeSerializer,
    DocumentVersionSerializer, DocumentVersionListSerializer,
    DocumentStatusSerializer, DocumentReviewCycleSerializer, DocumentReviewCycleListSerializer, DocumentReviewStepSerializer,
    DocumentSerializer, DocumentListSerializer, DocumentCreateSerializer,
    DocumentAuditSerializer, DocumentSubscriptionSerializer, DocumentCommentSerializer,
    InitiateReviewSerializer, SubmitReviewSerializer, TransitionStatusSerializer,
)
from api.pagination import StandardResultsSetPagination

User = get_user_model()


# Reference ViewSets
class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all().order_by('code')
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class DocumentTagViewSet(viewsets.ModelViewSet):
    queryset = DocumentTag.objects.all().order_by('name')
    serializer_class = DocumentTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().select_related('category').order_by('name')
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'editor_type', 'is_active']
    search_fields = ['code', 'name']


# Folder ViewSet
class DocumentFolderViewSet(viewsets.ModelViewSet):
    queryset = DocumentFolder.objects.all().select_related('parent', 'owner').order_by('sequence', 'name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'parent', 'is_private', 'is_active']
    search_fields = ['folder_id', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentFolderListSerializer
        if self.action == 'tree':
            return DocumentFolderTreeSerializer
        return DocumentFolderSerializer

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder tree structure."""
        laboratory_id = request.query_params.get('laboratory_id')
        if not laboratory_id:
            return Response({'error': 'laboratory_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        root_folders = DocumentFolder.objects.filter(
            laboratory_id=laboratory_id,
            parent__isnull=True,
            is_active=True
        ).order_by('sequence', 'name')

        serializer = DocumentFolderTreeSerializer(root_folders, many=True)
        return Response(serializer.data)


# Document ViewSet
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().select_related(
        'folder', 'category', 'template', 'created_by'
    ).prefetch_related('tags', 'authors').order_by('-updated_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['laboratory', 'folder', 'category', 'is_public', 'is_archived', 'is_active']
    search_fields = ['document_id', 'document_number', 'title']
    ordering_fields = ['title', 'document_number', 'updated_at', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.save(created_by=self.request.user)
        # Log audit
        DocumentAudit.objects.create(
            document=document,
            action='CREATED',
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a document."""
        document = self.get_object()
        versions = document.versions.all().order_by('-created_at')
        serializer = DocumentVersionListSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of a document."""
        document = self.get_object()
        serializer = DocumentVersionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        version = serializer.save(document=document, created_by=request.user)

        # Log audit
        DocumentAudit.objects.create(
            document=document,
            version=version,
            action='VERSION_CREATED',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response(DocumentVersionSerializer(version).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get status history of a document."""
        document = self.get_object()
        history = document.status_history.all().order_by('-date')
        serializer = DocumentStatusSerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def initiate_review(self, request, pk=None):
        """Initiate a review cycle for a document."""
        document = self.get_object()
        serializer = InitiateReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        version = DocumentVersion.objects.get(pk=data['version_id'])
        reviewers = User.objects.filter(pk__in=data['reviewer_ids'])

        workflow = DocumentReviewWorkflow(document)
        success, message, review_cycle = workflow.initiate_review(
            version=version,
            reviewers=list(reviewers),
            initiated_by=request.user,
            due_date=data.get('due_date'),
            comment=data.get('comment', ''),
        )

        if success:
            return Response({
                'success': True,
                'message': message,
                'review_cycle': DocumentReviewCycleSerializer(review_cycle).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition document to a new status."""
        document = self.get_object()
        serializer = TransitionStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        workflow = DocumentReviewWorkflow(document)
        success, message = workflow.transition_status(
            new_status=data['status'],
            user=request.user,
            comment=data.get('comment', ''),
            effective_date=data.get('effective_date'),
        )

        if success:
            document.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'document': DocumentSerializer(document, context={'request': request}).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an approved document."""
        document = self.get_object()
        workflow = DocumentReviewWorkflow(document)
        success, message = workflow.publish(user=request.user)

        if success:
            document.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'document': DocumentSerializer(document, context={'request': request}).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a document."""
        document = self.get_object()
        reason = request.data.get('reason', '')
        workflow = DocumentReviewWorkflow(document)
        success, message = workflow.archive(user=request.user, reason=reason)

        if success:
            document.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'document': DocumentSerializer(document, context={'request': request}).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Get audit trail for a document."""
        document = self.get_object()
        audit = document.audit_trail.all().order_by('-timestamp')[:100]
        serializer = DocumentAuditSerializer(audit, many=True)
        return Response(serializer.data)


# Review ViewSets
class DocumentReviewCycleViewSet(viewsets.ModelViewSet):
    queryset = DocumentReviewCycle.objects.all().select_related(
        'document', 'version', 'initiated_by'
    ).prefetch_related('steps').order_by('-initiated_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['document', 'status']
    search_fields = ['document__title', 'document__document_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentReviewCycleListSerializer
        return DocumentReviewCycleSerializer


class DocumentReviewStepViewSet(viewsets.ModelViewSet):
    queryset = DocumentReviewStep.objects.all().select_related(
        'review_cycle', 'reviewer'
    ).order_by('review_cycle', 'sequence')
    serializer_class = DocumentReviewStepSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_cycle', 'reviewer', 'status']

    @action(detail=True, methods=['post'])
    def submit_review(self, request, pk=None):
        """Submit review decision for a step."""
        step = self.get_object()
        serializer = SubmitReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if step.reviewer != request.user:
            return Response(
                {'error': 'Only the assigned reviewer can submit this review'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = serializer.validated_data
        workflow = DocumentReviewWorkflow(step.review_cycle.document)
        success, message = workflow.submit_review(
            review_step=step,
            approved=data['approved'],
            comment=data.get('comment', ''),
        )

        if success:
            step.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'step': DocumentReviewStepSerializer(step).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reviews for the current user."""
        workflow = DocumentReviewWorkflow.__class__
        pending_steps = DocumentReviewStep.objects.filter(
            reviewer=request.user,
            status='PENDING',
            review_cycle__status='IN_PROGRESS'
        ).select_related('review_cycle__document', 'review_cycle__version')

        serializer = DocumentReviewStepSerializer(pending_steps, many=True)
        return Response(serializer.data)


# Subscription ViewSet
class DocumentSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = DocumentSubscription.objects.all().select_related('document', 'user')
    serializer_class = DocumentSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'user', 'notify_on', 'is_active']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# Comment ViewSet
class DocumentCommentViewSet(viewsets.ModelViewSet):
    queryset = DocumentComment.objects.all().select_related(
        'document', 'version', 'author', 'parent'
    ).order_by('created_at')
    serializer_class = DocumentCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'version', 'is_resolved']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a comment as resolved."""
        from django.utils import timezone
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response(DocumentCommentSerializer(comment).data)

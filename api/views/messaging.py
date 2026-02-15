# api/views/messaging.py
"""
API Views for messaging module.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.contrib.auth import get_user_model

from messaging.models import (
    MessageThread, Message, MessageAttachment,
    ActivityFeed, ActivityStream,
    Notification, Notice,
)
from messaging.services import NotificationService, ActivityService
from api.serializers import (
    MessageThreadSerializer, MessageThreadListSerializer, MessageThreadCreateSerializer,
    MessageSerializer, MessageListSerializer, MessageAttachmentSerializer, ReplyMessageSerializer,
    ActivityFeedSerializer, ActivityStreamSerializer, ActivityStreamListSerializer,
    NotificationSerializer, NotificationListSerializer, NotificationCreateSerializer,
    NoticeSerializer, NoticeListSerializer,
)
from api.pagination import StandardResultsSetPagination

User = get_user_model()


# Message ViewSets
class MessageThreadViewSet(viewsets.ModelViewSet):
    queryset = MessageThread.objects.all().select_related(
        'creator', 'laboratory'
    ).prefetch_related('recipients', 'messages').order_by('-updated_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'is_broadcast', 'is_urgent']
    search_fields = ['thread_id', 'subject']

    def get_queryset(self):
        # Filter to threads user is involved in
        user = self.request.user
        return self.queryset.filter(
            Q(creator=user) | Q(recipients=user)
        ).exclude(deleted_by=user).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return MessageThreadListSerializer
        if self.action == 'create':
            return MessageThreadCreateSerializer
        return MessageThreadSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        initial_message = data.pop('initial_message')
        recipient_ids = data.pop('recipient_ids')

        # Create thread
        thread = MessageThread.objects.create(
            creator=self.request.user,
            **data
        )
        thread.recipients.add(*User.objects.filter(pk__in=recipient_ids))

        # Create initial message
        Message.objects.create(
            thread=thread,
            sender=self.request.user,
            body=initial_message,
        )

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a thread."""
        thread = self.get_object()
        serializer = ReplyMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        parent = None
        if data.get('parent_id'):
            parent = Message.objects.get(pk=data['parent_id'], thread=thread)

        message = Message.objects.create(
            thread=thread,
            sender=request.user,
            body=data['body'],
            parent=parent,
        )

        return Response(MessageSerializer(message, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in thread as read."""
        thread = self.get_object()
        thread.mark_as_read(request.user)
        return Response({'success': True, 'message': 'Thread marked as read'})

    @action(detail=True, methods=['delete'])
    def delete_for_me(self, request, pk=None):
        """Delete thread for current user only."""
        thread = self.get_object()
        thread.deleted_by.add(request.user)
        return Response({'success': True, 'message': 'Thread deleted'})


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related(
        'thread', 'sender', 'parent'
    ).prefetch_related('attachments').order_by('created_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['thread', 'sender']

    def get_serializer_class(self):
        if self.action == 'list':
            return MessageListSerializer
        return MessageSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark message as read."""
        message = self.get_object()
        message.viewers.add(request.user)
        return Response({'success': True})


# Activity ViewSets
class ActivityFeedViewSet(viewsets.ModelViewSet):
    queryset = ActivityFeed.objects.all().order_by('name')
    serializer_class = ActivityFeedSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'feed_type', 'is_active']
    search_fields = ['name', 'slug']

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Subscribe current user to feed."""
        feed = self.get_object()
        feed.subscribers.add(request.user)
        return Response({'success': True, 'message': 'Subscribed to feed'})

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        """Unsubscribe current user from feed."""
        feed = self.get_object()
        feed.subscribers.remove(request.user)
        return Response({'success': True, 'message': 'Unsubscribed from feed'})

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        """Get feeds current user is subscribed to."""
        feeds = request.user.subscribed_feeds.filter(is_active=True)
        serializer = ActivityFeedSerializer(feeds, many=True)
        return Response(serializer.data)


class ActivityStreamViewSet(viewsets.ModelViewSet):
    queryset = ActivityStream.objects.all().select_related(
        'actor', 'action_object_content_type', 'target_content_type'
    ).prefetch_related('feeds').order_by('-timestamp')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['actor', 'verb', 'is_public']
    search_fields = ['action_object_repr', 'description']

    def get_serializer_class(self):
        if self.action == 'list':
            return ActivityStreamListSerializer
        return ActivityStreamSerializer

    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        """Get activity feed for current user."""
        limit = int(request.query_params.get('limit', 50))
        since = request.query_params.get('since')

        activities = ActivityService.get_user_feed(
            user=request.user,
            limit=limit,
            since=since,
        )

        serializer = ActivityStreamListSerializer(activities, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread activities for current user."""
        activities = ActivityService.get_unread_activities(user=request.user)
        serializer = ActivityStreamListSerializer(activities, many=True, context={'request': request})
        return Response({
            'count': activities.count(),
            'activities': serializer.data,
        })

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark activity as viewed."""
        activity = self.get_object()
        ActivityService.mark_as_viewed(activity, request.user)
        return Response({'success': True})


# Notification ViewSets
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().select_related(
        'sender', 'laboratory'
    ).order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'notification_type', 'priority', 'is_global']
    search_fields = ['notification_id', 'title', 'message']

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def get_queryset(self):
        # Get notifications for current user
        return NotificationService.get_user_notifications(
            user=self.request.user,
            include_dismissed=self.request.query_params.get('include_dismissed') == 'true'
        )

    def perform_create(self, serializer):
        data = serializer.validated_data
        user_ids = data.pop('user_ids', [])
        group_ids = data.pop('group_ids', [])

        users = User.objects.filter(pk__in=user_ids) if user_ids else None

        notification = NotificationService.create(
            sender=self.request.user,
            users=list(users) if users else None,
            **data
        )

        if group_ids:
            notification.groups.add(*group_ids)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        notifications = NotificationService.get_user_notifications(
            user=request.user,
            unread_only=True,
            limit=20,
        )
        serializer = NotificationListSerializer(notifications, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = NotificationService.get_unread_count(user=request.user)
        return Response({'count': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        NotificationService.mark_as_read(notification, request.user)
        return Response({'success': True})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = NotificationService.mark_all_as_read(user=request.user)
        return Response({'success': True, 'count': count})

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss notification."""
        notification = self.get_object()
        NotificationService.dismiss(notification, request.user)
        return Response({'success': True})


# Notice ViewSet
class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().select_related('author', 'laboratory').order_by('-is_pinned', '-publish_date')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'audience', 'is_pinned', 'style', 'is_active']
    search_fields = ['notice_id', 'title', 'body']

    def get_serializer_class(self):
        if self.action == 'list':
            return NoticeListSerializer
        return NoticeSerializer

    def get_queryset(self):
        # Filter to published notices visible to user
        from django.utils import timezone
        now = timezone.now()

        qs = self.queryset.filter(
            is_active=True,
            publish_date__lte=now,
        ).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gte=now)
        )

        # Filter by audience
        user = self.request.user
        user_groups = user.groups.all()

        return qs.filter(
            Q(audience='ALL') |
            Q(audience='LAB') |
            Q(audience_groups__in=user_groups)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned notices."""
        notices = self.get_queryset().filter(is_pinned=True)
        serializer = NoticeListSerializer(notices, many=True)
        return Response(serializer.data)

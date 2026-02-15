# api/serializers/messaging.py
"""
API Serializers for messaging module.
"""

from rest_framework import serializers
from messaging.models import (
    MessageThread, Message, MessageAttachment,
    ActivityFeed, ActivityStream,
    Notification, Notice,
)


# Thread Serializers
class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'filename', 'file', 'file_type', 'file_size', 'uploaded_at']
        read_only_fields = ['file_type', 'file_size', 'uploaded_at']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['message_id', 'created_at', 'edited_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.viewers.filter(id=request.user.id).exists()
        return False


class MessageListSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'message_id', 'sender', 'sender_name', 'body', 'created_at', 'has_attachments']


class MessageThreadSerializer(serializers.ModelSerializer):
    messages = MessageListSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    last_message = MessageListSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = '__all__'
        read_only_fields = ['thread_id', 'created_at', 'updated_at']

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0


class MessageThreadListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ['id', 'thread_id', 'subject', 'creator', 'creator_name', 'is_broadcast',
                  'is_urgent', 'message_count', 'last_message_preview', 'unread_count', 'updated_at']

    def get_last_message_preview(self, obj):
        last = obj.last_message
        if last:
            return last.body[:100] + '...' if len(last.body) > 100 else last.body
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0


class MessageThreadCreateSerializer(serializers.ModelSerializer):
    initial_message = serializers.CharField(write_only=True)
    recipient_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = MessageThread
        fields = ['laboratory', 'subject', 'is_broadcast', 'is_urgent', 'initial_message', 'recipient_ids']


class ReplyMessageSerializer(serializers.Serializer):
    body = serializers.CharField()
    parent_id = serializers.IntegerField(required=False)


# Activity Serializers
class ActivityFeedSerializer(serializers.ModelSerializer):
    subscriber_count = serializers.SerializerMethodField()

    class Meta:
        model = ActivityFeed
        fields = '__all__'

    def get_subscriber_count(self, obj):
        return obj.subscribers.count()


class ActivityStreamSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    sentence = serializers.CharField(read_only=True)
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = ActivityStream
        fields = '__all__'
        read_only_fields = ['activity_id', 'timestamp']

    def get_is_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.viewers.filter(id=request.user.id).exists()
        return False


class ActivityStreamListSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    sentence = serializers.CharField(read_only=True)

    class Meta:
        model = ActivityStream
        fields = ['id', 'activity_id', 'actor', 'actor_name', 'verb', 'sentence',
                  'action_object_repr', 'target_repr', 'timestamp']


# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    is_read = serializers.SerializerMethodField()
    is_dismissed = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['notification_id', 'sent_at', 'created_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.read_by.filter(id=request.user.id).exists()
        return False

    def get_is_dismissed(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.dismissed_by.filter(id=request.user.id).exists()
        return False


class NotificationListSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_id', 'title', 'message', 'notification_type', 'type_display',
                  'priority', 'priority_display', 'action_url', 'is_read', 'created_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.read_by.filter(id=request.user.id).exists()
        return False


class NotificationCreateSerializer(serializers.ModelSerializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    group_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'priority', 'laboratory',
                  'action_url', 'send_email', 'expires_at', 'user_ids', 'group_ids', 'departments']


# Notice Serializers
class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['notice_id', 'created_at', 'updated_at']


class NoticeListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notice
        fields = ['id', 'notice_id', 'title', 'author', 'author_name', 'audience',
                  'is_pinned', 'style', 'publish_date', 'expiry_date', 'is_published']

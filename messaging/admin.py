# messaging/admin.py
"""
Django admin configuration for messaging module.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    MessageThread, Message, MessageAttachment,
    ActivityFeed, ActivityStream,
    Notification, Notice,
)


# Message Thread
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['message_id', 'sender', 'body', 'created_at']
    fields = ['message_id', 'sender', 'body', 'created_at']


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['thread_id', 'subject', 'creator', 'message_count', 'is_broadcast', 'is_urgent', 'updated_at']
    list_filter = ['is_broadcast', 'is_urgent', 'laboratory', 'created_at']
    search_fields = ['thread_id', 'subject', 'creator__username']
    readonly_fields = ['thread_id', 'created_at', 'updated_at']
    filter_horizontal = ['recipients', 'deleted_by']
    inlines = [MessageInline]


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0
    readonly_fields = ['filename', 'file_type', 'file_size', 'uploaded_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'thread', 'sender', 'body_preview', 'is_system_message', 'created_at']
    list_filter = ['is_system_message', 'created_at']
    search_fields = ['message_id', 'body', 'sender__username']
    readonly_fields = ['message_id', 'created_at', 'edited_at']
    filter_horizontal = ['viewers', 'deleted_by']
    inlines = [MessageAttachmentInline]

    def body_preview(self, obj):
        return obj.body[:100] + '...' if len(obj.body) > 100 else obj.body
    body_preview.short_description = 'Body'


# Activity
@admin.register(ActivityFeed)
class ActivityFeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'feed_type', 'laboratory', 'subscriber_count', 'is_active']
    list_filter = ['feed_type', 'laboratory', 'is_active']
    search_fields = ['name', 'slug']
    filter_horizontal = ['subscribers']
    prepopulated_fields = {'slug': ('name',)}

    def subscriber_count(self, obj):
        return obj.subscribers.count()
    subscriber_count.short_description = 'Subscribers'


@admin.register(ActivityStream)
class ActivityStreamAdmin(admin.ModelAdmin):
    list_display = ['activity_id', 'actor', 'verb', 'action_object_repr', 'target_repr', 'timestamp']
    list_filter = ['verb', 'timestamp']
    search_fields = ['activity_id', 'actor__username', 'action_object_repr', 'description']
    readonly_fields = ['activity_id', 'timestamp']
    filter_horizontal = ['feeds', 'viewers']
    date_hierarchy = 'timestamp'


# Notifications
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'title', 'notification_type_display', 'priority_display', 'sender', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_global', 'send_email', 'laboratory']
    search_fields = ['notification_id', 'title', 'message']
    readonly_fields = ['notification_id', 'sent_at', 'created_at']
    filter_horizontal = ['users', 'groups', 'read_by', 'dismissed_by']
    date_hierarchy = 'created_at'

    def notification_type_display(self, obj):
        colors = {
            'INFO': '#3182ce',
            'SUCCESS': '#38a169',
            'WARNING': '#d69e2e',
            'ERROR': '#c53030',
            'ACTION': '#805ad5',
        }
        color = colors.get(obj.notification_type, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_notification_type_display()
        )
    notification_type_display.short_description = 'Type'

    def priority_display(self, obj):
        colors = {
            'LOW': '#718096',
            'NORMAL': '#3182ce',
            'HIGH': '#d69e2e',
            'URGENT': '#c53030',
        }
        color = colors.get(obj.priority, '#000')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['notice_id', 'title', 'author', 'audience', 'is_pinned', 'publish_date', 'is_published']
    list_filter = ['audience', 'is_pinned', 'style', 'is_active', 'laboratory']
    search_fields = ['notice_id', 'title', 'body']
    readonly_fields = ['notice_id', 'created_at', 'updated_at']
    filter_horizontal = ['audience_groups']
    date_hierarchy = 'publish_date'

    def is_published(self, obj):
        if obj.is_published:
            return format_html('<span style="color: #38a169;">Published</span>')
        return format_html('<span style="color: #718096;">Not Published</span>')
    is_published.short_description = 'Status'

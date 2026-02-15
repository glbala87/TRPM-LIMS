# messaging/services/notification_service.py
"""
Notification service for creating and managing notifications.
"""

from typing import List, Optional, Union
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ..models import Notification

User = get_user_model()


class NotificationService:
    """
    Service for creating and managing notifications.
    """

    @classmethod
    def create(
        cls,
        title: str,
        message: str,
        users: Optional[List] = None,
        groups: Optional[List] = None,
        departments: Optional[List[str]] = None,
        notification_type: str = 'INFO',
        priority: str = 'NORMAL',
        sender: Optional[User] = None,
        laboratory_id: Optional[int] = None,
        linked_object: Optional[object] = None,
        action_url: str = '',
        send_email: bool = False,
        expires_at: Optional[timezone.datetime] = None,
    ) -> Notification:
        """
        Create a notification.

        Args:
            title: Notification title
            message: Notification message
            users: List of users to notify
            groups: List of groups to notify
            departments: List of department names to notify
            notification_type: Type of notification
            priority: Priority level
            sender: User sending the notification
            laboratory_id: Laboratory scope
            linked_object: Related object
            action_url: URL for action button
            send_email: Whether to send email notification
            expires_at: When the notification expires

        Returns:
            Created Notification instance
        """
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            sender=sender,
            laboratory_id=laboratory_id,
            action_url=action_url,
            send_email=send_email,
            expires_at=expires_at,
            sent_at=timezone.now(),
            departments=departments or [],
        )

        # Set linked object
        if linked_object:
            content_type = ContentType.objects.get_for_model(linked_object)
            notification.linked_content_type = content_type
            notification.linked_object_id = linked_object.pk
            notification.save()

        # Add targets
        if users:
            notification.users.add(*users)
        if groups:
            notification.groups.add(*groups)

        return notification

    @classmethod
    def broadcast(
        cls,
        title: str,
        message: str,
        laboratory_id: int,
        notification_type: str = 'INFO',
        priority: str = 'NORMAL',
        sender: Optional[User] = None,
        **kwargs
    ) -> Notification:
        """
        Broadcast notification to all users in a laboratory.

        Args:
            title: Notification title
            message: Notification message
            laboratory_id: Laboratory to broadcast to
            notification_type: Type of notification
            priority: Priority level
            sender: User sending the notification
            **kwargs: Additional notification parameters

        Returns:
            Created Notification instance
        """
        notification = cls.create(
            title=title,
            message=message,
            laboratory_id=laboratory_id,
            notification_type=notification_type,
            priority=priority,
            sender=sender,
            **kwargs
        )
        notification.is_global = True
        notification.save()

        return notification

    @classmethod
    def notify_user(
        cls,
        user: User,
        title: str,
        message: str,
        **kwargs
    ) -> Notification:
        """
        Send notification to a single user.

        Args:
            user: User to notify
            title: Notification title
            message: Notification message
            **kwargs: Additional notification parameters

        Returns:
            Created Notification instance
        """
        return cls.create(
            title=title,
            message=message,
            users=[user],
            **kwargs
        )

    @classmethod
    def get_user_notifications(
        cls,
        user: User,
        unread_only: bool = False,
        include_dismissed: bool = False,
        limit: Optional[int] = None,
    ):
        """
        Get notifications for a user.

        Args:
            user: User to get notifications for
            unread_only: Only return unread notifications
            include_dismissed: Include dismissed notifications
            limit: Maximum number of notifications to return

        Returns:
            QuerySet of notifications
        """
        # Get user's groups
        user_groups = user.groups.all()

        # Build query
        query = Q(users=user) | Q(groups__in=user_groups) | Q(is_global=True)

        notifications = Notification.objects.filter(query).distinct()

        # Filter out expired
        notifications = notifications.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

        if unread_only:
            notifications = notifications.exclude(read_by=user)

        if not include_dismissed:
            notifications = notifications.exclude(dismissed_by=user)

        notifications = notifications.order_by('-priority', '-created_at')

        if limit:
            notifications = notifications[:limit]

        return notifications

    @classmethod
    def mark_as_read(cls, notification: Notification, user: User) -> None:
        """Mark notification as read by user."""
        notification.mark_as_read(user)

    @classmethod
    def mark_all_as_read(cls, user: User, laboratory_id: Optional[int] = None) -> int:
        """
        Mark all notifications as read for a user.

        Returns:
            Count of notifications marked as read
        """
        notifications = cls.get_user_notifications(user, unread_only=True)

        if laboratory_id:
            notifications = notifications.filter(
                Q(laboratory_id=laboratory_id) | Q(is_global=True)
            )

        count = 0
        for notification in notifications:
            notification.mark_as_read(user)
            count += 1

        return count

    @classmethod
    def dismiss(cls, notification: Notification, user: User) -> None:
        """Dismiss notification for user."""
        notification.dismiss(user)

    @classmethod
    def get_unread_count(cls, user: User, laboratory_id: Optional[int] = None) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            user: User to count for
            laboratory_id: Optional laboratory filter

        Returns:
            Count of unread notifications
        """
        notifications = cls.get_user_notifications(user, unread_only=True)

        if laboratory_id:
            notifications = notifications.filter(
                Q(laboratory_id=laboratory_id) | Q(is_global=True)
            )

        return notifications.count()

# messaging/services/activity_service.py
"""
Activity stream service for logging and retrieving activities.
"""

from typing import List, Optional, Any
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ..models import ActivityStream, ActivityFeed

User = get_user_model()


class ActivityService:
    """
    Service for logging and retrieving activity streams.
    """

    @classmethod
    def log_activity(
        cls,
        actor: User,
        verb: str,
        action_object: Any,
        target: Optional[Any] = None,
        description: str = '',
        extra_data: Optional[dict] = None,
        feeds: Optional[List[ActivityFeed]] = None,
        feed_slugs: Optional[List[str]] = None,
        is_public: bool = True,
    ) -> ActivityStream:
        """
        Log an activity to the stream.

        Args:
            actor: User performing the action
            verb: Action verb (e.g., 'created', 'updated')
            action_object: Primary object of the action
            target: Optional secondary object
            description: Additional description
            extra_data: Extra JSON data
            feeds: List of feeds to add activity to
            feed_slugs: List of feed slugs to add activity to
            is_public: Whether activity is public

        Returns:
            Created ActivityStream instance
        """
        # Get content types
        action_ct = ContentType.objects.get_for_model(action_object)

        activity = ActivityStream.objects.create(
            actor=actor,
            verb=verb,
            action_object_content_type=action_ct,
            action_object_id=action_object.pk,
            action_object_repr=str(action_object)[:255],
            description=description,
            extra_data=extra_data or {},
            is_public=is_public,
        )

        # Set target if provided
        if target:
            target_ct = ContentType.objects.get_for_model(target)
            activity.target_content_type = target_ct
            activity.target_id = target.pk
            activity.target_repr = str(target)[:255]
            activity.save()

        # Add to feeds
        if feeds:
            activity.feeds.add(*feeds)

        if feed_slugs:
            existing_feeds = ActivityFeed.objects.filter(slug__in=feed_slugs)
            activity.feeds.add(*existing_feeds)

        return activity

    @classmethod
    def log_create(
        cls,
        actor: User,
        obj: Any,
        **kwargs
    ) -> ActivityStream:
        """Log a create action."""
        return cls.log_activity(
            actor=actor,
            verb='created',
            action_object=obj,
            **kwargs
        )

    @classmethod
    def log_update(
        cls,
        actor: User,
        obj: Any,
        changes: Optional[dict] = None,
        **kwargs
    ) -> ActivityStream:
        """Log an update action."""
        extra_data = kwargs.pop('extra_data', {})
        if changes:
            extra_data['changes'] = changes

        return cls.log_activity(
            actor=actor,
            verb='updated',
            action_object=obj,
            extra_data=extra_data,
            **kwargs
        )

    @classmethod
    def log_delete(
        cls,
        actor: User,
        obj: Any,
        **kwargs
    ) -> ActivityStream:
        """Log a delete action."""
        return cls.log_activity(
            actor=actor,
            verb='deleted',
            action_object=obj,
            **kwargs
        )

    @classmethod
    def log_transition(
        cls,
        actor: User,
        obj: Any,
        from_status: str,
        to_status: str,
        **kwargs
    ) -> ActivityStream:
        """Log a status transition."""
        extra_data = kwargs.pop('extra_data', {})
        extra_data['from_status'] = from_status
        extra_data['to_status'] = to_status

        return cls.log_activity(
            actor=actor,
            verb='transitioned',
            action_object=obj,
            extra_data=extra_data,
            description=f"Status changed from {from_status} to {to_status}",
            **kwargs
        )

    @classmethod
    def get_user_feed(
        cls,
        user: User,
        feed_slugs: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        since: Optional[timezone.datetime] = None,
    ):
        """
        Get activity feed for a user.

        Args:
            user: User to get feed for
            feed_slugs: Filter to specific feeds
            limit: Maximum activities to return
            offset: Pagination offset
            since: Only activities after this time

        Returns:
            QuerySet of activities
        """
        # Get feeds user is subscribed to
        subscribed_feeds = user.subscribed_feeds.filter(is_active=True)

        # Build query
        query = Q(feeds__in=subscribed_feeds) | Q(actor=user)

        if feed_slugs:
            query = Q(feeds__slug__in=feed_slugs)

        activities = ActivityStream.objects.filter(query).filter(is_public=True)

        if since:
            activities = activities.filter(timestamp__gt=since)

        return activities.distinct().order_by('-timestamp')[offset:offset + limit]

    @classmethod
    def get_object_activities(
        cls,
        obj: Any,
        limit: int = 50,
    ):
        """
        Get activities for a specific object.

        Args:
            obj: Object to get activities for
            limit: Maximum activities to return

        Returns:
            QuerySet of activities
        """
        content_type = ContentType.objects.get_for_model(obj)

        return ActivityStream.objects.filter(
            Q(action_object_content_type=content_type, action_object_id=obj.pk) |
            Q(target_content_type=content_type, target_id=obj.pk)
        ).order_by('-timestamp')[:limit]

    @classmethod
    def get_actor_activities(
        cls,
        actor: User,
        limit: int = 50,
    ):
        """
        Get activities performed by a specific user.

        Args:
            actor: User to get activities for
            limit: Maximum activities to return

        Returns:
            QuerySet of activities
        """
        return ActivityStream.objects.filter(
            actor=actor
        ).order_by('-timestamp')[:limit]

    @classmethod
    def mark_as_viewed(
        cls,
        activity: ActivityStream,
        user: User,
    ) -> None:
        """Mark activity as viewed by user."""
        activity.viewers.add(user)

    @classmethod
    def get_unread_activities(
        cls,
        user: User,
        feed_slugs: Optional[List[str]] = None,
    ):
        """
        Get unread activities for a user.

        Args:
            user: User to check
            feed_slugs: Optional filter to specific feeds

        Returns:
            QuerySet of unread activities
        """
        subscribed_feeds = user.subscribed_feeds.filter(is_active=True)

        query = Q(feeds__in=subscribed_feeds)

        if feed_slugs:
            query = Q(feeds__slug__in=feed_slugs)

        return ActivityStream.objects.filter(query).filter(
            is_public=True
        ).exclude(
            viewers=user
        ).exclude(
            actor=user  # Don't count own activities
        ).distinct().order_by('-timestamp')

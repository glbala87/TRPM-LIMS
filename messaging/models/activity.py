# messaging/models/activity.py
"""
Activity feed and stream models using Actor-Verb-Object pattern.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import uuid


class ActivityFeed(models.Model):
    """
    Named activity feed for organizing activity streams.
    Users can subscribe to feeds to receive relevant activities.
    """
    FEED_TYPE_CHOICES = [
        ('SYSTEM', 'System'),
        ('SAMPLES', 'Samples'),
        ('RESULTS', 'Results'),
        ('QC', 'Quality Control'),
        ('EQUIPMENT', 'Equipment'),
        ('DOCUMENTS', 'Documents'),
        ('ORDERS', 'Orders'),
        ('INVENTORY', 'Inventory'),
        ('COMPLIANCE', 'Compliance'),
        ('CUSTOM', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    feed_type = models.CharField(max_length=20, choices=FEED_TYPE_CHOICES, default='CUSTOM')
    description = models.TextField(blank=True)

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='activity_feeds',
        null=True,
        blank=True,
        help_text="Lab-specific feed, or null for global"
    )

    # Subscribers
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='subscribed_feeds',
        blank=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Feed"
        verbose_name_plural = "Activity Feeds"
        ordering = ['name']

    def __str__(self):
        return self.name


class ActivityStream(models.Model):
    """
    Activity stream entry following Actor-Verb-Object pattern.
    Records actions performed by users on various objects.
    """
    VERB_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('transitioned', 'Transitioned'),
        ('assigned', 'Assigned'),
        ('commented', 'Commented'),
        ('uploaded', 'Uploaded'),
        ('downloaded', 'Downloaded'),
        ('shared', 'Shared'),
        ('started', 'Started'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
        ('received', 'Received'),
        ('released', 'Released'),
        ('flagged', 'Flagged'),
    ]

    activity_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique activity identifier"
    )

    # Actor (who performed the action)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )

    # Verb (what action was performed)
    verb = models.CharField(max_length=50, choices=VERB_CHOICES)

    # Action object (the primary object the action was performed on)
    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='action_object_activities'
    )
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_id')
    action_object_repr = models.CharField(max_length=255, blank=True, help_text="String representation of action object")

    # Target (optional secondary object)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='target_activities'
    )
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_id')
    target_repr = models.CharField(max_length=255, blank=True, help_text="String representation of target")

    # Additional context
    description = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    # Feeds this activity belongs to
    feeds = models.ManyToManyField(ActivityFeed, related_name='activities', blank=True)

    # Read tracking
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='viewed_activities',
        blank=True
    )

    # Privacy
    is_public = models.BooleanField(default=True)

    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Activity Stream"
        verbose_name_plural = "Activity Streams"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['actor', '-timestamp']),
            models.Index(fields=['verb', '-timestamp']),
            models.Index(fields=['action_object_content_type', 'action_object_id']),
        ]

    def save(self, *args, **kwargs):
        if not self.activity_id:
            self.activity_id = self._generate_activity_id()

        # Store string representations
        if self.action_object and not self.action_object_repr:
            self.action_object_repr = str(self.action_object)[:255]
        if self.target and not self.target_repr:
            self.target_repr = str(self.target)[:255]

        super().save(*args, **kwargs)

    def _generate_activity_id(self):
        """Generate unique activity ID with format: ACT-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"ACT-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.actor} {self.verb} {self.action_object_repr}"

    @property
    def sentence(self):
        """Generate human-readable sentence for the activity."""
        actor_name = self.actor.get_full_name() if self.actor else "System"
        verb = self.get_verb_display().lower()

        if self.target_repr:
            return f"{actor_name} {verb} {self.action_object_repr} on {self.target_repr}"
        return f"{actor_name} {verb} {self.action_object_repr}"

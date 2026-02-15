# messaging/models/threads.py
"""
Message thread and message models for internal communication.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class MessageThread(models.Model):
    """
    Conversation thread between users.
    """
    thread_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique thread identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='message_threads'
    )

    subject = models.CharField(max_length=255)

    # Participants
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_threads'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_threads'
    )

    # Thread type
    is_broadcast = models.BooleanField(default=False, help_text="Announcement to all recipients")
    is_urgent = models.BooleanField(default=False)

    # Related object (generic relation)
    related_content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_object_id = models.PositiveIntegerField(null=True, blank=True)

    # Soft delete tracking
    deleted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='deleted_threads',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Message Thread"
        verbose_name_plural = "Message Threads"
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        if not self.thread_id:
            self.thread_id = self._generate_thread_id()
        super().save(*args, **kwargs)

    def _generate_thread_id(self):
        """Generate unique thread ID with format: THR-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"THR-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.thread_id}: {self.subject}"

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    @property
    def participant_count(self):
        return self.recipients.count() + (1 if self.creator else 0)

    def get_unread_count(self, user):
        """Get count of unread messages for a user."""
        return self.messages.exclude(viewers=user).count()

    def mark_as_read(self, user):
        """Mark all messages in thread as read for user."""
        for message in self.messages.exclude(viewers=user):
            message.viewers.add(user)


class Message(models.Model):
    """
    Individual message within a thread.
    """
    message_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique message identifier"
    )

    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    # Sender
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages'
    )

    # Reply tracking
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Content
    body = models.TextField()
    is_system_message = models.BooleanField(default=False)

    # Attachments
    has_attachments = models.BooleanField(default=False)

    # Read tracking
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='viewed_messages',
        blank=True
    )

    # Soft delete tracking
    deleted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='deleted_messages',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = self._generate_message_id()
        super().save(*args, **kwargs)

        # Update thread timestamp
        if self.thread:
            self.thread.updated_at = timezone.now()
            self.thread.save(update_fields=['updated_at'])

    def _generate_message_id(self):
        """Generate unique message ID with format: MSG-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"MSG-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.message_id}: {self.body[:50]}..."

    @property
    def is_read_by_all(self):
        """Check if all recipients have read this message."""
        recipient_ids = set(self.thread.recipients.values_list('id', flat=True))
        viewer_ids = set(self.viewers.values_list('id', flat=True))
        return recipient_ids.issubset(viewer_ids)


class MessageAttachment(models.Model):
    """
    File attachment for a message.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='messaging/attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message Attachment"
        verbose_name_plural = "Message Attachments"

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = self.filename or self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)

        # Update message attachment flag
        if self.message and not self.message.has_attachments:
            self.message.has_attachments = True
            self.message.save(update_fields=['has_attachments'])

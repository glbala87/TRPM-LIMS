# transfers/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


class Transfer(models.Model):
    """
    Represents a sample transfer between locations/facilities.

    Tracks the movement of samples from one location to another,
    including shipping details and conditions.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    SHIPMENT_CONDITION_CHOICES = [
        ('AMBIENT', 'Ambient Temperature'),
        ('REFRIGERATED', 'Refrigerated (2-8C)'),
        ('FROZEN_MINUS20', 'Frozen (-20C)'),
        ('FROZEN_MINUS80', 'Frozen (-80C)'),
        ('DRY_ICE', 'Dry Ice'),
        ('LIQUID_NITROGEN', 'Liquid Nitrogen'),
    ]

    # Transfer identification
    transfer_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique transfer identifier"
    )

    # Location information
    source_location = models.CharField(
        max_length=200,
        help_text="Origin facility/location"
    )
    destination_location = models.CharField(
        max_length=200,
        help_text="Destination facility/location"
    )

    # Transfer dates
    transfer_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the transfer was initiated"
    )
    expected_arrival_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expected arrival date at destination"
    )
    actual_arrival_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual arrival date at destination"
    )

    # Shipping information
    courier = models.CharField(
        max_length=100,
        blank=True,
        help_text="Courier/shipping company name"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shipping tracking number"
    )

    # Shipment conditions
    shipment_conditions = models.CharField(
        max_length=20,
        choices=SHIPMENT_CONDITION_CHOICES,
        default='AMBIENT',
        help_text="Temperature/storage conditions during transport"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Personnel
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_transfers',
        help_text="User who initiated the transfer"
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_transfers',
        help_text="User who received the transfer"
    )

    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the transfer"
    )
    special_instructions = models.TextField(
        blank=True,
        help_text="Special handling instructions"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"
        ordering = ['-transfer_date']

    def __str__(self):
        return f"{self.transfer_number}: {self.source_location} -> {self.destination_location}"

    def save(self, *args, **kwargs):
        # Auto-generate transfer number if not provided
        if not self.transfer_number:
            self.transfer_number = self._generate_transfer_number()
        super().save(*args, **kwargs)

    def _generate_transfer_number(self):
        """Generate a unique transfer number."""
        from datetime import datetime
        prefix = "TRF"
        date_part = datetime.now().strftime("%Y%m%d")

        # Get the count of transfers for today
        today_count = Transfer.objects.filter(
            transfer_number__startswith=f"{prefix}{date_part}"
        ).count() + 1

        return f"{prefix}{date_part}{today_count:04d}"

    @property
    def total_items(self):
        """Return the total number of items in this transfer."""
        return self.items.count()

    @property
    def total_quantity(self):
        """Return the total quantity of samples in this transfer."""
        return sum(item.quantity for item in self.items.all())

    @property
    def is_overdue(self):
        """Check if the transfer is overdue."""
        if self.expected_arrival_date and self.status == 'IN_TRANSIT':
            return timezone.now() > self.expected_arrival_date
        return False

    def mark_in_transit(self, user=None):
        """Mark the transfer as in transit."""
        self.status = 'IN_TRANSIT'
        if user:
            self.initiated_by = user
        self.save()

    def mark_received(self, user=None):
        """Mark the transfer as received."""
        self.status = 'RECEIVED'
        self.actual_arrival_date = timezone.now()
        if user:
            self.received_by = user
        self.save()

    def cancel(self, reason=None):
        """Cancel the transfer."""
        self.status = 'CANCELLED'
        if reason:
            self.notes = f"{self.notes}\nCancelled: {reason}".strip()
        self.save()


class TransferItem(models.Model):
    """
    Represents an individual sample/item included in a transfer.
    """

    transfer = models.ForeignKey(
        Transfer,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Sample reference - using CharField for flexibility
    # Can be linked to MolecularSample, LabOrder, or other sample models
    sample_id = models.CharField(
        max_length=100,
        help_text="Sample identifier"
    )

    # Foreign key to lab_management.LabOrder sample if applicable
    lab_order = models.ForeignKey(
        'lab_management.LabOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_items',
        help_text="Associated lab order (if applicable)"
    )

    # Quantity information
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of sample units/aliquots"
    )

    # Container/storage information
    container_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of container (e.g., cryovial, tube)"
    )
    storage_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Position in shipping container/box"
    )

    # Condition tracking
    condition_on_departure = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sample condition when sent"
    )
    condition_on_arrival = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sample condition when received"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this item"
    )

    # Status
    is_received = models.BooleanField(
        default=False,
        help_text="Has this item been received and verified?"
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was this item received?"
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_transfer_items'
    )

    # Discrepancy tracking
    has_discrepancy = models.BooleanField(
        default=False,
        help_text="Is there any discrepancy with this item?"
    )
    discrepancy_notes = models.TextField(
        blank=True,
        help_text="Description of any discrepancies"
    )

    class Meta:
        verbose_name = "Transfer Item"
        verbose_name_plural = "Transfer Items"
        ordering = ['transfer', 'sample_id']

    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.sample_id} (x{self.quantity})"

    def mark_received(self, user=None, condition=None):
        """Mark this item as received."""
        self.is_received = True
        self.received_at = timezone.now()
        if user:
            self.received_by = user
        if condition:
            self.condition_on_arrival = condition
        self.save()

    def report_discrepancy(self, description):
        """Report a discrepancy for this item."""
        self.has_discrepancy = True
        self.discrepancy_notes = description
        self.save()

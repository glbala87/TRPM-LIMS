# storage/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


class StorageUnit(models.Model):
    """Storage equipment like freezers, refrigerators, nitrogen tanks"""

    UNIT_TYPE_CHOICES = [
        ('FREEZER_MINUS80', '-80°C Freezer'),
        ('FREEZER_MINUS20', '-20°C Freezer'),
        ('REFRIGERATOR', 'Refrigerator (2-8°C)'),
        ('NITROGEN_TANK', 'Liquid Nitrogen Tank'),
        ('ROOM_TEMP', 'Room Temperature Storage'),
        ('INCUBATOR', 'Incubator'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('FULL', 'Full'),
        ('OUT_OF_SERVICE', 'Out of Service'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)

    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Physical location (room, floor, building)"
    )

    temperature_min = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum temperature (°C)"
    )
    temperature_max = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum temperature (°C)"
    )
    temperature_target = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target temperature (°C)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)

    capacity_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., '4 shelves, 20 racks per shelf'"
    )

    has_temperature_monitoring = models.BooleanField(default=False)
    has_alarm = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Storage Unit"
        verbose_name_plural = "Storage Units"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_unit_type_display()})"

    @property
    def temperature_range(self):
        if self.temperature_min is not None and self.temperature_max is not None:
            return f"{self.temperature_min}°C to {self.temperature_max}°C"
        return None

    @property
    def total_positions(self):
        return sum(rack.total_positions for rack in self.racks.all())

    @property
    def occupied_positions(self):
        return StoragePosition.objects.filter(
            rack__unit=self,
            is_occupied=True
        ).count()

    @property
    def available_positions(self):
        return self.total_positions - self.occupied_positions


class StorageRack(models.Model):
    """Rack/shelf within a storage unit"""

    unit = models.ForeignKey(
        StorageUnit,
        on_delete=models.CASCADE,
        related_name='racks'
    )
    rack_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)

    shelf_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Shelf position in unit"
    )

    rows = models.PositiveIntegerField(
        default=8,
        validators=[MinValueValidator(1)],
        help_text="Number of rows (A-H typically)"
    )
    columns = models.PositiveIntegerField(
        default=12,
        validators=[MinValueValidator(1)],
        help_text="Number of columns (1-12 typically)"
    )

    rack_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., 'Box rack', 'Tube rack'"
    )

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Storage Rack"
        verbose_name_plural = "Storage Racks"
        unique_together = [['unit', 'rack_id']]
        ordering = ['unit', 'shelf_number', 'rack_id']

    def __str__(self):
        return f"{self.unit.code}/{self.rack_id}"

    @property
    def total_positions(self):
        return self.rows * self.columns

    @property
    def occupied_positions(self):
        return self.positions.filter(is_occupied=True).count()

    @property
    def available_positions(self):
        return self.total_positions - self.occupied_positions

    def get_position_label(self, row, column):
        """Convert row/column to position label (e.g., A1, B2)"""
        row_letter = chr(ord('A') + row - 1)
        return f"{row_letter}{column}"

    def get_available_position(self):
        """Get first available position in the rack"""
        occupied = set(self.positions.filter(is_occupied=True).values_list('position', flat=True))

        for row in range(1, self.rows + 1):
            for col in range(1, self.columns + 1):
                position = self.get_position_label(row, col)
                if position not in occupied:
                    # Create or get the position
                    pos, _ = StoragePosition.objects.get_or_create(
                        rack=self,
                        position=position,
                        defaults={'row': row, 'column': col}
                    )
                    return pos
        return None


class StoragePosition(models.Model):
    """Individual position within a rack"""

    rack = models.ForeignKey(
        StorageRack,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    position = models.CharField(
        max_length=10,
        help_text="Position label (e.g., A1, B2)"
    )
    row = models.PositiveIntegerField(null=True, blank=True)
    column = models.PositiveIntegerField(null=True, blank=True)

    is_occupied = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)

    stored_at = models.DateTimeField(null=True, blank=True)
    stored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stored_samples'
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Storage Position"
        verbose_name_plural = "Storage Positions"
        unique_together = [['rack', 'position']]
        ordering = ['rack', 'position']

    def __str__(self):
        return f"{self.rack.unit.code}/{self.rack.rack_id}/{self.position}"

    @property
    def full_location(self):
        return f"{self.rack.unit.name} > {self.rack.rack_id} > {self.position}"

    def store_sample(self, user=None):
        """Mark position as occupied"""
        self.is_occupied = True
        self.is_reserved = False
        self.stored_at = timezone.now()
        self.stored_by = user
        self.save()

    def remove_sample(self):
        """Mark position as unoccupied"""
        self.is_occupied = False
        self.stored_at = None
        self.stored_by = None
        self.save()

    def reserve(self):
        """Reserve position for upcoming storage"""
        if not self.is_occupied:
            self.is_reserved = True
            self.save()
            return True
        return False


class StorageLog(models.Model):
    """Audit log for storage operations"""

    ACTION_CHOICES = [
        ('STORE', 'Sample Stored'),
        ('RETRIEVE', 'Sample Retrieved'),
        ('MOVE', 'Sample Moved'),
        ('DISPOSE', 'Sample Disposed'),
    ]

    position = models.ForeignKey(
        StoragePosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    sample_id = models.CharField(
        max_length=100,
        help_text="Sample identifier (stored for historical reference)"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    from_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Previous location (for moves)"
    )
    to_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="New location (for moves)"
    )

    timestamp = models.DateTimeField(default=timezone.now)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Storage Log"
        verbose_name_plural = "Storage Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sample_id} - {self.get_action_display()} at {self.timestamp}"

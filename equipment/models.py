# equipment/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class InstrumentType(models.Model):
    """Types of laboratory instruments"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)

    maintenance_interval_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Recommended maintenance interval in days"
    )
    calibration_interval_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Required calibration interval in days"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Instrument Type"
        verbose_name_plural = "Instrument Types"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Instrument(models.Model):
    """Individual laboratory instruments"""

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('CALIBRATION', 'Under Calibration'),
        ('REPAIR', 'Under Repair'),
        ('RETIRED', 'Retired'),
        ('OUT_OF_SERVICE', 'Out of Service'),
    ]

    name = models.CharField(max_length=200)
    instrument_type = models.ForeignKey(
        InstrumentType,
        on_delete=models.PROTECT,
        related_name='instruments'
    )
    serial_number = models.CharField(max_length=100, unique=True)
    asset_number = models.CharField(max_length=100, blank=True)

    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    software_version = models.CharField(max_length=50, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Physical location in the lab"
    )

    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiration = models.DateField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)

    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    last_calibration = models.DateField(null=True, blank=True)
    next_calibration = models.DateField(null=True, blank=True)

    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)

    notes = models.TextField(blank=True)
    specifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Technical specifications"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Instrument"
        verbose_name_plural = "Instruments"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    @property
    def is_maintenance_due(self):
        if self.next_maintenance:
            return self.next_maintenance <= timezone.now().date()
        return False

    @property
    def is_calibration_due(self):
        if self.next_calibration:
            return self.next_calibration <= timezone.now().date()
        return False

    @property
    def is_available(self):
        return self.status == 'ACTIVE' and self.is_active

    @property
    def warranty_valid(self):
        if self.warranty_expiration:
            return self.warranty_expiration > timezone.now().date()
        return False


class MaintenanceRecord(models.Model):
    """Maintenance and calibration records for instruments"""

    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('CALIBRATION', 'Calibration'),
        ('QUALIFICATION', 'Qualification (IQ/OQ/PQ)'),
        ('REPAIR', 'Repair'),
        ('UPGRADE', 'Upgrade'),
        ('INSPECTION', 'Inspection'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )

    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )

    scheduled_date = models.DateField()
    performed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    performed_by = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of technician/engineer"
    )
    performed_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_performed'
    )

    service_provider = models.CharField(
        max_length=200,
        blank=True,
        help_text="External service company"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of work performed"
    )
    findings = models.TextField(
        blank=True,
        help_text="Issues found during maintenance"
    )
    actions_taken = models.TextField(
        blank=True,
        help_text="Corrective actions performed"
    )

    parts_replaced = models.TextField(
        blank=True,
        help_text="List of replaced parts"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    next_due = models.DateField(
        null=True,
        blank=True,
        help_text="Next maintenance/calibration due date"
    )

    certificate = models.FileField(
        upload_to='maintenance_certificates/%Y/%m/',
        null=True,
        blank=True,
        help_text="Calibration certificate or maintenance report"
    )
    certificate_number = models.CharField(max_length=100, blank=True)

    passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did the instrument pass calibration/qualification?"
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_created'
    )

    class Meta:
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.instrument.name} - {self.get_maintenance_type_display()} ({self.scheduled_date})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update instrument's maintenance/calibration dates when completed
        if self.status == 'COMPLETED' and self.completed_at:
            instrument = self.instrument

            if self.maintenance_type == 'CALIBRATION':
                instrument.last_calibration = self.completed_at.date()
                if self.next_due:
                    instrument.next_calibration = self.next_due
            elif self.maintenance_type in ['PREVENTIVE', 'CORRECTIVE']:
                instrument.last_maintenance = self.completed_at.date()
                if self.next_due:
                    instrument.next_maintenance = self.next_due

            instrument.save()

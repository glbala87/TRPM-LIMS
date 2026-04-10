# sensors/models.py
"""
Environmental sensor and monitoring models.
Inspired by baobab.lims temperature monitoring and NanoLIMS sensor data.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class SensorType(models.Model):
    """Type of monitoring sensor."""

    MEASUREMENT_TYPE_CHOICES = [
        ('TEMPERATURE', 'Temperature'), ('HUMIDITY', 'Humidity'),
        ('CO2', 'CO2 Level'), ('O2', 'Oxygen Level'),
        ('PRESSURE', 'Pressure'), ('DOOR', 'Door Status'),
        ('POWER', 'Power Status'), ('CUSTOM', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    measurement_type = models.CharField(max_length=20, choices=MEASUREMENT_TYPE_CHOICES)
    unit = models.CharField(max_length=20, help_text="Unit of measurement (°C, %, etc.)")
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sensor Type"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_measurement_type_display()})"


class MonitoringDevice(models.Model):
    """Physical monitoring device."""

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'), ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Maintenance'), ('RETIRED', 'Retired'),
    ]

    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    sensor_type = models.ForeignKey(SensorType, on_delete=models.PROTECT)
    mac_address = models.CharField(max_length=17, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Location
    storage_unit = models.ForeignKey(
        'storage.StorageUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='monitoring_devices'
    )
    location_description = models.CharField(max_length=200, blank=True)

    # Configuration
    reading_interval_minutes = models.PositiveIntegerField(default=15)
    alert_enabled = models.BooleanField(default=True)

    # Thresholds
    warning_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warning_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    critical_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    critical_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    last_reading = models.DateTimeField(null=True, blank=True)
    last_reading_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    installed_date = models.DateField(null=True, blank=True)
    calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Monitoring Device"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    def get_latest_reading(self):
        return self.readings.order_by('-timestamp').first()

    def is_in_alarm(self):
        if self.last_reading_value is None:
            return False
        if self.critical_min and self.last_reading_value < self.critical_min:
            return True
        if self.critical_max and self.last_reading_value > self.critical_max:
            return True
        return False


class SensorReading(models.Model):
    """Individual sensor reading."""

    STATUS_CHOICES = [
        ('NORMAL', 'Normal'), ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'), ('ERROR', 'Error'),
    ]

    device = models.ForeignKey(MonitoringDevice, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NORMAL')
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Sensor Reading"
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['device', 'timestamp'])]

    def __str__(self):
        return f"{self.device.name}: {self.value} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Auto-determine status based on thresholds
        device = self.device
        if device.critical_min and self.value < device.critical_min:
            self.status = 'CRITICAL'
        elif device.critical_max and self.value > device.critical_max:
            self.status = 'CRITICAL'
        elif device.warning_min and self.value < device.warning_min:
            self.status = 'WARNING'
        elif device.warning_max and self.value > device.warning_max:
            self.status = 'WARNING'
        else:
            self.status = 'NORMAL'

        super().save(*args, **kwargs)

        # Update device last reading
        device.last_reading = self.timestamp
        device.last_reading_value = self.value
        device.save(update_fields=['last_reading', 'last_reading_value'])


class SensorAlert(models.Model):
    """Alert triggered by sensor reading."""

    SEVERITY_CHOICES = [
        ('WARNING', 'Warning'), ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'), ('ACKNOWLEDGED', 'Acknowledged'), ('RESOLVED', 'Resolved'),
    ]

    device = models.ForeignKey(MonitoringDevice, on_delete=models.CASCADE, related_name='alerts')
    reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE, null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_sensor_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_sensor_alerts')
    resolution_notes = models.TextField(blank=True)

    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Sensor Alert"
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.device.name}: {self.get_severity_display()} at {self.triggered_at}"

    def acknowledge(self, user):
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save()

    def resolve(self, user, notes=''):
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()


class AlertNotificationRule(models.Model):
    """Rules for sending alert notifications."""

    name = models.CharField(max_length=100)
    sensor_types = models.ManyToManyField(SensorType, blank=True)
    devices = models.ManyToManyField(MonitoringDevice, blank=True)
    severity_levels = models.JSONField(default=list, help_text="List of severities to notify on")

    # Notification targets
    notify_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    notify_emails = models.JSONField(default=list, help_text="Additional email addresses")
    notify_sms = models.JSONField(default=list, help_text="SMS phone numbers")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alert Notification Rule"

    def __str__(self):
        return self.name

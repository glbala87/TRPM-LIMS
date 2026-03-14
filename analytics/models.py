# analytics/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class DashboardWidget(models.Model):
    """Configurable dashboard widgets."""
    WIDGET_TYPES = [
        ('KPI', 'KPI Card'),
        ('PIE', 'Pie Chart'),
        ('BAR', 'Bar Chart'),
        ('LINE', 'Line Chart'),
        ('TABLE', 'Data Table'),
        ('GAUGE', 'Gauge'),
    ]

    SIZE_CHOICES = [
        ('SM', 'Small (1/4)'),
        ('MD', 'Medium (1/2)'),
        ('LG', 'Large (3/4)'),
        ('XL', 'Full Width'),
    ]

    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=10, choices=WIDGET_TYPES)
    data_source = models.CharField(max_length=200, help_text="Service method or query identifier")
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default='MD')
    position = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        verbose_name = "Dashboard Widget"

    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"


class SavedQuery(models.Model):
    """Reusable analytical queries."""
    QUERY_TYPES = [
        ('SAMPLE', 'Sample Query'),
        ('QC', 'QC Query'),
        ('EQUIPMENT', 'Equipment Query'),
        ('CUSTOM', 'Custom Query'),
    ]

    name = models.CharField(max_length=200)
    query_type = models.CharField(max_length=20, choices=QUERY_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_queries')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Saved Query"
        verbose_name_plural = "Saved Queries"
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Report(models.Model):
    """Generated analytical reports."""
    REPORT_TYPES = [
        ('DAILY', 'Daily Summary'),
        ('WEEKLY', 'Weekly Summary'),
        ('MONTHLY', 'Monthly Summary'),
        ('TAT', 'Turnaround Time'),
        ('QC', 'Quality Control'),
        ('CUSTOM', 'Custom Report'),
    ]

    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('XLSX', 'Excel'),
        ('CSV', 'CSV'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    output_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='PDF')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    parameters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    error_message = models.TextField(blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Report"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class KPIMetric(models.Model):
    """Historical KPI snapshots."""
    CATEGORIES = [
        ('SAMPLE', 'Samples'),
        ('QC', 'Quality Control'),
        ('EQUIPMENT', 'Equipment'),
        ('REAGENT', 'Reagents'),
        ('STORAGE', 'Storage'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    unit = models.CharField(max_length=50, blank=True)
    date = models.DateField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "KPI Metric"
        ordering = ['-date', 'name']
        indexes = [
            models.Index(fields=['name', 'date']),
            models.Index(fields=['category', 'date']),
        ]

    def __str__(self):
        return f"{self.name}: {self.value}{self.unit} ({self.date})"


class Alert(models.Model):
    """System alerts for dashboard display."""
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('WARNING', 'Warning'),
        ('INFO', 'Informational'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    source = models.CharField(max_length=100, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alert"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


class ScheduledReport(models.Model):
    """Automated report scheduling."""
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    output_format = models.CharField(max_length=10, choices=Report.FORMAT_CHOICES, default='PDF')
    recipients = models.TextField(help_text="Comma-separated email addresses")
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Scheduled Report"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

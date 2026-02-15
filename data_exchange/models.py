"""
Data exchange models for batch import/export operations.
"""
from django.db import models
from django.conf import settings
import uuid


class ImportJob(models.Model):
    """
    Tracks batch import operations.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VALIDATING', 'Validating'),
        ('VALIDATED', 'Validated'),
        ('IMPORTING', 'Importing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    DATA_TYPE_CHOICES = [
        ('PATIENTS', 'Patients'),
        ('SAMPLES', 'Samples'),
        ('RESULTS', 'Results'),
        ('REAGENTS', 'Reagents'),
        ('EQUIPMENT', 'Equipment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # File information
    source_file = models.FileField(upload_to='imports/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_format = models.CharField(max_length=20, default='CSV')  # CSV, XLSX

    # Import statistics
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    skipped_rows = models.PositiveIntegerField(default=0)

    # Validation and error details
    validation_errors = models.JSONField(default=list, blank=True)
    import_errors = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)

    # Column mapping (for flexible imports)
    column_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text="Maps source columns to model fields"
    )

    # Options
    skip_duplicates = models.BooleanField(default=True)
    update_existing = models.BooleanField(default=False)
    dry_run = models.BooleanField(default=False)

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='import_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Import Job'
        verbose_name_plural = 'Import Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.data_type} Import - {self.status} ({self.id})"

    @property
    def progress_percentage(self):
        if self.total_rows == 0:
            return 0
        return int((self.processed_rows / self.total_rows) * 100)

    @property
    def success_rate(self):
        if self.processed_rows == 0:
            return 0
        return int((self.successful_rows / self.processed_rows) * 100)


class ImportedRecord(models.Model):
    """
    Tracks individual records imported via ImportJob.
    """
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('SKIPPED', 'Skipped'),
        ('DUPLICATE', 'Duplicate'),
    ]

    import_job = models.ForeignKey(
        ImportJob,
        on_delete=models.CASCADE,
        related_name='records'
    )
    row_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    raw_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    # Reference to created/updated object
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imported Record'
        verbose_name_plural = 'Imported Records'
        ordering = ['row_number']

    def __str__(self):
        return f"Row {self.row_number}: {self.status}"


class ExportTemplate(models.Model):
    """
    Saved templates for exporting data.
    """
    DATA_TYPE_CHOICES = [
        ('PATIENTS', 'Patients'),
        ('SAMPLES', 'Samples'),
        ('RESULTS', 'Results'),
        ('LAB_ORDERS', 'Lab Orders'),
        ('REAGENTS', 'Reagents'),
        ('EQUIPMENT', 'Equipment'),
        ('AUDIT_LOGS', 'Audit Logs'),
    ]

    FORMAT_CHOICES = [
        ('CSV', 'CSV'),
        ('XLSX', 'Excel'),
        ('JSON', 'JSON'),
        ('PDF', 'PDF'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES)
    output_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='CSV')

    # Column configuration
    included_fields = models.JSONField(
        default=list,
        help_text="List of field names to include in export"
    )
    field_labels = models.JSONField(
        default=dict,
        help_text="Custom labels for fields"
    )
    field_order = models.JSONField(
        default=list,
        help_text="Order of fields in export"
    )

    # Filters
    default_filters = models.JSONField(
        default=dict,
        help_text="Default filter criteria"
    )

    # Formatting options
    date_format = models.CharField(max_length=50, default='%Y-%m-%d')
    datetime_format = models.CharField(max_length=50, default='%Y-%m-%d %H:%M:%S')
    include_headers = models.BooleanField(default=True)

    # Access control
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='export_templates'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Export Template'
        verbose_name_plural = 'Export Templates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.data_type})"


class ExportJob(models.Model):
    """
    Tracks export operations.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ExportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='export_jobs'
    )
    data_type = models.CharField(max_length=50)
    output_format = models.CharField(max_length=10, default='CSV')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Filters applied
    filters = models.JSONField(default=dict, blank=True)

    # Result
    output_file = models.FileField(upload_to='exports/%Y/%m/', null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='export_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Export Job'
        verbose_name_plural = 'Export Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.data_type} Export - {self.status} ({self.id})"

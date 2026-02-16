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


class ExternalSystem(models.Model):
    """
    Configuration for external systems (EHR, LIS) for HL7/FHIR integration.
    """

    PROTOCOL_CHOICES = [
        ('HL7V2', 'HL7 v2.x'),
        ('FHIR_R4', 'FHIR R4'),
        ('FHIR_STU3', 'FHIR STU3'),
    ]

    TRANSPORT_CHOICES = [
        ('MLLP', 'MLLP (TCP/IP)'),
        ('HTTP', 'HTTP/HTTPS'),
        ('SFTP', 'SFTP'),
        ('FILE', 'File System'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TESTING', 'Testing'),
        ('ERROR', 'Error'),
    ]

    # Basic identification
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="System identifier name"
    )
    description = models.TextField(blank=True)
    system_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of system (EHR, LIS, etc.)"
    )

    # Protocol configuration
    protocol = models.CharField(
        max_length=20,
        choices=PROTOCOL_CHOICES,
        default='HL7V2'
    )
    protocol_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="Protocol version (e.g., 2.5.1, R4)"
    )

    # Transport configuration
    transport = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        default='MLLP'
    )
    host = models.CharField(
        max_length=255,
        blank=True,
        help_text="Hostname or IP address"
    )
    port = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Port number"
    )
    path = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL path or file path"
    )

    # Authentication
    credentials = models.JSONField(
        default=dict,
        blank=True,
        help_text="Authentication credentials (encrypted in production)"
    )
    # Example: {"username": "...", "password": "...", "api_key": "...", "client_id": "..."}

    # HL7 v2 configuration
    hl7_sending_application = models.CharField(
        max_length=50,
        default='TRPM-LIMS',
        help_text="MSH-3: Sending Application"
    )
    hl7_sending_facility = models.CharField(
        max_length=50,
        blank=True,
        help_text="MSH-4: Sending Facility"
    )
    hl7_receiving_application = models.CharField(
        max_length=50,
        blank=True,
        help_text="MSH-5: Receiving Application"
    )
    hl7_receiving_facility = models.CharField(
        max_length=50,
        blank=True,
        help_text="MSH-6: Receiving Facility"
    )
    hl7_version = models.CharField(
        max_length=10,
        default='2.5.1',
        help_text="HL7 Version ID"
    )

    # FHIR configuration
    fhir_base_url = models.URLField(
        blank=True,
        help_text="FHIR server base URL"
    )
    fhir_client_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="OAuth2 client ID"
    )
    fhir_capabilities = models.JSONField(
        default=list,
        blank=True,
        help_text="Supported FHIR resources/operations"
    )

    # Connection settings
    timeout_seconds = models.PositiveIntegerField(
        default=30,
        help_text="Connection timeout in seconds"
    )
    retry_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Number of retry attempts"
    )
    retry_delay_seconds = models.PositiveIntegerField(
        default=60,
        help_text="Delay between retries"
    )

    # Message settings
    message_encoding = models.CharField(
        max_length=20,
        default='UTF-8',
        help_text="Character encoding for messages"
    )
    auto_acknowledge = models.BooleanField(
        default=True,
        help_text="Automatically send acknowledgments"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='INACTIVE'
    )
    last_connection_at = models.DateTimeField(
        null=True,
        blank=True
    )
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'External System'
        verbose_name_plural = 'External Systems'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_protocol_display()})"

    @property
    def connection_string(self):
        """Get connection string for display."""
        if self.transport in ['MLLP', 'HTTP']:
            return f"{self.host}:{self.port}{self.path or ''}"
        elif self.transport == 'SFTP':
            return f"sftp://{self.host}:{self.port or 22}{self.path}"
        return self.path


class MessageLog(models.Model):
    """
    Log of HL7/FHIR messages sent and received.
    """

    DIRECTION_CHOICES = [
        ('OUTBOUND', 'Outbound'),
        ('INBOUND', 'Inbound'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENDING', 'Sending'),
        ('SENT', 'Sent'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('FAILED', 'Failed'),
        ('REJECTED', 'Rejected'),
        ('RETRYING', 'Retrying'),
    ]

    MESSAGE_TYPE_CHOICES = [
        # HL7 v2 messages
        ('ORU_R01', 'ORU^R01 - Observation Result'),
        ('ORM_O01', 'ORM^O01 - Order Message'),
        ('ADT_A01', 'ADT^A01 - Admit'),
        ('ADT_A04', 'ADT^A04 - Register'),
        ('ACK', 'ACK - Acknowledgment'),
        # FHIR resources
        ('FHIR_DIAGNOSTIC_REPORT', 'FHIR DiagnosticReport'),
        ('FHIR_OBSERVATION', 'FHIR Observation'),
        ('FHIR_PATIENT', 'FHIR Patient'),
        ('FHIR_SPECIMEN', 'FHIR Specimen'),
        ('FHIR_BUNDLE', 'FHIR Bundle'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # System and direction
    external_system = models.ForeignKey(
        ExternalSystem,
        on_delete=models.CASCADE,
        related_name='message_logs'
    )
    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES
    )

    # Message identification
    message_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Message Control ID (MSH-10) or FHIR ID"
    )
    message_type = models.CharField(
        max_length=50,
        choices=MESSAGE_TYPE_CHOICES
    )

    # Message content
    raw_message = models.TextField(
        help_text="Raw message content"
    )
    parsed_message = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parsed message structure"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    status_message = models.TextField(blank=True)

    # Linked LIMS object (GenericForeignKey)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)

    # Acknowledgment
    acknowledgment_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of acknowledgment message"
    )
    acknowledgment_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="ACK code (AA, AE, AR)"
    )
    acknowledgment_message = models.TextField(blank=True)

    # Retry tracking
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Message Log'
        verbose_name_plural = 'Message Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['external_system', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.message_type} - {self.message_id} ({self.status})"

    @property
    def is_successful(self):
        return self.status in ['SENT', 'ACKNOWLEDGED']

    @property
    def needs_retry(self):
        return (
            self.status in ['FAILED', 'RETRYING'] and
            self.retry_count < self.external_system.retry_attempts
        )

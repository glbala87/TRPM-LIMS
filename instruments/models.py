# instruments/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class InstrumentConnection(models.Model):
    """Configuration for instrument network connections."""

    PROTOCOL_CHOICES = [
        ('ASTM', 'ASTM E1381/E1394'),
        ('HL7', 'HL7 v2.x'),
        ('CUSTOM', 'Custom Protocol'),
    ]

    CONNECTION_TYPE_CHOICES = [
        ('TCP_SERVER', 'TCP Server (Listen)'),
        ('TCP_CLIENT', 'TCP Client (Connect)'),
        ('SERIAL', 'Serial Port'),
    ]

    instrument = models.ForeignKey(
        'equipment.Instrument',
        on_delete=models.CASCADE,
        related_name='connections'
    )

    name = models.CharField(
        max_length=100,
        help_text="Friendly name for this connection"
    )

    protocol = models.CharField(
        max_length=10,
        choices=PROTOCOL_CHOICES,
        default='ASTM'
    )

    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPE_CHOICES,
        default='TCP_SERVER'
    )

    # Network settings
    host = models.CharField(
        max_length=255,
        default='0.0.0.0',
        help_text="IP address or hostname"
    )
    port = models.PositiveIntegerField(
        default=5000,
        help_text="TCP port number"
    )

    # Serial settings (for serial connections)
    serial_port = models.CharField(
        max_length=50,
        blank=True,
        help_text="Serial port (e.g., COM1, /dev/ttyUSB0)"
    )
    baud_rate = models.PositiveIntegerField(
        default=9600,
        help_text="Baud rate for serial connections"
    )

    # Connection parameters
    timeout = models.PositiveIntegerField(
        default=30,
        help_text="Connection timeout in seconds"
    )
    retry_interval = models.PositiveIntegerField(
        default=60,
        help_text="Retry interval in seconds after connection failure"
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        help_text="Maximum connection retry attempts"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable this connection"
    )
    auto_start = models.BooleanField(
        default=True,
        help_text="Automatically start connection on service startup"
    )

    last_connection = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful connection time"
    )
    last_message = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last message received/sent"
    )
    connection_status = models.CharField(
        max_length=20,
        default='DISCONNECTED',
        choices=[
            ('CONNECTED', 'Connected'),
            ('DISCONNECTED', 'Disconnected'),
            ('CONNECTING', 'Connecting'),
            ('ERROR', 'Error'),
        ]
    )
    last_error = models.TextField(
        blank=True,
        help_text="Last error message"
    )

    # Protocol-specific configuration
    protocol_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Protocol-specific configuration options"
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instrument_connections_created'
    )

    class Meta:
        verbose_name = "Instrument Connection"
        verbose_name_plural = "Instrument Connections"
        ordering = ['instrument__name', 'name']
        unique_together = [['host', 'port']]

    def __str__(self):
        return f"{self.instrument.name} - {self.name} ({self.get_protocol_display()})"

    def update_connection_status(self, status, error=None):
        """Update the connection status."""
        self.connection_status = status
        if status == 'CONNECTED':
            self.last_connection = timezone.now()
            self.last_error = ''
        elif error:
            self.last_error = str(error)
        self.save(update_fields=['connection_status', 'last_connection', 'last_error', 'updated_at'])

    def update_last_message(self):
        """Update the last message timestamp."""
        self.last_message = timezone.now()
        self.save(update_fields=['last_message', 'updated_at'])


class MessageLog(models.Model):
    """Log of messages sent/received from instruments."""

    DIRECTION_CHOICES = [
        ('INBOUND', 'Inbound (from instrument)'),
        ('OUTBOUND', 'Outbound (to instrument)'),
    ]

    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('PARSED', 'Parsed'),
        ('PROCESSED', 'Processed'),
        ('SENT', 'Sent'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('ERROR', 'Error'),
        ('IGNORED', 'Ignored'),
    ]

    MESSAGE_TYPE_CHOICES = [
        # ASTM message types
        ('ASTM_HEADER', 'ASTM Header'),
        ('ASTM_PATIENT', 'ASTM Patient'),
        ('ASTM_ORDER', 'ASTM Order'),
        ('ASTM_RESULT', 'ASTM Result'),
        ('ASTM_COMMENT', 'ASTM Comment'),
        ('ASTM_TERMINATOR', 'ASTM Terminator'),
        ('ASTM_QUERY', 'ASTM Query'),
        # HL7 message types
        ('HL7_ORM', 'HL7 Order Message (ORM)'),
        ('HL7_ORU', 'HL7 Observation Result (ORU)'),
        ('HL7_QRY', 'HL7 Query Message (QRY)'),
        ('HL7_ACK', 'HL7 Acknowledgment (ACK)'),
        ('HL7_ADT', 'HL7 Admit/Discharge/Transfer (ADT)'),
        # Other
        ('RAW', 'Raw Data'),
        ('UNKNOWN', 'Unknown'),
    ]

    connection = models.ForeignKey(
        InstrumentConnection,
        on_delete=models.CASCADE,
        related_name='message_logs'
    )

    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES
    )

    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='UNKNOWN'
    )

    # Message content
    raw_message = models.TextField(
        help_text="Raw message as received/sent"
    )
    parsed_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parsed message data"
    )

    # Processing info
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED'
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if processing failed"
    )

    # Related records (populated after processing)
    related_sample_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Sample ID from message"
    )
    related_patient_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Patient ID from message"
    )
    related_order_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Order ID from message"
    )

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Checksum/validation
    checksum = models.CharField(
        max_length=10,
        blank=True,
        help_text="Message checksum"
    )
    checksum_valid = models.BooleanField(
        null=True,
        blank=True,
        help_text="Was the checksum valid?"
    )

    class Meta:
        verbose_name = "Message Log"
        verbose_name_plural = "Message Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['connection', 'timestamp']),
            models.Index(fields=['direction', 'status']),
            models.Index(fields=['related_sample_id']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        return f"{self.connection.instrument.name} - {self.get_direction_display()} - {self.timestamp}"

    def mark_processed(self, parsed_data=None, error=None):
        """Mark message as processed."""
        self.processed_at = timezone.now()
        if parsed_data:
            self.parsed_data = parsed_data
            self.status = 'PROCESSED'
        if error:
            self.error_message = str(error)
            self.status = 'ERROR'
        self.save()


class WorklistExport(models.Model):
    """Track worklist exports to instruments."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('PARTIAL', 'Partially Processed'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error'),
    ]

    connection = models.ForeignKey(
        InstrumentConnection,
        on_delete=models.CASCADE,
        related_name='worklist_exports'
    )

    # Export content
    samples = models.JSONField(
        default=list,
        help_text="List of sample IDs included in worklist"
    )
    export_data = models.JSONField(
        default=dict,
        help_text="Full worklist data"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worklist_exports'
    )

    error_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Worklist Export"
        verbose_name_plural = "Worklist Exports"
        ordering = ['-created_at']

    def __str__(self):
        return f"Worklist to {self.connection.instrument.name} ({self.created_at})"

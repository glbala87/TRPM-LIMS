# molecular_diagnostics/models/samples.py

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class MolecularSampleType(models.Model):
    """Types of samples used in molecular diagnostics (e.g., Whole Blood, Tissue, Saliva)"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    collection_instructions = models.TextField(blank=True)
    storage_temperature = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., -20°C, 2-8°C, Room Temperature"
    )
    stability_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum hours sample remains stable at storage temperature"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Molecular Sample Type"
        verbose_name_plural = "Molecular Sample Types"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class MolecularSample(models.Model):
    """Molecular sample linked to a lab order, with workflow tracking"""

    WORKFLOW_STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('EXTRACTED', 'Extracted'),
        ('AMPLIFIED', 'Amplified'),
        ('SEQUENCED', 'Sequenced'),
        ('ANALYZED', 'Analyzed'),
        ('REPORTED', 'Reported'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]

    sample_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique sample identifier"
    )
    lab_order = models.ForeignKey(
        'lab_management.LabOrder',
        on_delete=models.CASCADE,
        related_name='molecular_samples'
    )
    sample_type = models.ForeignKey(
        MolecularSampleType,
        on_delete=models.PROTECT,
        related_name='samples'
    )
    workflow_status = models.CharField(
        max_length=20,
        choices=WORKFLOW_STATUS_CHOICES,
        default='RECEIVED'
    )
    current_step = models.ForeignKey(
        'molecular_diagnostics.WorkflowStep',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_samples'
    )
    test_panel = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.PROTECT,
        related_name='samples',
        null=True,
        blank=True
    )

    collection_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sample was collected from the patient"
    )
    received_datetime = models.DateTimeField(
        default=timezone.now,
        help_text="When the sample was received in the lab"
    )

    storage_location = models.ForeignKey(
        'storage.StoragePosition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='samples'
    )

    # Aliquot tracking
    aliquot_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aliquots',
        help_text="Parent sample if this is an aliquot"
    )
    aliquot_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Aliquot number (1, 2, 3, etc.)"
    )

    volume_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Volume in microliters"
    )
    concentration_ng_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Concentration in ng/µL (after extraction)"
    )
    a260_280_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="A260/A280 purity ratio"
    )

    priority = models.CharField(
        max_length=20,
        choices=[
            ('ROUTINE', 'Routine'),
            ('URGENT', 'Urgent'),
            ('STAT', 'STAT'),
        ],
        default='ROUTINE'
    )

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_molecular_samples'
    )

    class Meta:
        verbose_name = "Molecular Sample"
        verbose_name_plural = "Molecular Samples"
        ordering = ['-received_datetime']

    def save(self, *args, **kwargs):
        if not self.sample_id:
            self.sample_id = self._generate_sample_id()
        super().save(*args, **kwargs)

    def _generate_sample_id(self):
        """Generate unique sample ID with format: MOL-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"MOL-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.sample_id} ({self.get_workflow_status_display()})"

    @property
    def is_aliquot(self):
        return self.aliquot_of is not None

    @property
    def patient(self):
        return self.lab_order.patient

    def get_turnaround_time(self):
        """Calculate current turnaround time in hours"""
        if self.workflow_status == 'REPORTED':
            # Get the reported history entry
            reported_entry = self.history.filter(to_status='REPORTED').first()
            if reported_entry:
                delta = reported_entry.timestamp - self.received_datetime
                return delta.total_seconds() / 3600
        delta = timezone.now() - self.received_datetime
        return delta.total_seconds() / 3600

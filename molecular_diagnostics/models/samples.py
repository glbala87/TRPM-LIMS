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

    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('STAT', 'STAT'),
    ]

    DERIVATION_TYPE_CHOICES = [
        ('ORIGINAL', 'Original Sample'),
        ('ALIQUOT', 'Aliquot'),
        ('EXTRACT', 'Extracted Material'),
        ('LIBRARY', 'Sequencing Library'),
        ('DISSECTION', 'Dissected Tissue'),
        ('AMPLICON', 'Amplified Product'),
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

    # Sample hierarchy and derivation tracking
    parent_sample = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_samples',
        help_text="Parent sample this was derived from"
    )
    derivation_type = models.CharField(
        max_length=20,
        choices=DERIVATION_TYPE_CHOICES,
        default='ORIGINAL',
        help_text="How this sample was derived from parent"
    )
    aliquot_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Aliquot number (1, 2, 3, etc.)"
    )
    # Keep aliquot_of as an alias property for backward compatibility
    @property
    def aliquot_of(self):
        """Backward compatibility alias for parent_sample."""
        return self.parent_sample if self.derivation_type == 'ALIQUOT' else None

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
        choices=PRIORITY_CHOICES,
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
        return self.derivation_type == 'ALIQUOT'

    @property
    def is_derived(self):
        """Check if this sample was derived from another sample."""
        return self.parent_sample is not None

    @property
    def is_original(self):
        """Check if this is an original sample (not derived)."""
        return self.derivation_type == 'ORIGINAL' and self.parent_sample is None

    @property
    def patient(self):
        return self.lab_order.patient

    def get_ancestor_chain(self):
        """
        Get the complete ancestry chain from this sample back to the original.
        Returns a list starting with the oldest ancestor and ending with self.
        """
        chain = [self]
        current = self

        # Prevent infinite loops with a max depth
        max_depth = 20
        depth = 0

        while current.parent_sample and depth < max_depth:
            chain.insert(0, current.parent_sample)
            current = current.parent_sample
            depth += 1

        return chain

    def get_root_sample(self):
        """Get the original/root sample in the ancestry chain."""
        chain = self.get_ancestor_chain()
        return chain[0] if chain else self

    def get_descendants(self, include_self=False):
        """
        Get all samples derived from this sample (recursive).
        Returns a flat list of all descendant samples.
        """
        descendants = []
        if include_self:
            descendants.append(self)

        for child in self.derived_samples.all():
            descendants.append(child)
            descendants.extend(child.get_descendants(include_self=False))

        return descendants

    def create_aliquot(self, volume_ul=None, created_by=None, notes=''):
        """
        Create an aliquot from this sample.
        Returns the new aliquot sample.
        """
        # Count existing aliquots to determine aliquot number
        existing_aliquots = MolecularSample.objects.filter(
            parent_sample=self,
            derivation_type='ALIQUOT'
        ).count()

        aliquot = MolecularSample.objects.create(
            lab_order=self.lab_order,
            sample_type=self.sample_type,
            parent_sample=self,
            derivation_type='ALIQUOT',
            aliquot_number=existing_aliquots + 1,
            volume_ul=volume_ul,
            priority=self.priority,
            notes=notes,
            created_by=created_by,
        )
        return aliquot

    def create_extract(self, volume_ul=None, concentration_ng_ul=None,
                       a260_280_ratio=None, created_by=None, notes=''):
        """
        Create an extracted material sample from this sample.
        Returns the new extract sample.
        """
        extract = MolecularSample.objects.create(
            lab_order=self.lab_order,
            sample_type=self.sample_type,
            parent_sample=self,
            derivation_type='EXTRACT',
            volume_ul=volume_ul,
            concentration_ng_ul=concentration_ng_ul,
            a260_280_ratio=a260_280_ratio,
            priority=self.priority,
            workflow_status='EXTRACTED',
            notes=notes,
            created_by=created_by,
        )
        return extract

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

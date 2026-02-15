# pathology/models/histology.py
"""
Histology specimen tracking model.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Histology(models.Model):
    """
    Histology specimen tracking from receipt through processing to slides.
    """
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('GROSSING', 'Grossing'),
        ('PROCESSING', 'Processing'),
        ('EMBEDDING', 'Embedding'),
        ('CUTTING', 'Cutting'),
        ('STAINING', 'Staining'),
        ('COVERSLIPPING', 'Coverslipping'),
        ('QC', 'Quality Control'),
        ('READY', 'Ready for Review'),
        ('IN_REVIEW', 'In Review'),
        ('REPORTED', 'Reported'),
        ('ARCHIVED', 'Archived'),
        ('CANCELLED', 'Cancelled'),
    ]

    FIXATION_CHOICES = [
        ('FORMALIN', 'Formalin'),
        ('ALCOHOL', 'Alcohol'),
        ('FROZEN', 'Frozen'),
        ('FRESH', 'Fresh'),
        ('OTHER', 'Other'),
    ]

    histology_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique histology identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='histology_samples'
    )

    # Source - can be from molecular sample or lab order
    molecular_sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='histology_samples'
    )
    lab_order = models.ForeignKey(
        'lab_management.LabOrder',
        on_delete=models.CASCADE,
        related_name='histology_samples'
    )

    # Specimen info
    specimen_type = models.ForeignKey(
        'pathology.SpecimenType',
        on_delete=models.PROTECT,
        related_name='histology_samples'
    )
    specimen_site = models.ForeignKey(
        'pathology.TumorSite',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='histology_samples'
    )
    clinical_history = models.TextField(blank=True)

    # Identifiers
    surgical_number = models.CharField(max_length=50, blank=True, help_text="Surgical pathology number")
    accession_number = models.CharField(max_length=50, blank=True)
    h_and_e_barcode = models.CharField(max_length=100, blank=True, help_text="H&E slide barcode")

    # Processing info
    fixation_type = models.CharField(max_length=20, choices=FIXATION_CHOICES, default='FORMALIN')
    fixation_start = models.DateTimeField(null=True, blank=True)
    fixation_end = models.DateTimeField(null=True, blank=True)

    # Blocks and slides
    block_count = models.PositiveSmallIntegerField(default=1)
    slide_count = models.PositiveSmallIntegerField(default=0)

    # Tissue quality
    tumor_cell_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tumor cell percentage"
    )
    necrosis_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Necrosis percentage"
    )
    tissue_adequacy = models.CharField(
        max_length=20,
        choices=[
            ('ADEQUATE', 'Adequate'),
            ('SUBOPTIMAL', 'Suboptimal'),
            ('INADEQUATE', 'Inadequate'),
        ],
        blank=True
    )

    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    received_datetime = models.DateTimeField(default=timezone.now)
    grossing_datetime = models.DateTimeField(null=True, blank=True)
    processed_datetime = models.DateTimeField(null=True, blank=True)

    # Gross description
    gross_description = models.TextField(blank=True)
    gross_measurements = models.CharField(max_length=200, blank=True, help_text="e.g., 3.0 x 2.5 x 1.5 cm")
    gross_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in grams")

    # Images
    gross_photo_count = models.PositiveSmallIntegerField(default=0)

    # Notes
    notes = models.TextField(blank=True)
    is_stat = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_histology'
    )

    class Meta:
        verbose_name = "Histology"
        verbose_name_plural = "Histologies"
        ordering = ['-received_datetime']

    def save(self, *args, **kwargs):
        if not self.histology_id:
            self.histology_id = self._generate_histology_id()
        super().save(*args, **kwargs)

    def _generate_histology_id(self):
        """Generate unique histology ID with format: HIS-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"HIS-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.histology_id} ({self.get_status_display()})"

    @property
    def patient(self):
        return self.lab_order.patient

    @property
    def fixation_hours(self):
        """Calculate fixation time in hours."""
        if self.fixation_start and self.fixation_end:
            delta = self.fixation_end - self.fixation_start
            return delta.total_seconds() / 3600
        return None


class HistologyBlock(models.Model):
    """
    Individual tissue block from a histology specimen.
    """
    histology = models.ForeignKey(
        Histology,
        on_delete=models.CASCADE,
        related_name='blocks'
    )

    block_id = models.CharField(max_length=20, help_text="e.g., A, B, C or 1, 2, 3")
    barcode = models.CharField(max_length=100, blank=True)

    # Block info
    tissue_description = models.CharField(max_length=200, blank=True)
    cassette_color = models.CharField(max_length=20, blank=True)

    # Processing
    embedded_at = models.DateTimeField(null=True, blank=True)
    embedded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='embedded_blocks'
    )

    # Quality
    is_decalcified = models.BooleanField(default=False)
    decalcification_method = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Histology Block"
        verbose_name_plural = "Histology Blocks"
        ordering = ['histology', 'block_id']
        unique_together = [['histology', 'block_id']]

    def __str__(self):
        return f"{self.histology.histology_id}-{self.block_id}"


class HistologySlide(models.Model):
    """
    Individual slide cut from a histology block.
    """
    block = models.ForeignKey(
        HistologyBlock,
        on_delete=models.CASCADE,
        related_name='slides'
    )

    slide_number = models.PositiveSmallIntegerField(default=1)
    barcode = models.CharField(max_length=100, blank=True)

    # Staining
    stain = models.ForeignKey(
        'pathology.StainingProtocol',
        on_delete=models.PROTECT,
        related_name='slides'
    )
    stained_at = models.DateTimeField(null=True, blank=True)
    stained_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stained_slides'
    )

    # Quality
    QUALITY_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('ACCEPTABLE', 'Acceptable'),
        ('POOR', 'Poor'),
        ('UNACCEPTABLE', 'Unacceptable'),
    ]
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, blank=True)
    quality_notes = models.TextField(blank=True)
    requires_recut = models.BooleanField(default=False)

    # Digital pathology
    is_scanned = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(null=True, blank=True)
    scan_magnification = models.CharField(max_length=10, blank=True, help_text="e.g., 20x, 40x")
    scan_file_path = models.CharField(max_length=500, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Histology Slide"
        verbose_name_plural = "Histology Slides"
        ordering = ['block', 'slide_number']

    def __str__(self):
        return f"{self.block}-{self.slide_number} ({self.stain.code})"

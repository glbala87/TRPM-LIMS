# microbiology/models/results.py
"""
Microbiology result models for organism identification and AST results.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class MicrobiologySample(models.Model):
    """
    Microbiology sample linked to a lab order.
    """
    SAMPLE_STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('IN_PROCESS', 'In Process'),
        ('CULTURE_SETUP', 'Culture Setup'),
        ('INCUBATION', 'Incubation'),
        ('IDENTIFICATION', 'Identification'),
        ('AST_PENDING', 'AST Pending'),
        ('AST_COMPLETE', 'AST Complete'),
        ('REVIEW', 'Review'),
        ('REPORTED', 'Reported'),
        ('CANCELLED', 'Cancelled'),
    ]

    SPECIMEN_TYPE_CHOICES = [
        ('BLOOD', 'Blood'),
        ('URINE', 'Urine'),
        ('SPUTUM', 'Sputum'),
        ('STOOL', 'Stool'),
        ('CSF', 'Cerebrospinal Fluid'),
        ('WOUND', 'Wound Swab'),
        ('TISSUE', 'Tissue'),
        ('THROAT', 'Throat Swab'),
        ('NASAL', 'Nasal Swab'),
        ('RESPIRATORY', 'Respiratory'),
        ('GENITAL', 'Genital'),
        ('FLUID', 'Body Fluid'),
        ('OTHER', 'Other'),
    ]

    sample_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique sample identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='microbiology_samples'
    )
    lab_order = models.ForeignKey(
        'lab_management.LabOrder',
        on_delete=models.CASCADE,
        related_name='microbiology_samples'
    )

    specimen_type = models.CharField(max_length=20, choices=SPECIMEN_TYPE_CHOICES)
    specimen_source = models.CharField(max_length=100, blank=True, help_text="Specific source/site")
    collection_datetime = models.DateTimeField(null=True, blank=True)
    received_datetime = models.DateTimeField(default=timezone.now)

    status = models.CharField(max_length=20, choices=SAMPLE_STATUS_CHOICES, default='RECEIVED')

    # Culture details
    culture_type = models.CharField(max_length=50, blank=True, help_text="e.g., Aerobic, Anaerobic")
    culture_setup_datetime = models.DateTimeField(null=True, blank=True)
    incubation_start = models.DateTimeField(null=True, blank=True)
    incubation_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    # Clinical info
    clinical_info = models.TextField(blank=True)
    antibiotics_prior = models.TextField(blank=True, help_text="Prior antibiotic therapy")

    # Result summary
    growth_observed = models.BooleanField(null=True, blank=True)
    preliminary_result = models.TextField(blank=True)
    final_result = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_micro_samples'
    )

    class Meta:
        verbose_name = "Microbiology Sample"
        verbose_name_plural = "Microbiology Samples"
        ordering = ['-received_datetime']

    def save(self, *args, **kwargs):
        if not self.sample_id:
            self.sample_id = self._generate_sample_id()
        super().save(*args, **kwargs)

    def _generate_sample_id(self):
        """Generate unique sample ID with format: MIC-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"MIC-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.sample_id} ({self.get_specimen_type_display()})"


class OrganismResult(models.Model):
    """
    Organism identified in a microbiology sample.
    """
    QUANTITY_CHOICES = [
        ('NONE', 'No Growth'),
        ('RARE', 'Rare'),
        ('FEW', 'Few'),
        ('MODERATE', 'Moderate'),
        ('MANY', 'Many'),
        ('HEAVY', 'Heavy Growth'),
        ('CFU_COUNT', 'CFU Count'),
    ]

    IDENTIFICATION_METHOD_CHOICES = [
        ('MALDI-TOF', 'MALDI-TOF MS'),
        ('BIOCHEMICAL', 'Biochemical Tests'),
        ('VITEK', 'VITEK'),
        ('API', 'API System'),
        ('PCR', 'PCR'),
        ('SEQUENCING', 'Sequencing'),
        ('MORPHOLOGY', 'Morphology'),
        ('OTHER', 'Other'),
    ]

    result_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique result identifier"
    )

    sample = models.ForeignKey(
        MicrobiologySample,
        on_delete=models.CASCADE,
        related_name='organism_results'
    )
    organism = models.ForeignKey(
        'microbiology.Organism',
        on_delete=models.PROTECT,
        related_name='results'
    )

    # Identification
    identification_method = models.CharField(
        max_length=20,
        choices=IDENTIFICATION_METHOD_CHOICES,
        default='MALDI-TOF'
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Identification confidence score"
    )
    identification_datetime = models.DateTimeField(null=True, blank=True)

    # Quantity
    quantity = models.CharField(max_length=20, choices=QUANTITY_CHOICES, default='MODERATE')
    cfu_count = models.PositiveIntegerField(null=True, blank=True, help_text="Colony forming units per mL")
    colony_description = models.CharField(max_length=200, blank=True)

    # Clinical significance
    is_significant = models.BooleanField(default=True, help_text="Clinically significant isolate")
    is_contaminant = models.BooleanField(default=False)
    requires_ast = models.BooleanField(default=True)

    # Sequencing data
    sequence_number = models.PositiveSmallIntegerField(default=1, help_text="Isolate sequence number")

    # AST panel
    ast_panel = models.ForeignKey(
        'microbiology.ASTPanel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organism_results'
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    identified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='identified_organisms'
    )

    class Meta:
        verbose_name = "Organism Result"
        verbose_name_plural = "Organism Results"
        ordering = ['sample', 'sequence_number']

    def save(self, *args, **kwargs):
        if not self.result_id:
            self.result_id = self._generate_result_id()
        super().save(*args, **kwargs)

    def _generate_result_id(self):
        """Generate unique result ID with format: ISO-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"ISO-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.sample.sample_id} - {self.organism}"


class ASTResult(models.Model):
    """
    Individual AST result for an antibiotic tested against an organism isolate.
    """
    INTERPRETATION_CHOICES = [
        ('S', 'Susceptible'),
        ('I', 'Intermediate'),
        ('R', 'Resistant'),
        ('SDD', 'Susceptible-Dose Dependent'),
        ('NS', 'Non-Susceptible'),
        ('NI', 'No Interpretation'),
    ]

    TEST_METHOD_CHOICES = [
        ('MIC', 'MIC'),
        ('DISK', 'Disk Diffusion'),
        ('ETEST', 'E-Test'),
        ('GRADIENT', 'Gradient Strip'),
        ('AUTOMATED', 'Automated System'),
    ]

    organism_result = models.ForeignKey(
        OrganismResult,
        on_delete=models.CASCADE,
        related_name='ast_results'
    )
    antibiotic = models.ForeignKey(
        'microbiology.Antibiotic',
        on_delete=models.PROTECT,
        related_name='ast_results'
    )

    # Testing details
    test_method = models.CharField(max_length=20, choices=TEST_METHOD_CHOICES, default='MIC')
    raw_value = models.CharField(max_length=20, help_text="Raw MIC or zone diameter value")
    mic_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MIC in mg/L"
    )
    zone_diameter = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Zone diameter in mm"
    )

    # Interpretation
    interpretation = models.CharField(max_length=5, choices=INTERPRETATION_CHOICES)
    interpretation_guideline = models.ForeignKey(
        'microbiology.ASTGuideline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ast_results'
    )
    breakpoint_used = models.ForeignKey(
        'microbiology.Breakpoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ast_results'
    )

    # Override
    is_manual_override = models.BooleanField(default=False)
    original_interpretation = models.CharField(max_length=5, blank=True)
    override_reason = models.TextField(blank=True)

    # Reporting
    is_reported = models.BooleanField(default=True)
    report_comment = models.CharField(max_length=200, blank=True)

    # Timestamps
    tested_datetime = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tested_ast_results'
    )

    class Meta:
        verbose_name = "AST Result"
        verbose_name_plural = "AST Results"
        ordering = ['organism_result', 'antibiotic']
        unique_together = [['organism_result', 'antibiotic', 'test_method']]

    def __str__(self):
        return f"{self.organism_result} - {self.antibiotic.abbreviation}: {self.interpretation}"

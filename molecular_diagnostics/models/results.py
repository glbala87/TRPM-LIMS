# molecular_diagnostics/models/results.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class MolecularResult(models.Model):
    """Master result record for a molecular test"""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PRELIMINARY', 'Preliminary'),
        ('FINAL', 'Final'),
        ('AMENDED', 'Amended'),
        ('CANCELLED', 'Cancelled'),
    ]

    INTERPRETATION_CHOICES = [
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('INDETERMINATE', 'Indeterminate'),
        ('NOT_TESTED', 'Not Tested'),
        ('INCONCLUSIVE', 'Inconclusive'),
    ]

    sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.CASCADE,
        related_name='results'
    )
    test_panel = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.PROTECT,
        related_name='results'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    interpretation = models.CharField(
        max_length=20,
        choices=INTERPRETATION_CHOICES,
        blank=True
    )

    result_summary = models.TextField(
        blank=True,
        help_text="Summary of test results"
    )
    clinical_significance = models.TextField(
        blank=True,
        help_text="Clinical interpretation and significance"
    )
    recommendations = models.TextField(
        blank=True,
        help_text="Follow-up recommendations"
    )
    limitations = models.TextField(
        blank=True,
        help_text="Test limitations and disclaimers"
    )

    # Approval workflow
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_results'
    )
    performed_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_results'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_results'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Report generation
    report_generated = models.BooleanField(default=False)
    report_generated_at = models.DateTimeField(null=True, blank=True)
    report_file = models.FileField(
        upload_to='molecular_reports/%Y/%m/',
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Molecular Result"
        verbose_name_plural = "Molecular Results"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sample.sample_id} - {self.test_panel.code}: {self.get_status_display()}"

    @property
    def is_reportable(self):
        return self.status in ['FINAL', 'AMENDED']

    def approve(self, user):
        """Approve the result"""
        self.approved_by = user
        self.approved_at = timezone.now()
        self.status = 'FINAL'
        self.save()


class PCRResult(models.Model):
    """Detailed PCR results for individual targets"""

    DETECTION_CHOICES = [
        ('DETECTED', 'Detected'),
        ('NOT_DETECTED', 'Not Detected'),
        ('INDETERMINATE', 'Indeterminate'),
    ]

    molecular_result = models.ForeignKey(
        MolecularResult,
        on_delete=models.CASCADE,
        related_name='pcr_results'
    )
    target_gene = models.ForeignKey(
        'molecular_diagnostics.GeneTarget',
        on_delete=models.PROTECT,
        related_name='pcr_results'
    )

    ct_value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cycle threshold value"
    )
    is_detected = models.CharField(
        max_length=20,
        choices=DETECTION_CHOICES,
        blank=True
    )

    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Quantified value (copies/mL, IU/mL, etc.)"
    )
    quantity_unit = models.CharField(max_length=50, blank=True)

    fluorescence_channel = models.CharField(max_length=50, blank=True)
    amplification_curve = models.JSONField(
        default=dict,
        blank=True,
        help_text="Amplification curve data points"
    )

    replicate_number = models.PositiveIntegerField(default=1)
    well_position = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "PCR Result"
        verbose_name_plural = "PCR Results"
        ordering = ['molecular_result', 'target_gene']

    def __str__(self):
        ct = f"Ct={self.ct_value}" if self.ct_value else "Ct=N/A"
        return f"{self.target_gene.symbol}: {self.get_is_detected_display()} ({ct})"

    def save(self, *args, **kwargs):
        # Auto-determine detection based on Ct value
        if self.ct_value is not None and not self.is_detected:
            # Typical Ct cutoff of 40 for positive detection
            if self.ct_value <= 40:
                self.is_detected = 'DETECTED'
            else:
                self.is_detected = 'NOT_DETECTED'
        super().save(*args, **kwargs)


class SequencingResult(models.Model):
    """NGS/Sanger sequencing quality metrics and summary"""

    molecular_result = models.OneToOneField(
        MolecularResult,
        on_delete=models.CASCADE,
        related_name='sequencing_result'
    )

    # NGS metrics
    total_reads = models.BigIntegerField(null=True, blank=True)
    mapped_reads = models.BigIntegerField(null=True, blank=True)
    mean_coverage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    coverage_uniformity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of target covered at minimum depth"
    )

    quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Mean quality score (Phred)"
    )
    q30_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of bases >= Q30"
    )

    on_target_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    duplicate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Sanger-specific
    trace_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    sequence_length = models.PositiveIntegerField(null=True, blank=True)

    run_file = models.FileField(
        upload_to='sequencing_data/%Y/%m/',
        null=True,
        blank=True,
        help_text="Raw data file (FASTQ, BAM, etc.)"
    )

    class Meta:
        verbose_name = "Sequencing Result"
        verbose_name_plural = "Sequencing Results"

    def __str__(self):
        return f"Sequencing: {self.molecular_result.sample.sample_id}"

    @property
    def mapping_rate(self):
        if self.total_reads and self.mapped_reads:
            return (self.mapped_reads / self.total_reads) * 100
        return None


class VariantCall(models.Model):
    """Individual variant calls from sequencing"""

    CLASSIFICATION_CHOICES = [
        ('PATHOGENIC', 'Pathogenic'),
        ('LIKELY_PATHOGENIC', 'Likely Pathogenic'),
        ('VUS', 'Variant of Uncertain Significance'),
        ('LIKELY_BENIGN', 'Likely Benign'),
        ('BENIGN', 'Benign'),
    ]

    ZYGOSITY_CHOICES = [
        ('HETEROZYGOUS', 'Heterozygous'),
        ('HOMOZYGOUS', 'Homozygous'),
        ('HEMIZYGOUS', 'Hemizygous'),
    ]

    molecular_result = models.ForeignKey(
        MolecularResult,
        on_delete=models.CASCADE,
        related_name='variant_calls'
    )

    gene = models.ForeignKey(
        'molecular_diagnostics.GeneTarget',
        on_delete=models.PROTECT,
        related_name='variants'
    )

    chromosome = models.CharField(max_length=10)
    position = models.BigIntegerField()
    ref_allele = models.CharField(max_length=500)
    alt_allele = models.CharField(max_length=500)

    # HGVS notation
    hgvs_c = models.CharField(
        max_length=200,
        blank=True,
        help_text="cDNA notation (e.g., c.1234A>G)"
    )
    hgvs_p = models.CharField(
        max_length=200,
        blank=True,
        help_text="Protein notation (e.g., p.Arg123Gly)"
    )

    variant_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="SNV, Insertion, Deletion, etc."
    )
    consequence = models.CharField(
        max_length=100,
        blank=True,
        help_text="Functional consequence (missense, frameshift, etc.)"
    )

    classification = models.CharField(
        max_length=20,
        choices=CLASSIFICATION_CHOICES,
        blank=True
    )
    zygosity = models.CharField(
        max_length=20,
        choices=ZYGOSITY_CHOICES,
        blank=True
    )

    allele_frequency = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Variant allele frequency in sample"
    )
    read_depth = models.PositiveIntegerField(null=True, blank=True)

    # External database references
    dbsnp_id = models.CharField(max_length=50, blank=True)
    clinvar_id = models.CharField(max_length=50, blank=True)
    cosmic_id = models.CharField(max_length=50, blank=True)

    population_frequency = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Population allele frequency (gnomAD, etc.)"
    )

    is_reportable = models.BooleanField(
        default=True,
        help_text="Include in clinical report"
    )
    interpretation = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Variant Call"
        verbose_name_plural = "Variant Calls"
        ordering = ['chromosome', 'position']

    def __str__(self):
        return f"{self.gene.symbol}:{self.hgvs_c or f'{self.ref_allele}>{self.alt_allele}'}"

    @property
    def is_clinically_significant(self):
        return self.classification in ['PATHOGENIC', 'LIKELY_PATHOGENIC']

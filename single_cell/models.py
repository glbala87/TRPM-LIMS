# single_cell/models.py
"""
Single-cell genomics support models.
Inspired by miso-lims single-cell sample tracking.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class SingleCellSampleType(models.Model):
    """Types of single-cell samples."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    target_cell_count = models.PositiveIntegerField(null=True, blank=True)
    min_viability = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Single-Cell Sample Type"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class SingleCellSample(models.Model):
    """Single-cell sample with cell concentration tracking."""

    PROCESSING_STATUS_CHOICES = [
        ('RECEIVED', 'Received'), ('DISSOCIATED', 'Dissociated'),
        ('SORTED', 'Cell Sorted'), ('LOADED', 'Loaded on Chip'),
        ('CAPTURED', 'Cells Captured'), ('LYSED', 'Lysed'),
        ('LIBRARY_PREP', 'Library Preparation'), ('SEQUENCED', 'Sequenced'),
        ('ANALYZED', 'Analyzed'), ('FAILED', 'Failed'),
    ]

    PLATFORM_CHOICES = [
        ('10X_3PRIME', "10x Genomics 3' GEX"), ('10X_5PRIME', "10x Genomics 5' GEX"),
        ('10X_MULTIOME', "10x Multiome"), ('10X_VISIUM', "10x Visium"),
        ('SMART_SEQ2', 'Smart-seq2'), ('SMART_SEQ3', 'Smart-seq3'),
        ('DROP_SEQ', 'Drop-seq'), ('BD_RHAPSODY', 'BD Rhapsody'),
        ('PARSE', 'Parse Biosciences'), ('OTHER', 'Other'),
    ]

    sample_id = models.CharField(max_length=50, unique=True)
    molecular_sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample', on_delete=models.CASCADE,
        related_name='single_cell_samples'
    )
    sample_type = models.ForeignKey(SingleCellSampleType, on_delete=models.PROTECT)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='10X_3PRIME')
    status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='RECEIVED')

    # Cell metrics
    initial_cell_count = models.PositiveIntegerField(null=True, blank=True)
    cell_concentration = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    viability_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    target_cell_recovery = models.PositiveIntegerField(null=True, blank=True)
    actual_cell_recovery = models.PositiveIntegerField(null=True, blank=True)
    is_nuclei = models.BooleanField(default=False)
    nuclei_concentration = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Capture info
    chip_id = models.CharField(max_length=50, blank=True)
    chip_position = models.CharField(max_length=10, blank=True)
    capture_time = models.DateTimeField(null=True, blank=True)

    # Quality metrics
    mean_reads_per_cell = models.PositiveIntegerField(null=True, blank=True)
    median_genes_per_cell = models.PositiveIntegerField(null=True, blank=True)
    median_umi_per_cell = models.PositiveIntegerField(null=True, blank=True)
    sequencing_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Single-Cell Sample"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sample_id} ({self.get_platform_display()})"


class FeatureBarcode(models.Model):
    """Feature barcodes for CITE-seq, cell hashing, etc."""

    FEATURE_TYPE_CHOICES = [
        ('ANTIBODY', 'Antibody'), ('HASHTAG', 'Cell Hashtag'),
        ('CRISPR', 'CRISPR Guide'), ('CUSTOM', 'Custom'),
    ]

    name = models.CharField(max_length=100)
    barcode_sequence = models.CharField(max_length=50)
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES, default='ANTIBODY')
    target_antigen = models.CharField(max_length=100, blank=True)
    clone = models.CharField(max_length=50, blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    catalog_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['name', 'barcode_sequence']]

    def __str__(self):
        return f"{self.name} ({self.get_feature_type_display()})"


class FeatureBarcodePanel(models.Model):
    """Panel of feature barcodes."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    feature_barcodes = models.ManyToManyField(FeatureBarcode, related_name='panels')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SingleCellLibrary(models.Model):
    """Single-cell library linking to NGS library."""

    LIBRARY_TYPE_CHOICES = [
        ('GEX', 'Gene Expression'), ('VDJ_T', 'V(D)J T-cell'),
        ('VDJ_B', 'V(D)J B-cell'), ('ATAC', 'ATAC-seq'),
        ('FEATURE', 'Feature Barcode'), ('CUSTOM', 'Custom'),
    ]

    single_cell_sample = models.ForeignKey(SingleCellSample, on_delete=models.CASCADE, related_name='libraries')
    ngs_library = models.ForeignKey('molecular_diagnostics.NGSLibrary', on_delete=models.CASCADE)
    library_type = models.CharField(max_length=20, choices=LIBRARY_TYPE_CHOICES, default='GEX')
    feature_barcode_panel = models.ForeignKey(FeatureBarcodePanel, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_cells = models.PositiveIntegerField(null=True, blank=True)
    fraction_reads_in_cells = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.single_cell_sample.sample_id} - {self.get_library_type_display()}"


class CellCluster(models.Model):
    """Cell cluster identified in analysis."""
    single_cell_sample = models.ForeignKey(SingleCellSample, on_delete=models.CASCADE, related_name='clusters')
    cluster_id = models.CharField(max_length=50)
    cluster_name = models.CharField(max_length=100, blank=True)
    cell_count = models.PositiveIntegerField()
    cell_type = models.CharField(max_length=100, blank=True)
    markers = models.JSONField(default=list)
    mean_genes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mean_umi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = [['single_cell_sample', 'cluster_id']]

    def __str__(self):
        return f"{self.cluster_id}: {self.cell_type or 'Unannotated'}"

# molecular_diagnostics/models/tests.py

from django.db import models


class GeneTarget(models.Model):
    """Gene or genetic region targeted by molecular tests"""

    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official gene symbol (e.g., BRCA1, TP53)"
    )
    chromosome = models.CharField(max_length=10, blank=True)
    genomic_coordinates = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., chr17:43044295-43170245"
    )
    transcript_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Reference transcript (e.g., NM_007294.4)"
    )
    description = models.TextField(blank=True)
    clinical_significance = models.TextField(
        blank=True,
        help_text="Clinical relevance of this gene"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gene Target"
        verbose_name_plural = "Gene Targets"
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class MolecularTestPanel(models.Model):
    """Test panels for molecular diagnostics"""

    TEST_TYPE_CHOICES = [
        ('PCR', 'PCR'),
        ('RT_PCR', 'Real-time PCR'),
        ('NGS', 'Next-Generation Sequencing'),
        ('SANGER', 'Sanger Sequencing'),
        ('FISH', 'Fluorescence In Situ Hybridization'),
        ('MICROARRAY', 'Microarray'),
        ('MLPA', 'MLPA'),
        ('FRAGMENT', 'Fragment Analysis'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    description = models.TextField(blank=True)

    gene_targets = models.ManyToManyField(
        GeneTarget,
        related_name='test_panels',
        blank=True
    )

    methodology = models.TextField(
        blank=True,
        help_text="Detailed methodology description"
    )
    sample_requirements = models.TextField(
        blank=True,
        help_text="Required sample types, volume, and conditions"
    )

    tat_hours = models.PositiveIntegerField(
        help_text="Target turnaround time in hours (SLA)"
    )

    reagent_kits = models.ManyToManyField(
        'reagents.MolecularReagent',
        related_name='test_panels',
        blank=True
    )

    min_concentration_ng_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum DNA/RNA concentration required"
    )
    min_volume_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum sample volume required"
    )

    requires_extraction = models.BooleanField(
        default=True,
        help_text="Does this test require DNA/RNA extraction?"
    )

    workflow = models.ForeignKey(
        'molecular_diagnostics.WorkflowDefinition',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_panels'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Molecular Test Panel"
        verbose_name_plural = "Molecular Test Panels"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_test_type_display()})"

    @property
    def gene_count(self):
        return self.gene_targets.count()

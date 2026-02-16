# molecular_diagnostics/models/annotations.py
"""
Variant annotation models for ClinVar and gnomAD integration.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class AnnotationCache(models.Model):
    """
    Global cache for variant annotations to reduce API calls.
    Stores normalized variant data that can be reused across samples.
    """

    # Normalized variant key (e.g., "chr1-12345-A-G" or "rs12345")
    variant_key = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Normalized variant identifier (chr-pos-ref-alt or rsID)"
    )

    # Alternate keys for lookup
    hgvs_notation = models.CharField(
        max_length=300,
        blank=True,
        db_index=True,
        help_text="HGVS notation for variant lookup"
    )
    dbsnp_id = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="dbSNP rsID"
    )

    # ClinVar cached data
    clinvar_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cached ClinVar annotation data"
    )
    clinvar_fetched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When ClinVar data was last fetched"
    )

    # gnomAD cached data
    gnomad_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cached gnomAD annotation data"
    )
    gnomad_fetched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When gnomAD data was last fetched"
    )

    # Analytics
    hit_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this cache entry was used"
    )
    last_hit_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this cache entry was accessed"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Annotation Cache"
        verbose_name_plural = "Annotation Cache Entries"
        ordering = ['-hit_count', '-updated_at']

    def __str__(self):
        return f"Cache: {self.variant_key}"

    def record_hit(self):
        """Record a cache hit."""
        self.hit_count += 1
        self.last_hit_at = timezone.now()
        self.save(update_fields=['hit_count', 'last_hit_at'])

    @property
    def clinvar_expired(self):
        """Check if ClinVar data needs refresh."""
        if not self.clinvar_fetched_at:
            return True
        ttl_days = getattr(settings, 'ANNOTATION_CACHE_TTL_DAYS', 30)
        expiry = self.clinvar_fetched_at + timezone.timedelta(days=ttl_days)
        return timezone.now() > expiry

    @property
    def gnomad_expired(self):
        """Check if gnomAD data needs refresh."""
        if not self.gnomad_fetched_at:
            return True
        ttl_days = getattr(settings, 'ANNOTATION_CACHE_TTL_DAYS', 30)
        expiry = self.gnomad_fetched_at + timezone.timedelta(days=ttl_days)
        return timezone.now() > expiry

    @classmethod
    def get_or_create_for_variant(cls, chromosome, position, ref, alt):
        """Get or create a cache entry for a variant."""
        variant_key = f"{chromosome}-{position}-{ref}-{alt}"
        cache_entry, created = cls.objects.get_or_create(
            variant_key=variant_key,
            defaults={}
        )
        return cache_entry, created


class VariantAnnotation(models.Model):
    """
    Detailed annotations for a variant call, including ClinVar and gnomAD data.
    OneToOne relationship with VariantCall.
    """

    ANNOTATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PARTIAL', 'Partial'),  # Some annotations failed
        ('FAILED', 'Failed'),
        ('NOT_FOUND', 'Not Found'),  # Variant not in databases
    ]

    CLINICAL_SIGNIFICANCE_CHOICES = [
        ('PATHOGENIC', 'Pathogenic'),
        ('LIKELY_PATHOGENIC', 'Likely pathogenic'),
        ('UNCERTAIN_SIGNIFICANCE', 'Uncertain significance'),
        ('LIKELY_BENIGN', 'Likely benign'),
        ('BENIGN', 'Benign'),
        ('CONFLICTING', 'Conflicting interpretations'),
        ('NOT_PROVIDED', 'Not provided'),
        ('DRUG_RESPONSE', 'Drug response'),
        ('RISK_FACTOR', 'Risk factor'),
        ('ASSOCIATION', 'Association'),
        ('PROTECTIVE', 'Protective'),
    ]

    REVIEW_STATUS_CHOICES = [
        ('PRACTICE_GUIDELINE', 'practice guideline'),
        ('EXPERT_PANEL', 'reviewed by expert panel'),
        ('MULTIPLE_SUBMITTERS', 'criteria provided, multiple submitters, no conflicts'),
        ('SINGLE_SUBMITTER', 'criteria provided, single submitter'),
        ('CONFLICTING', 'criteria provided, conflicting interpretations'),
        ('NO_ASSERTION', 'no assertion criteria provided'),
        ('NO_CLASSIFICATION', 'no classification provided'),
    ]

    # Link to VariantCall
    variant_call = models.OneToOneField(
        'molecular_diagnostics.VariantCall',
        on_delete=models.CASCADE,
        related_name='annotation'
    )

    # Link to cache for efficient lookups
    cache_entry = models.ForeignKey(
        AnnotationCache,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='annotations'
    )

    # Status tracking
    annotation_status = models.CharField(
        max_length=20,
        choices=ANNOTATION_STATUS_CHOICES,
        default='PENDING'
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if annotation failed"
    )

    # ===================
    # ClinVar Fields
    # ===================
    clinvar_variation_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="ClinVar Variation ID"
    )
    clinvar_allele_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="ClinVar Allele ID"
    )

    clinical_significance = models.CharField(
        max_length=50,
        choices=CLINICAL_SIGNIFICANCE_CHOICES,
        blank=True,
        help_text="ClinVar clinical significance"
    )
    clinical_significance_raw = models.CharField(
        max_length=500,
        blank=True,
        help_text="Raw clinical significance from ClinVar"
    )

    review_status = models.CharField(
        max_length=100,
        choices=REVIEW_STATUS_CHOICES,
        blank=True,
        help_text="ClinVar review status"
    )
    review_status_stars = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="ClinVar review status star rating (0-4)"
    )

    # ClinVar condition/disease associations
    conditions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of associated conditions/diseases"
    )
    # Example: [{"name": "Breast cancer", "medgen_id": "CN123", "trait_type": "Disease"}]

    # ClinVar submitters and assertions
    submitters = models.JSONField(
        default=list,
        blank=True,
        help_text="List of ClinVar submitters and their assertions"
    )
    # Example: [{"name": "Lab A", "significance": "Pathogenic", "date": "2023-01-01"}]

    submission_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of ClinVar submissions"
    )

    last_evaluated = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last ClinVar evaluation"
    )

    clinvar_fetched_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ===================
    # gnomAD Fields
    # ===================

    # Allele frequencies
    genome_af = models.DecimalField(
        max_digits=12,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="gnomAD genome allele frequency (overall)"
    )
    exome_af = models.DecimalField(
        max_digits=12,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="gnomAD exome allele frequency (overall)"
    )

    # Allele counts
    genome_ac = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="gnomAD genome allele count"
    )
    genome_an = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="gnomAD genome allele number"
    )
    exome_ac = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="gnomAD exome allele count"
    )
    exome_an = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="gnomAD exome allele number"
    )

    # Homozygote counts
    genome_homozygotes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of homozygotes in gnomAD genomes"
    )
    exome_homozygotes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of homozygotes in gnomAD exomes"
    )

    # Population-specific frequencies
    populations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Population-specific allele frequencies"
    )
    # Example: {"afr": 0.001, "amr": 0.002, "asj": 0.0, "eas": 0.005, "fin": 0.001, "nfe": 0.003, "sas": 0.002}

    # Highest population frequency (for filtering)
    max_population_af = models.DecimalField(
        max_digits=12,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="Maximum allele frequency across populations"
    )
    max_population = models.CharField(
        max_length=50,
        blank=True,
        help_text="Population with maximum allele frequency"
    )

    # gnomAD flags and quality metrics
    flags = models.JSONField(
        default=list,
        blank=True,
        help_text="gnomAD quality flags"
    )
    # Example: ["lcr", "segdup"]

    # Gene constraint metrics (from gnomAD)
    gene_constraint = models.JSONField(
        default=dict,
        blank=True,
        help_text="Gene constraint metrics (pLI, LOEUF, etc.)"
    )
    # Example: {"pLI": 0.99, "loeuf": 0.15, "missense_z": 3.5}

    gnomad_fetched_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ===================
    # Additional Fields
    # ===================

    # In-silico predictions (can be populated from various sources)
    in_silico_predictions = models.JSONField(
        default=dict,
        blank=True,
        help_text="In-silico prediction scores (SIFT, PolyPhen, CADD, etc.)"
    )
    # Example: {"sift": {"score": 0.01, "prediction": "deleterious"}, "polyphen": {"score": 0.95, "prediction": "probably_damaging"}}

    # Literature references
    pubmed_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Associated PubMed IDs"
    )

    # Audit fields
    annotated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='annotations_created'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variant Annotation"
        verbose_name_plural = "Variant Annotations"
        ordering = ['-updated_at']

    def __str__(self):
        vc = self.variant_call
        return f"Annotation: {vc.gene.symbol}:{vc.hgvs_c or 'variant'}"

    @property
    def is_complete(self):
        """Check if annotation is complete with both sources."""
        return (
            self.annotation_status == 'COMPLETED' and
            self.clinvar_fetched_at and
            self.gnomad_fetched_at
        )

    @property
    def combined_frequency(self):
        """Get the best available population frequency."""
        # Prefer genome frequency, fall back to exome
        if self.genome_af is not None:
            return self.genome_af
        return self.exome_af

    @property
    def is_rare(self):
        """Check if variant is rare (<1% in all populations)."""
        if self.max_population_af is not None:
            return self.max_population_af < 0.01
        return None

    @property
    def significance_level(self):
        """
        Return a numeric level for clinical significance for sorting.
        Higher = more clinically significant.
        """
        levels = {
            'PATHOGENIC': 5,
            'LIKELY_PATHOGENIC': 4,
            'UNCERTAIN_SIGNIFICANCE': 3,
            'LIKELY_BENIGN': 2,
            'BENIGN': 1,
            'NOT_PROVIDED': 0,
        }
        return levels.get(self.clinical_significance, 0)

    def update_from_clinvar(self, clinvar_data):
        """Update annotation with ClinVar data."""
        if not clinvar_data:
            return

        self.clinvar_variation_id = clinvar_data.get('variation_id', '')
        self.clinvar_allele_id = clinvar_data.get('allele_id', '')
        self.clinical_significance_raw = clinvar_data.get('clinical_significance', '')

        # Normalize clinical significance
        sig_lower = self.clinical_significance_raw.lower()
        if 'pathogenic' in sig_lower and 'likely' in sig_lower:
            self.clinical_significance = 'LIKELY_PATHOGENIC'
        elif 'pathogenic' in sig_lower:
            self.clinical_significance = 'PATHOGENIC'
        elif 'benign' in sig_lower and 'likely' in sig_lower:
            self.clinical_significance = 'LIKELY_BENIGN'
        elif 'benign' in sig_lower:
            self.clinical_significance = 'BENIGN'
        elif 'uncertain' in sig_lower:
            self.clinical_significance = 'UNCERTAIN_SIGNIFICANCE'
        elif 'conflicting' in sig_lower:
            self.clinical_significance = 'CONFLICTING'
        elif 'drug' in sig_lower:
            self.clinical_significance = 'DRUG_RESPONSE'
        elif 'risk' in sig_lower:
            self.clinical_significance = 'RISK_FACTOR'
        else:
            self.clinical_significance = 'NOT_PROVIDED'

        self.review_status = clinvar_data.get('review_status', '')
        self.review_status_stars = clinvar_data.get('review_stars')
        self.conditions = clinvar_data.get('conditions', [])
        self.submitters = clinvar_data.get('submitters', [])
        self.submission_count = clinvar_data.get('submission_count')
        self.pubmed_ids = clinvar_data.get('pubmed_ids', [])

        if clinvar_data.get('last_evaluated'):
            try:
                from datetime import datetime
                self.last_evaluated = datetime.strptime(
                    clinvar_data['last_evaluated'], '%Y-%m-%d'
                ).date()
            except (ValueError, TypeError):
                pass

        self.clinvar_fetched_at = timezone.now()

    def update_from_gnomad(self, gnomad_data):
        """Update annotation with gnomAD data."""
        if not gnomad_data:
            return

        # Genome data
        genome = gnomad_data.get('genome', {})
        self.genome_af = genome.get('af')
        self.genome_ac = genome.get('ac')
        self.genome_an = genome.get('an')
        self.genome_homozygotes = genome.get('homozygotes')

        # Exome data
        exome = gnomad_data.get('exome', {})
        self.exome_af = exome.get('af')
        self.exome_ac = exome.get('ac')
        self.exome_an = exome.get('an')
        self.exome_homozygotes = exome.get('homozygotes')

        # Population frequencies
        self.populations = gnomad_data.get('populations', {})

        # Find max population frequency
        if self.populations:
            max_pop = max(self.populations.items(), key=lambda x: x[1] or 0)
            self.max_population = max_pop[0]
            self.max_population_af = max_pop[1]

        # Flags
        self.flags = gnomad_data.get('flags', [])

        # Gene constraint
        self.gene_constraint = gnomad_data.get('gene_constraint', {})

        self.gnomad_fetched_at = timezone.now()

        # Also update the VariantCall population_frequency field
        if self.genome_af is not None:
            self.variant_call.population_frequency = self.genome_af
            self.variant_call.save(update_fields=['population_frequency'])
        elif self.exome_af is not None:
            self.variant_call.population_frequency = self.exome_af
            self.variant_call.save(update_fields=['population_frequency'])

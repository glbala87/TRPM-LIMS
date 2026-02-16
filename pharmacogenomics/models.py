# pharmacogenomics/models.py
"""
Pharmacogenomics (PGx) models for drug-gene interaction analysis.

Includes:
- Gene and allele definitions
- Metabolizer phenotypes
- Drug-gene interactions
- CPIC-based dosing recommendations
- Patient PGx results
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class PGxGene(models.Model):
    """
    Pharmacogene definition with clinical relevance information.

    Examples: CYP2D6, CYP2C19, CYP2C9, CYP3A4, DPYD, TPMT, UGT1A1, SLCO1B1
    """

    GENE_CATEGORY_CHOICES = [
        ('CYP', 'Cytochrome P450'),
        ('TRANSPORTER', 'Drug Transporter'),
        ('PHASE2', 'Phase II Enzyme'),
        ('TARGET', 'Drug Target'),
        ('HLA', 'HLA Gene'),
        ('OTHER', 'Other'),
    ]

    symbol = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Gene symbol (e.g., CYP2D6)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Full gene name"
    )
    category = models.CharField(
        max_length=20,
        choices=GENE_CATEGORY_CHOICES,
        default='CYP'
    )

    # Reference information
    ensembl_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ensembl Gene ID"
    )
    ncbi_gene_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="NCBI Gene ID"
    )
    pharmvar_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="PharmVar Gene ID"
    )

    # Genomic location
    chromosome = models.CharField(max_length=10, blank=True)
    start_position = models.BigIntegerField(null=True, blank=True)
    end_position = models.BigIntegerField(null=True, blank=True)
    reference_sequence = models.CharField(
        max_length=50,
        blank=True,
        help_text="Reference sequence (e.g., NG_008376.4)"
    )

    # Clinical information
    description = models.TextField(
        blank=True,
        help_text="Gene function and PGx relevance"
    )
    clinical_importance = models.TextField(
        blank=True,
        help_text="Clinical significance notes"
    )

    # Diplotype calling settings
    uses_activity_score = models.BooleanField(
        default=True,
        help_text="Whether phenotype is determined by activity score"
    )
    copy_number_relevant = models.BooleanField(
        default=False,
        help_text="Whether gene duplications affect phenotype (e.g., CYP2D6)"
    )

    # Links to GeneTarget in molecular_diagnostics if needed
    gene_target = models.ForeignKey(
        'molecular_diagnostics.GeneTarget',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pgx_genes'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PGx Gene"
        verbose_name_plural = "PGx Genes"
        ordering = ['symbol']

    def __str__(self):
        return self.symbol


class StarAllele(models.Model):
    """
    Star allele definition for a pharmacogene.

    Examples: *1 (reference), *2, *3, *17, etc.
    """

    FUNCTION_CHOICES = [
        ('NORMAL', 'Normal Function'),
        ('INCREASED', 'Increased Function'),
        ('DECREASED', 'Decreased Function'),
        ('NO_FUNCTION', 'No Function'),
        ('UNCERTAIN', 'Uncertain Function'),
        ('UNKNOWN', 'Unknown'),
    ]

    gene = models.ForeignKey(
        PGxGene,
        on_delete=models.CASCADE,
        related_name='alleles'
    )
    name = models.CharField(
        max_length=50,
        help_text="Star allele name (e.g., *1, *2, *17)"
    )

    # Function and activity
    function = models.CharField(
        max_length=20,
        choices=FUNCTION_CHOICES,
        default='NORMAL'
    )
    activity_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Activity score (e.g., 0, 0.5, 1, 2)"
    )

    # Defining variants
    defining_variants = models.JSONField(
        default=list,
        blank=True,
        help_text="List of defining variants for this allele"
    )
    # Example: [{"rsid": "rs1234", "hgvs": "c.123A>G", "effect": "missense"}]

    # Reference information
    pharmvar_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="PharmVar Allele ID"
    )
    cpic_allele_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="CPIC Allele ID"
    )

    # Population frequencies
    population_frequencies = models.JSONField(
        default=dict,
        blank=True,
        help_text="Allele frequencies by population"
    )
    # Example: {"afr": 0.15, "eur": 0.22, "eas": 0.05}

    description = models.TextField(blank=True)
    clinical_significance = models.TextField(blank=True)

    is_reference = models.BooleanField(
        default=False,
        help_text="Is this the reference allele (*1)?"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Star Allele"
        verbose_name_plural = "Star Alleles"
        ordering = ['gene', 'name']
        unique_together = ['gene', 'name']

    def __str__(self):
        return f"{self.gene.symbol}{self.name}"


class Phenotype(models.Model):
    """
    Metabolizer/function phenotype definition.

    Examples: Poor Metabolizer (PM), Intermediate (IM), Normal (NM), Ultra-Rapid (UM)
    """

    PHENOTYPE_TYPE_CHOICES = [
        ('PM', 'Poor Metabolizer'),
        ('IM', 'Intermediate Metabolizer'),
        ('NM', 'Normal Metabolizer'),
        ('RM', 'Rapid Metabolizer'),
        ('UM', 'Ultrarapid Metabolizer'),
        ('INDETERMINATE', 'Indeterminate'),
        ('POSSIBLE_IM', 'Possible Intermediate Metabolizer'),
        ('LIKELY_PM', 'Likely Poor Metabolizer'),
        ('LIKELY_IM', 'Likely Intermediate Metabolizer'),
    ]

    gene = models.ForeignKey(
        PGxGene,
        on_delete=models.CASCADE,
        related_name='phenotypes'
    )
    code = models.CharField(
        max_length=20,
        choices=PHENOTYPE_TYPE_CHOICES,
        help_text="Phenotype code"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name"
    )

    # Activity score range for this phenotype
    activity_score_min = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum activity score for this phenotype"
    )
    activity_score_max = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum activity score for this phenotype"
    )

    # Example diplotypes that result in this phenotype
    example_diplotypes = models.JSONField(
        default=list,
        blank=True,
        help_text="Example diplotypes for this phenotype"
    )
    # Example: ["*1/*1", "*1/*2", "*2/*2"]

    description = models.TextField(blank=True)
    clinical_implications = models.TextField(
        blank=True,
        help_text="Clinical implications of this phenotype"
    )

    # Display order
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phenotype"
        verbose_name_plural = "Phenotypes"
        ordering = ['gene', 'sort_order', 'code']
        unique_together = ['gene', 'code']

    def __str__(self):
        return f"{self.gene.symbol}: {self.name}"


class Drug(models.Model):
    """
    Drug/medication with pharmacogenomic interactions.
    """

    DRUG_CLASS_CHOICES = [
        ('ANALGESIC', 'Analgesic'),
        ('ANTIDEPRESSANT', 'Antidepressant'),
        ('ANTICOAGULANT', 'Anticoagulant'),
        ('ANTIPSYCHOTIC', 'Antipsychotic'),
        ('CARDIOVASCULAR', 'Cardiovascular'),
        ('ONCOLOGY', 'Oncology'),
        ('IMMUNOSUPPRESSANT', 'Immunosuppressant'),
        ('ANTIPLATELET', 'Antiplatelet'),
        ('PPI', 'Proton Pump Inhibitor'),
        ('ANTIBIOTIC', 'Antibiotic'),
        ('ANTIVIRAL', 'Antiviral'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Generic drug name"
    )
    brand_names = models.JSONField(
        default=list,
        blank=True,
        help_text="List of brand names"
    )
    drug_class = models.CharField(
        max_length=50,
        choices=DRUG_CLASS_CHOICES,
        default='OTHER'
    )

    # Identifiers
    rxnorm_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="RxNorm Concept ID"
    )
    drugbank_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="DrugBank ID"
    )
    atc_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="ATC Code"
    )

    description = models.TextField(blank=True)
    mechanism_of_action = models.TextField(blank=True)

    # PGx relevance
    has_cpic_guideline = models.BooleanField(
        default=False,
        help_text="Has CPIC dosing guideline"
    )
    has_fda_label = models.BooleanField(
        default=False,
        help_text="Has PGx information in FDA label"
    )
    cpic_level = models.CharField(
        max_length=10,
        blank=True,
        help_text="CPIC evidence level (A, B, C, D)"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Drug"
        verbose_name_plural = "Drugs"
        ordering = ['name']

    def __str__(self):
        return self.name


class DrugGeneInteraction(models.Model):
    """
    Drug-gene interaction pair defining PGx relationship.
    """

    EVIDENCE_LEVEL_CHOICES = [
        ('1A', '1A - Strong'),
        ('1B', '1B - Moderate'),
        ('2A', '2A - Weak'),
        ('2B', '2B - Very Weak'),
        ('3', '3 - Annotation'),
        ('4', '4 - Insufficient'),
    ]

    INTERACTION_TYPE_CHOICES = [
        ('PK', 'Pharmacokinetic'),
        ('PD', 'Pharmacodynamic'),
        ('ADR', 'Adverse Drug Reaction'),
        ('EFFICACY', 'Efficacy'),
        ('DOSING', 'Dosing'),
    ]

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='gene_interactions'
    )
    gene = models.ForeignKey(
        PGxGene,
        on_delete=models.CASCADE,
        related_name='drug_interactions'
    )

    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPE_CHOICES,
        default='PK'
    )
    evidence_level = models.CharField(
        max_length=10,
        choices=EVIDENCE_LEVEL_CHOICES,
        blank=True
    )

    # CPIC information
    cpic_guideline_url = models.URLField(blank=True)
    cpic_publication_pmid = models.CharField(
        max_length=50,
        blank=True,
        help_text="PMID for CPIC guideline publication"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the drug-gene interaction"
    )
    clinical_summary = models.TextField(
        blank=True,
        help_text="Clinical summary of interaction"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Drug-Gene Interaction"
        verbose_name_plural = "Drug-Gene Interactions"
        unique_together = ['drug', 'gene']
        ordering = ['drug', 'gene']

    def __str__(self):
        return f"{self.drug.name} - {self.gene.symbol}"


class DrugRecommendation(models.Model):
    """
    Drug dosing recommendation based on phenotype.

    Based on CPIC guidelines.
    """

    RECOMMENDATION_STRENGTH_CHOICES = [
        ('STRONG', 'Strong'),
        ('MODERATE', 'Moderate'),
        ('OPTIONAL', 'Optional'),
    ]

    ACTION_CHOICES = [
        ('STANDARD', 'Use standard dose'),
        ('REDUCE', 'Reduce dose'),
        ('INCREASE', 'Increase dose'),
        ('AVOID', 'Avoid drug'),
        ('ALTERNATIVE', 'Use alternative drug'),
        ('MONITOR', 'Enhanced monitoring'),
        ('CAUTION', 'Use with caution'),
    ]

    interaction = models.ForeignKey(
        DrugGeneInteraction,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    phenotype = models.ForeignKey(
        Phenotype,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )

    # Recommendation
    recommendation_strength = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_STRENGTH_CHOICES,
        default='STRONG'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default='STANDARD'
    )

    # Detailed guidance
    recommendation_text = models.TextField(
        help_text="Full recommendation text"
    )
    dosing_guidance = models.TextField(
        blank=True,
        help_text="Specific dosing guidance"
    )
    alternative_drugs = models.JSONField(
        default=list,
        blank=True,
        help_text="List of alternative drug options"
    )

    # Clinical context
    clinical_context = models.TextField(
        blank=True,
        help_text="Clinical context and considerations"
    )
    monitoring_recommendations = models.TextField(
        blank=True,
        help_text="Monitoring recommendations"
    )

    # References
    reference_pmids = models.JSONField(
        default=list,
        blank=True,
        help_text="PubMed IDs for supporting references"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Drug Recommendation"
        verbose_name_plural = "Drug Recommendations"
        unique_together = ['interaction', 'phenotype']
        ordering = ['interaction__drug__name', 'phenotype__gene__symbol']

    def __str__(self):
        return f"{self.interaction.drug.name} / {self.phenotype}: {self.action}"


class PGxPanel(models.Model):
    """
    PGx testing panel linking genes to a molecular test panel.
    """

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    # Genes included in this panel
    genes = models.ManyToManyField(
        PGxGene,
        related_name='panels'
    )

    # Link to molecular test panel
    molecular_panel = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pgx_panels'
    )

    # Coverage information
    target_regions = models.JSONField(
        default=list,
        blank=True,
        help_text="Target regions covered by panel"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PGx Panel"
        verbose_name_plural = "PGx Panels"
        ordering = ['name']

    def __str__(self):
        return f"{self.code}: {self.name}"


class PGxResult(models.Model):
    """
    Patient PGx result with diplotype, phenotype, and recommendations.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CALLING', 'Diplotype Calling'),
        ('CALLED', 'Called'),
        ('REVIEWED', 'Reviewed'),
        ('REPORTED', 'Reported'),
        ('FAILED', 'Failed'),
    ]

    # Link to molecular result
    molecular_result = models.ForeignKey(
        'molecular_diagnostics.MolecularResult',
        on_delete=models.CASCADE,
        related_name='pgx_results'
    )
    gene = models.ForeignKey(
        PGxGene,
        on_delete=models.PROTECT,
        related_name='results'
    )
    panel = models.ForeignKey(
        PGxPanel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Diplotype calling
    allele1 = models.ForeignKey(
        StarAllele,
        on_delete=models.PROTECT,
        related_name='results_as_allele1',
        null=True,
        blank=True
    )
    allele2 = models.ForeignKey(
        StarAllele,
        on_delete=models.PROTECT,
        related_name='results_as_allele2',
        null=True,
        blank=True
    )
    diplotype = models.CharField(
        max_length=100,
        blank=True,
        help_text="Diplotype string (e.g., *1/*17)"
    )

    # Copy number (for genes like CYP2D6)
    copy_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Gene copy number"
    )
    has_hybrid = models.BooleanField(
        default=False,
        help_text="Has hybrid allele"
    )

    # Activity score calculation
    activity_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated activity score"
    )

    # Phenotype assignment
    phenotype = models.ForeignKey(
        Phenotype,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results'
    )

    # Detected variants
    detected_variants = models.JSONField(
        default=list,
        blank=True,
        help_text="Variants detected for this gene"
    )

    # Calling details
    calling_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Method used for diplotype calling"
    )
    calling_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence score (0-100)"
    )

    # Clinical summary
    clinical_summary = models.TextField(
        blank=True,
        help_text="Clinical summary for this gene result"
    )
    interpretation = models.TextField(
        blank=True,
        help_text="Detailed interpretation"
    )

    # Audit
    called_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pgx_calls'
    )
    called_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pgx_reviews'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PGx Result"
        verbose_name_plural = "PGx Results"
        ordering = ['-created_at']
        unique_together = ['molecular_result', 'gene']

    def __str__(self):
        return f"{self.molecular_result.sample.sample_id} - {self.gene.symbol}: {self.diplotype}"

    @property
    def diplotype_display(self):
        if self.allele1 and self.allele2:
            return f"{self.allele1.name}/{self.allele2.name}"
        return self.diplotype or "Unknown"

    def calculate_activity_score(self):
        """Calculate activity score from allele activity scores."""
        if not self.allele1 or not self.allele2:
            return None

        score1 = self.allele1.activity_score or 0
        score2 = self.allele2.activity_score or 0

        # Account for copy number variations
        if self.copy_number and self.copy_number > 2:
            # Extra copies add activity (for genes like CYP2D6)
            extra_copies = self.copy_number - 2
            # Assume extra copies have normal function
            self.activity_score = score1 + score2 + extra_copies
        else:
            self.activity_score = score1 + score2

        return self.activity_score

    def determine_phenotype(self):
        """Determine phenotype based on activity score."""
        if self.activity_score is None:
            self.calculate_activity_score()

        if self.activity_score is None:
            return None

        # Find matching phenotype based on activity score range
        phenotype = Phenotype.objects.filter(
            gene=self.gene,
            activity_score_min__lte=self.activity_score,
            activity_score_max__gte=self.activity_score
        ).first()

        if phenotype:
            self.phenotype = phenotype

        return self.phenotype


class PGxDrugResult(models.Model):
    """
    Drug-specific recommendation based on PGx results.

    Links a PGxResult to specific drug recommendations.
    """

    pgx_result = models.ForeignKey(
        PGxResult,
        on_delete=models.CASCADE,
        related_name='drug_results'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.PROTECT,
        related_name='patient_results'
    )
    recommendation = models.ForeignKey(
        DrugRecommendation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_results'
    )

    # Patient-specific recommendation
    recommendation_text = models.TextField(
        blank=True,
        help_text="Personalized recommendation text"
    )
    action = models.CharField(
        max_length=20,
        choices=DrugRecommendation.ACTION_CHOICES,
        blank=True
    )

    # Clinical context
    clinical_notes = models.TextField(blank=True)
    is_actionable = models.BooleanField(
        default=True,
        help_text="Requires clinical action"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PGx Drug Result"
        verbose_name_plural = "PGx Drug Results"
        unique_together = ['pgx_result', 'drug']
        ordering = ['pgx_result', 'drug__name']

    def __str__(self):
        return f"{self.pgx_result} - {self.drug.name}: {self.action}"

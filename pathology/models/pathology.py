# pathology/models/pathology.py
"""
Pathology report model with TNM staging support.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Pathology(models.Model):
    """
    Pathology report with TNM staging for oncology cases.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PRELIMINARY', 'Preliminary'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('FINAL', 'Final'),
        ('AMENDED', 'Amended'),
        ('CANCELLED', 'Cancelled'),
    ]

    T_STAGE_CHOICES = [
        ('TX', 'TX - Primary tumor cannot be assessed'),
        ('T0', 'T0 - No evidence of primary tumor'),
        ('Tis', 'Tis - Carcinoma in situ'),
        ('T1', 'T1'),
        ('T1a', 'T1a'),
        ('T1b', 'T1b'),
        ('T1c', 'T1c'),
        ('T2', 'T2'),
        ('T2a', 'T2a'),
        ('T2b', 'T2b'),
        ('T3', 'T3'),
        ('T3a', 'T3a'),
        ('T3b', 'T3b'),
        ('T4', 'T4'),
        ('T4a', 'T4a'),
        ('T4b', 'T4b'),
    ]

    N_STAGE_CHOICES = [
        ('NX', 'NX - Regional lymph nodes cannot be assessed'),
        ('N0', 'N0 - No regional lymph node metastasis'),
        ('N1', 'N1'),
        ('N1a', 'N1a'),
        ('N1b', 'N1b'),
        ('N1c', 'N1c'),
        ('N2', 'N2'),
        ('N2a', 'N2a'),
        ('N2b', 'N2b'),
        ('N2c', 'N2c'),
        ('N3', 'N3'),
        ('N3a', 'N3a'),
        ('N3b', 'N3b'),
    ]

    M_STAGE_CHOICES = [
        ('MX', 'MX - Distant metastasis cannot be assessed'),
        ('M0', 'M0 - No distant metastasis'),
        ('M1', 'M1 - Distant metastasis'),
        ('M1a', 'M1a'),
        ('M1b', 'M1b'),
        ('M1c', 'M1c'),
    ]

    STAGE_GROUP_CHOICES = [
        ('0', 'Stage 0'),
        ('I', 'Stage I'),
        ('IA', 'Stage IA'),
        ('IB', 'Stage IB'),
        ('II', 'Stage II'),
        ('IIA', 'Stage IIA'),
        ('IIB', 'Stage IIB'),
        ('IIC', 'Stage IIC'),
        ('III', 'Stage III'),
        ('IIIA', 'Stage IIIA'),
        ('IIIB', 'Stage IIIB'),
        ('IIIC', 'Stage IIIC'),
        ('IV', 'Stage IV'),
        ('IVA', 'Stage IVA'),
        ('IVB', 'Stage IVB'),
    ]

    GRADE_CHOICES = [
        ('GX', 'GX - Grade cannot be assessed'),
        ('G1', 'G1 - Well differentiated'),
        ('G2', 'G2 - Moderately differentiated'),
        ('G3', 'G3 - Poorly differentiated'),
        ('G4', 'G4 - Undifferentiated'),
    ]

    pathology_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique pathology report identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='pathology_reports'
    )

    # Patient and histology link
    patient = models.ForeignKey(
        'lab_management.Patient',
        on_delete=models.CASCADE,
        related_name='pathology_reports'
    )
    histology = models.ForeignKey(
        'pathology.Histology',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pathology_reports'
    )
    lab_order = models.ForeignKey(
        'lab_management.LabOrder',
        on_delete=models.CASCADE,
        related_name='pathology_reports'
    )

    # Pathology type
    pathology_type = models.ForeignKey(
        'pathology.PathologyType',
        on_delete=models.PROTECT,
        related_name='reports'
    )

    # Tumor classification
    tumor_site = models.ForeignKey(
        'pathology.TumorSite',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pathology_reports'
    )
    tumor_morphology = models.ForeignKey(
        'pathology.TumorMorphology',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pathology_reports'
    )

    # TNM Staging (pathological)
    t_stage = models.CharField(max_length=10, choices=T_STAGE_CHOICES, blank=True)
    n_stage = models.CharField(max_length=10, choices=N_STAGE_CHOICES, blank=True)
    m_stage = models.CharField(max_length=10, choices=M_STAGE_CHOICES, blank=True)
    stage_group = models.CharField(max_length=10, choices=STAGE_GROUP_CHOICES, blank=True)

    # Clinical staging (if different from pathological)
    clinical_t_stage = models.CharField(max_length=10, choices=T_STAGE_CHOICES, blank=True)
    clinical_n_stage = models.CharField(max_length=10, choices=N_STAGE_CHOICES, blank=True)
    clinical_m_stage = models.CharField(max_length=10, choices=M_STAGE_CHOICES, blank=True)
    clinical_stage_group = models.CharField(max_length=10, choices=STAGE_GROUP_CHOICES, blank=True)

    # Staging system
    staging_system = models.CharField(
        max_length=50,
        default='AJCC 8th Edition',
        help_text="TNM staging system used"
    )

    # Grade
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)

    # Margins
    MARGIN_STATUS_CHOICES = [
        ('NEGATIVE', 'Negative'),
        ('POSITIVE', 'Positive'),
        ('CLOSE', 'Close'),
        ('INDETERMINATE', 'Indeterminate'),
        ('NA', 'Not Applicable'),
    ]
    margin_status = models.CharField(max_length=20, choices=MARGIN_STATUS_CHOICES, blank=True)
    closest_margin_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance to closest margin in mm"
    )
    margin_notes = models.TextField(blank=True)

    # Lymphovascular invasion
    lymphovascular_invasion = models.CharField(
        max_length=20,
        choices=[
            ('ABSENT', 'Absent'),
            ('PRESENT', 'Present'),
            ('INDETERMINATE', 'Indeterminate'),
        ],
        blank=True
    )
    perineural_invasion = models.CharField(
        max_length=20,
        choices=[
            ('ABSENT', 'Absent'),
            ('PRESENT', 'Present'),
            ('INDETERMINATE', 'Indeterminate'),
        ],
        blank=True
    )

    # Lymph nodes
    lymph_nodes_examined = models.PositiveSmallIntegerField(null=True, blank=True)
    lymph_nodes_positive = models.PositiveSmallIntegerField(null=True, blank=True)

    # Report content
    diagnosis = models.TextField(help_text="Final diagnosis")
    microscopic_description = models.TextField(blank=True)
    gross_description = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    clinical_correlation = models.TextField(blank=True)

    # IHC Results (stored as JSON for flexibility)
    ihc_results = models.JSONField(
        default=dict,
        blank=True,
        help_text="IHC marker results (e.g., {'ER': 'Positive 95%', 'PR': 'Positive 80%'})"
    )

    # Molecular findings
    molecular_findings = models.TextField(blank=True)

    # Synoptic data (structured CAP protocol data)
    synoptic_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured synoptic report data"
    )

    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Sign-off
    pathologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pathology_reports',
        null=True,
        blank=True,
        help_text="Signing pathologist"
    )
    signed_date = models.DateTimeField(null=True, blank=True)
    signature_hash = models.CharField(max_length=64, blank=True)

    # Amendment tracking
    amended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='amended_pathology_reports'
    )
    amended_date = models.DateTimeField(null=True, blank=True)
    amendment_reason = models.TextField(blank=True)
    original_diagnosis = models.TextField(blank=True, help_text="Original diagnosis before amendment")

    # Timestamps
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_pathology_reports'
    )

    class Meta:
        verbose_name = "Pathology Report"
        verbose_name_plural = "Pathology Reports"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pathology_id:
            self.pathology_id = self._generate_pathology_id()
        super().save(*args, **kwargs)

    def _generate_pathology_id(self):
        """Generate unique pathology ID with format: PATH-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"PATH-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.pathology_id} - {self.patient}"

    @property
    def tnm_stage(self):
        """Return formatted pTNM stage."""
        if self.t_stage and self.n_stage and self.m_stage:
            return f"p{self.t_stage}{self.n_stage}{self.m_stage}"
        return None

    @property
    def clinical_tnm_stage(self):
        """Return formatted cTNM stage."""
        if self.clinical_t_stage and self.clinical_n_stage and self.clinical_m_stage:
            return f"c{self.clinical_t_stage}{self.clinical_n_stage}{self.clinical_m_stage}"
        return None

    @property
    def is_signed(self):
        return self.pathologist is not None and self.signed_date is not None

    @property
    def lymph_node_ratio(self):
        """Calculate lymph node ratio (positive/examined)."""
        if self.lymph_nodes_examined and self.lymph_nodes_examined > 0:
            positive = self.lymph_nodes_positive or 0
            return round(positive / self.lymph_nodes_examined, 2)
        return None


class PathologyAddendum(models.Model):
    """
    Addendum to a pathology report.
    """
    pathology = models.ForeignKey(
        Pathology,
        on_delete=models.CASCADE,
        related_name='addenda'
    )

    addendum_number = models.PositiveSmallIntegerField(default=1)
    content = models.TextField()
    reason = models.CharField(max_length=200, blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pathology_addenda'
    )
    signed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pathology Addendum"
        verbose_name_plural = "Pathology Addenda"
        ordering = ['pathology', 'addendum_number']
        unique_together = [['pathology', 'addendum_number']]

    def __str__(self):
        return f"{self.pathology.pathology_id} - Addendum {self.addendum_number}"

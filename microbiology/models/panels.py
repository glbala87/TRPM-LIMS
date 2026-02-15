# microbiology/models/panels.py
"""
AST Panel models for lab-specific antibiotic testing configurations.
"""

from django.db import models
from django.utils import timezone
import uuid


class ASTPanel(models.Model):
    """
    Lab-specific AST panel defining which antibiotics to test for specific organisms.
    """
    panel_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique panel identifier"
    )

    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE,
        related_name='ast_panels'
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    # Panel type
    PANEL_TYPE_CHOICES = [
        ('STANDARD', 'Standard Panel'),
        ('SCREENING', 'Screening Panel'),
        ('EXTENDED', 'Extended Panel'),
        ('TARGETED', 'Targeted Panel'),
        ('STAT', 'STAT/Emergency Panel'),
    ]
    panel_type = models.CharField(max_length=20, choices=PANEL_TYPE_CHOICES, default='STANDARD')

    # Organisms this panel applies to
    organisms = models.ManyToManyField(
        'microbiology.Organism',
        related_name='ast_panels',
        blank=True
    )
    organism_groups = models.JSONField(
        default=list,
        blank=True,
        help_text="List of organism group names this panel applies to"
    )

    # Antibiotics in this panel
    antibiotics = models.ManyToManyField(
        'microbiology.Antibiotic',
        through='ASTMPanelAntibiotic',
        related_name='ast_panels'
    )

    # Guideline for interpretation
    guideline = models.ForeignKey(
        'microbiology.ASTGuideline',
        on_delete=models.PROTECT,
        related_name='panels',
        null=True,
        blank=True
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AST Panel"
        verbose_name_plural = "AST Panels"
        ordering = ['laboratory', 'name']
        unique_together = [['laboratory', 'code']]

    def save(self, *args, **kwargs):
        if not self.panel_id:
            self.panel_id = self._generate_panel_id()
        super().save(*args, **kwargs)

    def _generate_panel_id(self):
        """Generate unique panel ID with format: AST-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"AST-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def antibiotic_count(self):
        return self.panel_antibiotics.count()


class ASTMPanelAntibiotic(models.Model):
    """
    Through model for AST Panel to Antibiotic relationship with ordering and requirements.
    """
    panel = models.ForeignKey(ASTPanel, on_delete=models.CASCADE, related_name='panel_antibiotics')
    antibiotic = models.ForeignKey('microbiology.Antibiotic', on_delete=models.CASCADE)

    sequence = models.PositiveIntegerField(default=0, help_text="Display order")
    is_required = models.BooleanField(default=True, help_text="Must be tested")
    is_reported = models.BooleanField(default=True, help_text="Include in report")
    is_screening = models.BooleanField(default=False, help_text="Screening antibiotic")

    comment = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Panel Antibiotic"
        verbose_name_plural = "Panel Antibiotics"
        ordering = ['panel', 'sequence']
        unique_together = [['panel', 'antibiotic']]

    def __str__(self):
        return f"{self.panel.code} - {self.antibiotic.abbreviation}"

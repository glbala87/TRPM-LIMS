# microbiology/models/breakpoints.py
"""
Breakpoint models for antimicrobial susceptibility interpretation.
"""

from django.db import models
from .reference import ASTGuideline, TestMethod, BreakpointType, Host, SiteOfInfection
from .organisms import Organism
from .antibiotics import Antibiotic


class Breakpoint(models.Model):
    """
    Susceptibility breakpoint for a specific organism-antibiotic combination.
    Used for interpreting raw AST values (MIC or zone diameter) into S/I/R.
    """
    # Guideline and method
    guideline = models.ForeignKey(
        ASTGuideline,
        on_delete=models.CASCADE,
        related_name='breakpoints'
    )
    test_method = models.ForeignKey(
        TestMethod,
        on_delete=models.PROTECT,
        related_name='breakpoints'
    )
    breakpoint_type = models.ForeignKey(
        BreakpointType,
        on_delete=models.PROTECT,
        related_name='breakpoints',
        null=True,
        blank=True
    )

    # Organism and antibiotic
    organism = models.ForeignKey(
        Organism,
        on_delete=models.CASCADE,
        related_name='breakpoints',
        null=True,
        blank=True,
        help_text="Specific organism, or null for organism group"
    )
    organism_group = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organism group name (e.g., 'Enterobacteriaceae') when not specific"
    )
    antibiotic = models.ForeignKey(
        Antibiotic,
        on_delete=models.CASCADE,
        related_name='breakpoints'
    )

    # Context
    host = models.ForeignKey(
        Host,
        on_delete=models.PROTECT,
        related_name='breakpoints',
        null=True,
        blank=True
    )
    site_of_infection = models.ForeignKey(
        SiteOfInfection,
        on_delete=models.PROTECT,
        related_name='breakpoints',
        null=True,
        blank=True
    )

    # MIC breakpoints (in mg/L or ug/mL)
    susceptible_mic = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MIC <= this value is Susceptible"
    )
    intermediate_mic_low = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MIC >= this value is Intermediate (low bound)"
    )
    intermediate_mic_high = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MIC <= this value is Intermediate (high bound)"
    )
    resistant_mic = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="MIC >= this value is Resistant"
    )

    # Disk diffusion breakpoints (in mm)
    susceptible_disk = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Zone diameter >= this value is Susceptible"
    )
    intermediate_disk_low = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Zone diameter >= this value is Intermediate (low bound)"
    )
    intermediate_disk_high = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Zone diameter <= this value is Intermediate (high bound)"
    )
    resistant_disk = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Zone diameter <= this value is Resistant"
    )

    # ECOFF (Epidemiological Cut-Off)
    ecoff_mic = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Epidemiological cut-off for MIC"
    )
    ecoff_disk = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Epidemiological cut-off for disk"
    )

    # Comments and notes
    comment = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Breakpoint"
        verbose_name_plural = "Breakpoints"
        ordering = ['guideline', 'antibiotic', 'organism']

    def __str__(self):
        org_name = self.organism.abbreviated_name if self.organism else self.organism_group
        return f"{self.guideline} - {org_name} - {self.antibiotic.abbreviation}"

    def interpret_mic(self, mic_value):
        """
        Interpret MIC value and return interpretation code.
        Returns: 'S', 'I', 'R', 'SDD', or 'NS' (Not Susceptible)
        """
        if mic_value is None:
            return None

        if self.susceptible_mic and mic_value <= self.susceptible_mic:
            return 'S'
        if self.resistant_mic and mic_value >= self.resistant_mic:
            return 'R'
        if (self.intermediate_mic_low and self.intermediate_mic_high and
                self.intermediate_mic_low <= mic_value <= self.intermediate_mic_high):
            return 'I'
        # SDD (Susceptible-Dose Dependent) - treated as intermediate in most cases
        if self.susceptible_mic and self.resistant_mic:
            if self.susceptible_mic < mic_value < self.resistant_mic:
                return 'SDD'
        return 'NS'

    def interpret_disk(self, zone_diameter):
        """
        Interpret zone diameter and return interpretation code.
        Returns: 'S', 'I', 'R', or 'NS' (Not Susceptible)
        """
        if zone_diameter is None:
            return None

        if self.susceptible_disk and zone_diameter >= self.susceptible_disk:
            return 'S'
        if self.resistant_disk and zone_diameter <= self.resistant_disk:
            return 'R'
        if (self.intermediate_disk_low and self.intermediate_disk_high and
                self.intermediate_disk_low <= zone_diameter <= self.intermediate_disk_high):
            return 'I'
        return 'NS'

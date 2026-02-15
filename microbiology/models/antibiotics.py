# microbiology/models/antibiotics.py
"""
Antibiotic models with multiple coding systems support.
"""

from django.db import models
from django.utils import timezone
import uuid


class AntibioticClass(models.Model):
    """
    Antibiotic class/family (e.g., Penicillins, Cephalosporins, Fluoroquinolones).
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent_class = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subclasses',
        help_text="Parent antibiotic class for hierarchical classification"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Antibiotic Class"
        verbose_name_plural = "Antibiotic Classes"
        ordering = ['name']

    def __str__(self):
        return self.name


class Antibiotic(models.Model):
    """
    Antibiotic with multiple coding systems (WHONET, EUCAST, CLSI, ATC, LOINC).
    """
    antibiotic_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique antibiotic identifier"
    )

    # Basic info
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, help_text="Standard 2-3 letter abbreviation")
    antibiotic_class = models.ForeignKey(
        AntibioticClass,
        on_delete=models.PROTECT,
        related_name='antibiotics'
    )

    # Standard codes
    whonet_abx_code = models.CharField(max_length=10, blank=True, help_text="WHONET antibiotic code")
    eucast_code = models.CharField(max_length=20, blank=True, help_text="EUCAST code")
    clsi_code = models.CharField(max_length=20, blank=True, help_text="CLSI code")
    atc_code = models.CharField(max_length=10, blank=True, help_text="ATC classification code")
    loinc_disk = models.CharField(max_length=20, blank=True, help_text="LOINC code for disk diffusion")
    loinc_mic = models.CharField(max_length=20, blank=True, help_text="LOINC code for MIC")
    loinc_etest = models.CharField(max_length=20, blank=True, help_text="LOINC code for E-test")

    # Disk/testing characteristics
    potency = models.CharField(max_length=50, blank=True, help_text="e.g., 10 ug, 30 ug")
    disk_content_ug = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Disk content in micrograms"
    )

    # Usage flags
    human_use = models.BooleanField(default=True)
    veterinary_use = models.BooleanField(default=False)
    screening_drug = models.BooleanField(default=False, help_text="Used for resistance screening")
    confirmatory_drug = models.BooleanField(default=False, help_text="Used for resistance confirmation")

    # Spectrum
    spectrum_gram_positive = models.BooleanField(default=True)
    spectrum_gram_negative = models.BooleanField(default=True)
    spectrum_anaerobes = models.BooleanField(default=False)
    spectrum_fungi = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Antibiotic"
        verbose_name_plural = "Antibiotics"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.antibiotic_id:
            self.antibiotic_id = self._generate_antibiotic_id()
        super().save(*args, **kwargs)

    def _generate_antibiotic_id(self):
        """Generate unique antibiotic ID with format: ABX-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"ABX-{date_str}-{unique_suffix}"

    def __str__(self):
        return f"{self.abbreviation} - {self.name}"

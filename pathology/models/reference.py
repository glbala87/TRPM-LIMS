# pathology/models/reference.py
"""
Reference data models for pathology module.
"""

from django.db import models


class PathologyType(models.Model):
    """
    Type of pathology examination (e.g., Surgical, Cytology, Autopsy).
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    requires_gross = models.BooleanField(default=True, help_text="Requires gross examination")
    requires_microscopic = models.BooleanField(default=True, help_text="Requires microscopic examination")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pathology Type"
        verbose_name_plural = "Pathology Types"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class InflammationType(models.Model):
    """
    Type of inflammation observed in tissue.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Inflammation Type"
        verbose_name_plural = "Inflammation Types"
        ordering = ['name']

    def __str__(self):
        return self.name


class TumorSite(models.Model):
    """
    Anatomical site of tumor origin (ICD-O-3 topography).
    """
    code = models.CharField(max_length=10, unique=True, help_text="ICD-O-3 topography code")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    body_system = models.CharField(max_length=100, blank=True)

    # Parent for hierarchical sites
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subsites'
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tumor Site"
        verbose_name_plural = "Tumor Sites"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class TumorMorphology(models.Model):
    """
    Tumor morphology/histology type (ICD-O-3 morphology).
    """
    code = models.CharField(max_length=10, unique=True, help_text="ICD-O-3 morphology code")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Behavior code
    BEHAVIOR_CHOICES = [
        ('0', 'Benign'),
        ('1', 'Uncertain'),
        ('2', 'In situ'),
        ('3', 'Malignant, primary'),
        ('6', 'Malignant, metastatic'),
        ('9', 'Malignant, uncertain'),
    ]
    behavior = models.CharField(max_length=1, choices=BEHAVIOR_CHOICES, default='3')

    # Common grading
    typical_grade = models.CharField(max_length=10, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tumor Morphology"
        verbose_name_plural = "Tumor Morphologies"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def full_code(self):
        """Return morphology code with behavior (e.g., 8140/3)."""
        return f"{self.code}/{self.behavior}"


class SpecimenType(models.Model):
    """
    Type of pathology specimen.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    collection_method = models.CharField(max_length=100, blank=True)
    container_type = models.CharField(max_length=100, blank=True)
    fixative = models.CharField(max_length=100, blank=True, help_text="Required fixative")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Specimen Type"
        verbose_name_plural = "Specimen Types"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class StainingProtocol(models.Model):
    """
    Staining protocol for histology.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stain_type = models.CharField(
        max_length=20,
        choices=[
            ('ROUTINE', 'Routine'),
            ('SPECIAL', 'Special Stain'),
            ('IHC', 'Immunohistochemistry'),
            ('ISH', 'In Situ Hybridization'),
            ('FISH', 'FISH'),
            ('OTHER', 'Other'),
        ],
        default='ROUTINE'
    )
    antibody = models.CharField(max_length=100, blank=True, help_text="For IHC stains")
    clone = models.CharField(max_length=50, blank=True, help_text="Antibody clone")
    dilution = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Staining Protocol"
        verbose_name_plural = "Staining Protocols"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

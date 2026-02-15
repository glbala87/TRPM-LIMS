# microbiology/models/organisms.py
"""
Taxonomic hierarchy models for microbiology organisms.
Follows standard biological classification with WHONET and SNOMED-CT coding.
"""

from django.db import models
from django.utils import timezone
import uuid


class Kingdom(models.Model):
    """Taxonomic kingdom (e.g., Bacteria, Fungi, Protista)."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Kingdom"
        verbose_name_plural = "Kingdoms"
        ordering = ['name']

    def __str__(self):
        return self.name


class Phylum(models.Model):
    """Taxonomic phylum."""
    kingdom = models.ForeignKey(Kingdom, on_delete=models.CASCADE, related_name='phyla')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Phylum"
        verbose_name_plural = "Phyla"
        ordering = ['kingdom', 'name']
        unique_together = [['kingdom', 'name']]

    def __str__(self):
        return self.name


class OrganismClass(models.Model):
    """Taxonomic class."""
    phylum = models.ForeignKey(Phylum, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ['phylum', 'name']
        unique_together = [['phylum', 'name']]

    def __str__(self):
        return self.name


class Order(models.Model):
    """Taxonomic order."""
    organism_class = models.ForeignKey(OrganismClass, on_delete=models.CASCADE, related_name='orders')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['organism_class', 'name']
        unique_together = [['organism_class', 'name']]

    def __str__(self):
        return self.name


class Family(models.Model):
    """Taxonomic family."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='families')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
        ordering = ['order', 'name']
        unique_together = [['order', 'name']]

    def __str__(self):
        return self.name


class Genus(models.Model):
    """Taxonomic genus."""
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='genera')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Genus"
        verbose_name_plural = "Genera"
        ordering = ['family', 'name']
        unique_together = [['family', 'name']]

    def __str__(self):
        return self.name


class Organism(models.Model):
    """
    Microorganism with full taxonomic classification and standard coding.
    """
    ORGANISM_TYPE_CHOICES = [
        ('BACTERIA', 'Bacteria'),
        ('FUNGUS', 'Fungus'),
        ('PARASITE', 'Parasite'),
        ('VIRUS', 'Virus'),
        ('MYCOBACTERIA', 'Mycobacteria'),
        ('YEAST', 'Yeast'),
        ('MOLD', 'Mold'),
    ]

    MORPHOLOGY_CHOICES = [
        ('COCCI', 'Cocci'),
        ('BACILLI', 'Bacilli'),
        ('COCCOBACILLI', 'Coccobacilli'),
        ('SPIROCHETE', 'Spirochete'),
        ('PLEOMORPHIC', 'Pleomorphic'),
        ('FILAMENTOUS', 'Filamentous'),
        ('YEAST', 'Yeast'),
        ('DIMORPHIC', 'Dimorphic'),
        ('OTHER', 'Other'),
    ]

    GRAM_STAIN_CHOICES = [
        ('POSITIVE', 'Gram Positive'),
        ('NEGATIVE', 'Gram Negative'),
        ('VARIABLE', 'Gram Variable'),
        ('NA', 'Not Applicable'),
    ]

    organism_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique organism identifier"
    )

    # Taxonomy
    kingdom = models.ForeignKey(Kingdom, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)
    phylum = models.ForeignKey(Phylum, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)
    organism_class = models.ForeignKey(OrganismClass, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)
    genus = models.ForeignKey(Genus, on_delete=models.PROTECT, related_name='organisms', null=True, blank=True)

    # Species identification
    species = models.CharField(max_length=100)
    subspecies = models.CharField(max_length=100, blank=True)
    common_name = models.CharField(max_length=200, blank=True)

    # Standard codes
    whonet_org_code = models.CharField(max_length=20, blank=True, help_text="WHONET organism code")
    sct_code = models.CharField(max_length=20, blank=True, help_text="SNOMED-CT code")
    ncbi_tax_id = models.CharField(max_length=20, blank=True, help_text="NCBI Taxonomy ID")

    # Characteristics
    organism_type = models.CharField(max_length=20, choices=ORGANISM_TYPE_CHOICES, default='BACTERIA')
    morphology = models.CharField(max_length=20, choices=MORPHOLOGY_CHOICES, blank=True)
    gram_stain = models.CharField(max_length=20, choices=GRAM_STAIN_CHOICES, default='NA')
    anaerobe = models.BooleanField(default=False, help_text="Obligate anaerobe")
    facultative_anaerobe = models.BooleanField(default=False)

    # Clinical relevance
    is_pathogen = models.BooleanField(default=True)
    is_opportunistic = models.BooleanField(default=False)
    biosafety_level = models.PositiveSmallIntegerField(default=2, help_text="BSL 1-4")

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organism"
        verbose_name_plural = "Organisms"
        ordering = ['genus__name', 'species']

    def save(self, *args, **kwargs):
        if not self.organism_id:
            self.organism_id = self._generate_organism_id()
        super().save(*args, **kwargs)

    def _generate_organism_id(self):
        """Generate unique organism ID with format: ORG-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        return f"ORG-{date_str}-{unique_suffix}"

    def __str__(self):
        if self.genus:
            return f"{self.genus.name} {self.species}"
        return self.species

    @property
    def full_name(self):
        """Return full taxonomic name."""
        parts = []
        if self.genus:
            parts.append(self.genus.name)
        parts.append(self.species)
        if self.subspecies:
            parts.append(f"subsp. {self.subspecies}")
        return " ".join(parts)

    @property
    def abbreviated_name(self):
        """Return abbreviated name (e.g., E. coli)."""
        if self.genus:
            return f"{self.genus.name[0]}. {self.species}"
        return self.species

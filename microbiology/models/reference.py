# microbiology/models/reference.py
"""
Reference data models for microbiology module.
Includes test methods, breakpoint types, hosts, sites of infection, and AST guidelines.
"""

from django.db import models


class TestMethod(models.Model):
    """
    Test method for antimicrobial susceptibility testing (e.g., Disk Diffusion, MIC).
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Test Method"
        verbose_name_plural = "Test Methods"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class BreakpointType(models.Model):
    """
    Type of breakpoint (e.g., Human, Veterinary, ECOFF).
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Breakpoint Type"
        verbose_name_plural = "Breakpoint Types"
        ordering = ['name']

    def __str__(self):
        return self.name


class Host(models.Model):
    """
    Host species for veterinary microbiology (e.g., Human, Bovine, Canine).
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        ordering = ['name']

    def __str__(self):
        return self.name


class SiteOfInfection(models.Model):
    """
    Anatomical site of infection affecting breakpoint selection.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site of Infection"
        verbose_name_plural = "Sites of Infection"
        ordering = ['name']

    def __str__(self):
        return self.name


class ASTGuideline(models.Model):
    """
    AST guideline/standard with version year (e.g., CLSI 2024, EUCAST 2024).
    """
    GUIDELINE_CHOICES = [
        ('CLSI', 'CLSI'),
        ('EUCAST', 'EUCAST'),
        ('SFM', 'SFM (French)'),
        ('DIN', 'DIN (German)'),
        ('BSAC', 'BSAC (British)'),
        ('SRGA', 'SRGA (Swedish)'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=50, choices=GUIDELINE_CHOICES)
    year = models.PositiveIntegerField()
    version = models.CharField(max_length=20, blank=True, help_text="e.g., M100-Ed34")
    description = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AST Guideline"
        verbose_name_plural = "AST Guidelines"
        ordering = ['-year', 'name']
        unique_together = [['name', 'year']]

    def __str__(self):
        return f"{self.get_name_display()} {self.year}"

    def save(self, *args, **kwargs):
        # Ensure only one guideline per name is marked as current
        if self.is_current:
            ASTGuideline.objects.filter(name=self.name, is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

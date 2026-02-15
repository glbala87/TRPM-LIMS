# ontology/models.py
"""
Disease ontology and clinical terminology models.
Inspired by baobab.lims disease ontology support.
"""

from django.db import models
from django.conf import settings


class OntologySource(models.Model):
    """Source ontology (ICD-10, SNOMED-CT, HPO, etc.)."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    version = models.CharField(max_length=50, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ontology Source"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class DiseaseOntology(models.Model):
    """Disease/condition terms from standard ontologies."""

    source = models.ForeignKey(OntologySource, on_delete=models.CASCADE, related_name='terms')
    code = models.CharField(max_length=50, help_text="Term code (e.g., ICD-10 code)")
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    synonyms = models.JSONField(default=list, blank=True)

    # Hierarchy
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    hierarchy_level = models.PositiveIntegerField(default=0)

    # Clinical information
    clinical_significance = models.TextField(blank=True)
    affected_system = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Disease Term"
        verbose_name_plural = "Disease Terms"
        unique_together = [['source', 'code']]
        ordering = ['source', 'code']

    def __str__(self):
        return f"{self.code}: {self.name}"

    @property
    def full_code(self):
        return f"{self.source.code}:{self.code}"


class AnatomicalSite(models.Model):
    """Anatomical sites/body locations."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    system = models.CharField(max_length=100, blank=True, help_text="Body system")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Anatomical Site"
        ordering = ['name']

    def __str__(self):
        return self.name


class ClinicalIndication(models.Model):
    """Clinical indication for testing."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    diseases = models.ManyToManyField(DiseaseOntology, blank=True, related_name='indications')
    anatomical_sites = models.ManyToManyField(AnatomicalSite, blank=True)
    test_panels = models.ManyToManyField('molecular_diagnostics.MolecularTestPanel', blank=True, related_name='indications')
    icd_codes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Clinical Indication"
        ordering = ['name']

    def __str__(self):
        return self.name


class Organism(models.Model):
    """Organism/species for samples."""

    scientific_name = models.CharField(max_length=200, unique=True)
    common_name = models.CharField(max_length=200, blank=True)
    ncbi_taxonomy_id = models.CharField(max_length=20, blank=True)
    is_host = models.BooleanField(default=False, help_text="Can be a host organism")
    is_pathogen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Organism"
        ordering = ['scientific_name']

    def __str__(self):
        return f"{self.scientific_name} ({self.common_name})" if self.common_name else self.scientific_name


class PatientDiagnosis(models.Model):
    """Patient diagnosis linking to ontology terms."""

    patient = models.ForeignKey('lab_management.Patient', on_delete=models.CASCADE, related_name='diagnoses')
    disease = models.ForeignKey(DiseaseOntology, on_delete=models.PROTECT, related_name='patient_diagnoses')
    anatomical_site = models.ForeignKey(AnatomicalSite, on_delete=models.SET_NULL, null=True, blank=True)

    diagnosis_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    diagnosed_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Patient Diagnosis"
        verbose_name_plural = "Patient Diagnoses"
        ordering = ['-diagnosis_date']

    def __str__(self):
        return f"{self.patient} - {self.disease.name}"

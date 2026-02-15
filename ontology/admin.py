# ontology/admin.py

from django.contrib import admin
from .models import (
    OntologySource, DiseaseOntology, AnatomicalSite,
    ClinicalIndication, Organism, PatientDiagnosis
)


@admin.register(OntologySource)
class OntologySourceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'version', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(DiseaseOntology)
class DiseaseOntologyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'source', 'hierarchy_level', 'is_active']
    list_filter = ['source', 'hierarchy_level', 'is_active', 'affected_system']
    search_fields = ['code', 'name', 'description', 'synonyms']
    raw_id_fields = ['parent']

    fieldsets = (
        (None, {
            'fields': ('source', 'code', 'name', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'hierarchy_level')
        }),
        ('Clinical Information', {
            'fields': ('clinical_significance', 'affected_system', 'synonyms')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']


@admin.register(AnatomicalSite)
class AnatomicalSiteAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'system', 'parent', 'is_active']
    list_filter = ['system', 'is_active']
    search_fields = ['code', 'name']
    raw_id_fields = ['parent']


@admin.register(ClinicalIndication)
class ClinicalIndicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'disease_count', 'test_panel_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['diseases', 'anatomical_sites', 'test_panels']

    def disease_count(self, obj):
        return obj.diseases.count()
    disease_count.short_description = 'Diseases'

    def test_panel_count(self, obj):
        return obj.test_panels.count()
    test_panel_count.short_description = 'Test Panels'


@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    list_display = ['scientific_name', 'common_name', 'ncbi_taxonomy_id', 'is_host', 'is_pathogen', 'is_active']
    list_filter = ['is_host', 'is_pathogen', 'is_active']
    search_fields = ['scientific_name', 'common_name', 'ncbi_taxonomy_id']


@admin.register(PatientDiagnosis)
class PatientDiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'disease', 'diagnosis_date', 'is_primary', 'is_confirmed']
    list_filter = ['is_primary', 'is_confirmed', 'disease__source']
    search_fields = ['patient__mrn', 'disease__name', 'disease__code']
    raw_id_fields = ['patient', 'disease', 'anatomical_site']
    readonly_fields = ['created_at']

    fieldsets = (
        (None, {
            'fields': ('patient', 'disease', 'anatomical_site')
        }),
        ('Diagnosis Details', {
            'fields': ('diagnosis_date', 'is_primary', 'is_confirmed', 'diagnosed_by')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

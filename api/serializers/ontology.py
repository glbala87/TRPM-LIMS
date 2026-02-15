"""
Serializers for ontology app models.
"""
from rest_framework import serializers
from ontology.models import (
    OntologySource, DiseaseOntology, AnatomicalSite,
    ClinicalIndication, Organism, PatientDiagnosis
)


class OntologySourceSerializer(serializers.ModelSerializer):
    """Serializer for OntologySource model."""

    class Meta:
        model = OntologySource
        fields = ['id', 'code', 'name', 'version', 'url', 'description', 'is_active']


class DiseaseOntologySerializer(serializers.ModelSerializer):
    """Serializer for DiseaseOntology model."""
    source_name = serializers.CharField(source='source.name', read_only=True)
    full_code = serializers.ReadOnlyField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = DiseaseOntology
        fields = [
            'id', 'source', 'source_name', 'code', 'full_code', 'name', 'description',
            'synonyms', 'parent', 'parent_name', 'hierarchy_level',
            'clinical_significance', 'affected_system', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DiseaseOntologyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for DiseaseOntology list views."""
    source_code = serializers.CharField(source='source.code', read_only=True)
    full_code = serializers.ReadOnlyField()

    class Meta:
        model = DiseaseOntology
        fields = ['id', 'code', 'source_code', 'full_code', 'name', 'hierarchy_level']


class AnatomicalSiteSerializer(serializers.ModelSerializer):
    """Serializer for AnatomicalSite model."""
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = AnatomicalSite
        fields = ['id', 'code', 'name', 'parent', 'parent_name', 'system', 'is_active']


class ClinicalIndicationSerializer(serializers.ModelSerializer):
    """Serializer for ClinicalIndication model."""
    diseases = DiseaseOntologyListSerializer(many=True, read_only=True)
    disease_count = serializers.SerializerMethodField()
    test_panel_count = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalIndication
        fields = [
            'id', 'name', 'description', 'diseases', 'anatomical_sites',
            'test_panels', 'icd_codes', 'disease_count', 'test_panel_count', 'is_active'
        ]

    def get_disease_count(self, obj):
        return obj.diseases.count()

    def get_test_panel_count(self, obj):
        return obj.test_panels.count()


class OrganismSerializer(serializers.ModelSerializer):
    """Serializer for Organism model."""

    class Meta:
        model = Organism
        fields = [
            'id', 'scientific_name', 'common_name', 'ncbi_taxonomy_id',
            'is_host', 'is_pathogen', 'is_active'
        ]


class PatientDiagnosisSerializer(serializers.ModelSerializer):
    """Serializer for PatientDiagnosis model."""
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    disease_code = serializers.CharField(source='disease.full_code', read_only=True)
    anatomical_site_name = serializers.CharField(source='anatomical_site.name', read_only=True)

    class Meta:
        model = PatientDiagnosis
        fields = [
            'id', 'patient', 'disease', 'disease_name', 'disease_code',
            'anatomical_site', 'anatomical_site_name',
            'diagnosis_date', 'is_primary', 'is_confirmed',
            'notes', 'diagnosed_by', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']

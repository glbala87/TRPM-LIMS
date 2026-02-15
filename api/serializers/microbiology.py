# api/serializers/microbiology.py
"""
API Serializers for microbiology module.
"""

from rest_framework import serializers
from microbiology.models import (
    TestMethod, BreakpointType, Host, SiteOfInfection, ASTGuideline,
    Kingdom, Phylum, OrganismClass, Order, Family, Genus, Organism,
    AntibioticClass, Antibiotic,
    Breakpoint,
    ASTPanel, ASTMPanelAntibiotic,
    MicrobiologySample, OrganismResult, ASTResult,
)


# Reference Serializers
class TestMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestMethod
        fields = '__all__'


class BreakpointTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakpointType
        fields = '__all__'


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


class SiteOfInfectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteOfInfection
        fields = '__all__'


class ASTGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ASTGuideline
        fields = '__all__'


# Taxonomy Serializers
class KingdomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kingdom
        fields = '__all__'


class PhylumSerializer(serializers.ModelSerializer):
    kingdom_name = serializers.CharField(source='kingdom.name', read_only=True)

    class Meta:
        model = Phylum
        fields = '__all__'


class OrganismClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganismClass
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'


class GenusSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(source='family.name', read_only=True)

    class Meta:
        model = Genus
        fields = '__all__'


class OrganismSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    abbreviated_name = serializers.CharField(read_only=True)
    genus_name = serializers.CharField(source='genus.name', read_only=True)

    class Meta:
        model = Organism
        fields = '__all__'
        read_only_fields = ['organism_id', 'created_at', 'updated_at']


class OrganismListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Organism
        fields = ['id', 'organism_id', 'full_name', 'organism_type', 'gram_stain', 'whonet_org_code', 'is_active']


# Antibiotic Serializers
class AntibioticClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntibioticClass
        fields = '__all__'


class AntibioticSerializer(serializers.ModelSerializer):
    antibiotic_class_name = serializers.CharField(source='antibiotic_class.name', read_only=True)

    class Meta:
        model = Antibiotic
        fields = '__all__'
        read_only_fields = ['antibiotic_id', 'created_at', 'updated_at']


class AntibioticListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antibiotic
        fields = ['id', 'antibiotic_id', 'name', 'abbreviation', 'antibiotic_class', 'whonet_abx_code', 'is_active']


# Breakpoint Serializers
class BreakpointSerializer(serializers.ModelSerializer):
    guideline_display = serializers.CharField(source='guideline.__str__', read_only=True)
    antibiotic_name = serializers.CharField(source='antibiotic.name', read_only=True)
    organism_name = serializers.SerializerMethodField()

    class Meta:
        model = Breakpoint
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_organism_name(self, obj):
        if obj.organism:
            return obj.organism.abbreviated_name
        return obj.organism_group


# Panel Serializers
class ASTPanelAntibioticSerializer(serializers.ModelSerializer):
    antibiotic_name = serializers.CharField(source='antibiotic.name', read_only=True)
    antibiotic_abbreviation = serializers.CharField(source='antibiotic.abbreviation', read_only=True)

    class Meta:
        model = ASTMPanelAntibiotic
        fields = ['id', 'antibiotic', 'antibiotic_name', 'antibiotic_abbreviation',
                  'sequence', 'is_required', 'is_reported', 'is_screening', 'comment']


class ASTPanelSerializer(serializers.ModelSerializer):
    panel_antibiotics = ASTPanelAntibioticSerializer(many=True, read_only=True)
    antibiotic_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ASTPanel
        fields = '__all__'
        read_only_fields = ['panel_id', 'created_at', 'updated_at']


class ASTPanelListSerializer(serializers.ModelSerializer):
    antibiotic_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ASTPanel
        fields = ['id', 'panel_id', 'code', 'name', 'panel_type', 'antibiotic_count', 'is_active']


# Result Serializers
class ASTResultSerializer(serializers.ModelSerializer):
    antibiotic_name = serializers.CharField(source='antibiotic.name', read_only=True)
    antibiotic_abbreviation = serializers.CharField(source='antibiotic.abbreviation', read_only=True)
    interpretation_display = serializers.CharField(source='get_interpretation_display', read_only=True)

    class Meta:
        model = ASTResult
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrganismResultSerializer(serializers.ModelSerializer):
    organism_name = serializers.CharField(source='organism.full_name', read_only=True)
    ast_results = ASTResultSerializer(many=True, read_only=True)

    class Meta:
        model = OrganismResult
        fields = '__all__'
        read_only_fields = ['result_id', 'created_at', 'updated_at']


class OrganismResultListSerializer(serializers.ModelSerializer):
    organism_name = serializers.CharField(source='organism.abbreviated_name', read_only=True)
    ast_count = serializers.SerializerMethodField()

    class Meta:
        model = OrganismResult
        fields = ['id', 'result_id', 'sample', 'organism', 'organism_name', 'quantity', 'is_significant', 'ast_count']

    def get_ast_count(self, obj):
        return obj.ast_results.count()


class MicrobiologySampleSerializer(serializers.ModelSerializer):
    organism_results = OrganismResultSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MicrobiologySample
        fields = '__all__'
        read_only_fields = ['sample_id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return str(obj.lab_order.patient) if obj.lab_order else None


class MicrobiologySampleListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    organism_count = serializers.SerializerMethodField()

    class Meta:
        model = MicrobiologySample
        fields = ['id', 'sample_id', 'specimen_type', 'status', 'patient_name',
                  'organism_count', 'growth_observed', 'received_datetime']

    def get_patient_name(self, obj):
        return str(obj.lab_order.patient) if obj.lab_order else None

    def get_organism_count(self, obj):
        return obj.organism_results.count()


class MicrobiologySampleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicrobiologySample
        fields = ['laboratory', 'lab_order', 'specimen_type', 'specimen_source',
                  'collection_datetime', 'culture_type', 'clinical_info', 'antibiotics_prior', 'notes']


# Interpretation request serializer
class ASTInterpretationRequestSerializer(serializers.Serializer):
    organism_id = serializers.IntegerField()
    antibiotic_id = serializers.IntegerField()
    raw_value = serializers.CharField()
    test_method = serializers.ChoiceField(choices=['MIC', 'DISK', 'ETEST'])
    guideline_id = serializers.IntegerField(required=False)

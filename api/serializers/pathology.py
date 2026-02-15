# api/serializers/pathology.py
"""
API Serializers for pathology module.
"""

from rest_framework import serializers
from pathology.models import (
    PathologyType, InflammationType, TumorSite, TumorMorphology,
    SpecimenType, StainingProtocol,
    Histology, HistologyBlock, HistologySlide,
    Pathology, PathologyAddendum,
)


# Reference Serializers
class PathologyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathologyType
        fields = '__all__'


class InflammationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InflammationType
        fields = '__all__'


class TumorSiteSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = TumorSite
        fields = '__all__'


class TumorMorphologySerializer(serializers.ModelSerializer):
    full_code = serializers.CharField(read_only=True)
    behavior_display = serializers.CharField(source='get_behavior_display', read_only=True)

    class Meta:
        model = TumorMorphology
        fields = '__all__'


class SpecimenTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecimenType
        fields = '__all__'


class StainingProtocolSerializer(serializers.ModelSerializer):
    stain_type_display = serializers.CharField(source='get_stain_type_display', read_only=True)

    class Meta:
        model = StainingProtocol
        fields = '__all__'


# Histology Serializers
class HistologySlideSerializer(serializers.ModelSerializer):
    stain_name = serializers.CharField(source='stain.name', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)

    class Meta:
        model = HistologySlide
        fields = '__all__'
        read_only_fields = ['created_at']


class HistologyBlockSerializer(serializers.ModelSerializer):
    slides = HistologySlideSerializer(many=True, read_only=True)
    slide_count = serializers.SerializerMethodField()

    class Meta:
        model = HistologyBlock
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_slide_count(self, obj):
        return obj.slides.count()


class HistologySerializer(serializers.ModelSerializer):
    blocks = HistologyBlockSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    specimen_type_name = serializers.CharField(source='specimen_type.name', read_only=True)
    fixation_hours = serializers.FloatField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Histology
        fields = '__all__'
        read_only_fields = ['histology_id', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return str(obj.patient) if obj.lab_order else None


class HistologyListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    specimen_type_name = serializers.CharField(source='specimen_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Histology
        fields = ['id', 'histology_id', 'surgical_number', 'specimen_type', 'specimen_type_name',
                  'patient_name', 'status', 'status_display', 'block_count', 'slide_count',
                  'is_stat', 'received_datetime']

    def get_patient_name(self, obj):
        return str(obj.patient) if obj.lab_order else None


class HistologyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Histology
        fields = ['laboratory', 'lab_order', 'molecular_sample', 'specimen_type', 'specimen_site',
                  'clinical_history', 'surgical_number', 'fixation_type', 'is_stat', 'notes']


# Pathology Serializers
class PathologyAddendumSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = PathologyAddendum
        fields = '__all__'
        read_only_fields = ['signed_date']


class PathologySerializer(serializers.ModelSerializer):
    addenda = PathologyAddendumSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    tnm_stage = serializers.CharField(read_only=True)
    clinical_tnm_stage = serializers.CharField(read_only=True)
    is_signed = serializers.BooleanField(read_only=True)
    lymph_node_ratio = serializers.FloatField(read_only=True)
    pathologist_name = serializers.CharField(source='pathologist.get_full_name', read_only=True)
    tumor_site_name = serializers.CharField(source='tumor_site.name', read_only=True)
    tumor_morphology_name = serializers.CharField(source='tumor_morphology.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Pathology
        fields = '__all__'
        read_only_fields = ['pathology_id', 'signature_hash', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return str(obj.patient) if obj.patient else None


class PathologyListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    tnm_stage = serializers.CharField(read_only=True)
    pathologist_name = serializers.CharField(source='pathologist.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Pathology
        fields = ['id', 'pathology_id', 'patient', 'patient_name', 'pathology_type',
                  'tnm_stage', 'stage_group', 'grade', 'status', 'status_display',
                  'pathologist', 'pathologist_name', 'signed_date', 'created_at']

    def get_patient_name(self, obj):
        return str(obj.patient) if obj.patient else None


class PathologyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathology
        fields = ['laboratory', 'patient', 'histology', 'lab_order', 'pathology_type',
                  'tumor_site', 'tumor_morphology']


class PathologyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathology
        fields = ['diagnosis', 'microscopic_description', 'gross_description', 'comment',
                  'clinical_correlation', 't_stage', 'n_stage', 'm_stage', 'stage_group',
                  'grade', 'margin_status', 'closest_margin_mm', 'margin_notes',
                  'lymphovascular_invasion', 'perineural_invasion',
                  'lymph_nodes_examined', 'lymph_nodes_positive',
                  'ihc_results', 'molecular_findings', 'synoptic_data']


# Request Serializers
class SignReportSerializer(serializers.Serializer):
    is_preliminary = serializers.BooleanField(default=False)


class AmendReportSerializer(serializers.Serializer):
    new_diagnosis = serializers.CharField()
    amendment_reason = serializers.CharField()


class AddAddendumSerializer(serializers.Serializer):
    content = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CalculateStageSerializer(serializers.Serializer):
    t_stage = serializers.CharField()
    n_stage = serializers.CharField()
    m_stage = serializers.CharField()
    tumor_site_id = serializers.IntegerField(required=False)


class StagingSummarySerializer(serializers.Serializer):
    pathological = serializers.DictField()
    clinical = serializers.DictField()
    grade = serializers.CharField()
    staging_system = serializers.CharField()
    margin_status = serializers.CharField()
    lymph_nodes = serializers.DictField()
    invasion = serializers.DictField()
    calculated_stage = serializers.DictField(required=False)

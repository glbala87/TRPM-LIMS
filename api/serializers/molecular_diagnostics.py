"""
Serializers for molecular_diagnostics app models.
"""
from rest_framework import serializers
from molecular_diagnostics.models import (
    MolecularSample, MolecularSampleType, MolecularTestPanel, GeneTarget,
    MolecularResult, PCRResult, SequencingResult, VariantCall,
    PCRPlate, PlateWell, InstrumentRun, NGSLibrary, NGSPool,
    QCMetricDefinition, ControlSample, QCRecord,
    WorkflowDefinition, WorkflowStep, SampleHistory
)


# Sample Type Serializers

class MolecularSampleTypeSerializer(serializers.ModelSerializer):
    """Serializer for MolecularSampleType model."""

    class Meta:
        model = MolecularSampleType
        fields = [
            'id', 'name', 'code', 'description', 'storage_temperature',
            'stability_hours', 'collection_instructions', 'is_active'
        ]


# Gene Target Serializers

class GeneTargetSerializer(serializers.ModelSerializer):
    """Serializer for GeneTarget model."""

    class Meta:
        model = GeneTarget
        fields = [
            'id', 'symbol', 'name', 'chromosome', 'genomic_start', 'genomic_end',
            'transcript_id', 'exon', 'clinical_significance', 'description', 'is_active'
        ]


class GeneTargetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for GeneTarget list views."""

    class Meta:
        model = GeneTarget
        fields = ['id', 'symbol', 'name', 'chromosome', 'clinical_significance', 'is_active']


# Test Panel Serializers

class MolecularTestPanelSerializer(serializers.ModelSerializer):
    """Serializer for MolecularTestPanel model."""
    gene_targets = GeneTargetListSerializer(many=True, read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)

    class Meta:
        model = MolecularTestPanel
        fields = [
            'id', 'name', 'code', 'description', 'test_type', 'test_type_display',
            'methodology', 'gene_targets', 'sample_requirements', 'turnaround_days',
            'requires_extraction', 'clinical_indications', 'limitations', 'is_active'
        ]


class MolecularTestPanelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MolecularTestPanel list views."""
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    gene_count = serializers.SerializerMethodField()

    class Meta:
        model = MolecularTestPanel
        fields = ['id', 'name', 'code', 'test_type_display', 'turnaround_days', 'gene_count', 'is_active']

    def get_gene_count(self, obj):
        return obj.gene_targets.count()


# Sample Serializers

class MolecularSampleSerializer(serializers.ModelSerializer):
    """Serializer for MolecularSample model."""
    sample_type_name = serializers.CharField(source='sample_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    storage_location = serializers.SerializerMethodField()

    class Meta:
        model = MolecularSample
        fields = [
            'id', 'sample_id', 'lab_order', 'sample_type', 'sample_type_name',
            'status', 'status_display', 'priority', 'priority_display',
            'received_date', 'received_by', 'collection_date', 'collection_time',
            'volume_ul', 'concentration_ng_ul', 'a260_280_ratio', 'a260_230_ratio',
            'quality_notes', 'storage_position', 'storage_location',
            'is_aliquot', 'parent_aliquot', 'aliquot_number',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sample_id', 'created_at', 'updated_at']

    def get_storage_location(self, obj):
        if obj.storage_position:
            return obj.storage_position.full_location
        return None


class MolecularSampleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MolecularSample list views."""
    sample_type_name = serializers.CharField(source='sample_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = MolecularSample
        fields = [
            'id', 'sample_id', 'sample_type_name', 'status', 'status_display',
            'priority', 'priority_display', 'received_date', 'is_active'
        ]


class MolecularSampleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MolecularSample records."""

    class Meta:
        model = MolecularSample
        fields = [
            'lab_order', 'sample_type', 'priority', 'collection_date', 'collection_time',
            'volume_ul', 'quality_notes', 'is_aliquot', 'parent_aliquot'
        ]


class SampleTransitionSerializer(serializers.Serializer):
    """Serializer for sample workflow transitions."""
    new_status = serializers.ChoiceField(choices=MolecularSample.WORKFLOW_STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    qc_passed = serializers.BooleanField(required=False)
    qc_notes = serializers.CharField(required=False, allow_blank=True)


# Workflow Serializers

class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStep model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'name', 'order', 'status', 'status_display', 'description',
            'requires_qc', 'qc_metrics', 'required_equipment', 'estimated_duration_minutes',
            'is_terminal', 'allowed_transitions'
        ]


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowDefinition model."""
    steps = WorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = ['id', 'name', 'description', 'is_active', 'steps']


class SampleHistorySerializer(serializers.ModelSerializer):
    """Serializer for SampleHistory model."""
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = SampleHistory
        fields = [
            'id', 'sample', 'from_status', 'from_status_display',
            'to_status', 'to_status_display', 'user', 'user_name',
            'timestamp', 'notes', 'qc_passed', 'qc_notes'
        ]


# Batch Serializers

class InstrumentRunSerializer(serializers.ModelSerializer):
    """Serializer for InstrumentRun model."""
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = InstrumentRun
        fields = [
            'id', 'run_id', 'instrument', 'instrument_name', 'status', 'status_display',
            'protocol_name', 'protocol_version', 'run_parameters',
            'started_at', 'completed_at', 'duration', 'started_by', 'notes'
        ]


class InstrumentRunListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for InstrumentRun list views."""
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InstrumentRun
        fields = ['id', 'run_id', 'instrument_name', 'status_display', 'started_at', 'completed_at']


class PlateWellSerializer(serializers.ModelSerializer):
    """Serializer for PlateWell model."""
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True)
    control_type_display = serializers.CharField(source='get_control_type_display', read_only=True)

    class Meta:
        model = PlateWell
        fields = [
            'id', 'plate', 'position', 'sample', 'sample_id',
            'control_sample', 'control_type', 'control_type_display',
            'replicate_number', 'is_empty'
        ]


class PCRPlateSerializer(serializers.ModelSerializer):
    """Serializer for PCRPlate model."""
    plate_type_display = serializers.CharField(source='get_plate_type_display', read_only=True)
    wells = PlateWellSerializer(many=True, read_only=True)
    layout = serializers.SerializerMethodField()

    class Meta:
        model = PCRPlate
        fields = [
            'id', 'barcode', 'plate_type', 'plate_type_display',
            'instrument_run', 'created_at', 'created_by', 'wells', 'layout'
        ]

    def get_layout(self, obj):
        return obj.get_layout()


class PCRPlateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PCRPlate list views."""
    plate_type_display = serializers.CharField(source='get_plate_type_display', read_only=True)
    sample_count = serializers.SerializerMethodField()

    class Meta:
        model = PCRPlate
        fields = ['id', 'barcode', 'plate_type_display', 'instrument_run', 'created_at', 'sample_count']

    def get_sample_count(self, obj):
        return obj.wells.filter(sample__isnull=False).count()


class NGSLibrarySerializer(serializers.ModelSerializer):
    """Serializer for NGSLibrary model."""
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True)

    class Meta:
        model = NGSLibrary
        fields = [
            'id', 'library_id', 'sample', 'sample_id', 'index_sequence',
            'index2_sequence', 'concentration_nm', 'molarity_nm', 'fragment_size_bp',
            'prep_kit', 'prepared_by', 'prepared_at', 'notes'
        ]


class NGSPoolSerializer(serializers.ModelSerializer):
    """Serializer for NGSPool model."""
    libraries = NGSLibrarySerializer(many=True, read_only=True)

    class Meta:
        model = NGSPool
        fields = [
            'id', 'pool_id', 'libraries', 'concentration_nm', 'molarity_nm',
            'volume_ul', 'pooled_by', 'pooled_at', 'notes'
        ]


# Result Serializers

class PCRResultSerializer(serializers.ModelSerializer):
    """Serializer for PCRResult model."""
    gene_target_symbol = serializers.CharField(source='gene_target.symbol', read_only=True)
    detection_display = serializers.CharField(source='get_detection_display', read_only=True)

    class Meta:
        model = PCRResult
        fields = [
            'id', 'result', 'gene_target', 'gene_target_symbol',
            'detection', 'detection_display', 'ct_value', 'quantity',
            'quantity_unit', 'fluorescence_channel', 'amplification_curve', 'notes'
        ]


class SequencingResultSerializer(serializers.ModelSerializer):
    """Serializer for SequencingResult model."""
    mapping_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = SequencingResult
        fields = [
            'id', 'result', 'total_reads', 'mapped_reads', 'mapping_rate',
            'coverage_mean', 'coverage_uniformity', 'q30_percentage',
            'mean_quality_score', 'on_target_percentage', 'duplicate_percentage',
            'sanger_trace_score', 'sanger_sequence_length', 'run_file', 'notes'
        ]


class VariantCallSerializer(serializers.ModelSerializer):
    """Serializer for VariantCall model."""
    gene_target_symbol = serializers.CharField(source='gene_target.symbol', read_only=True)
    classification_display = serializers.CharField(source='get_classification_display', read_only=True)
    zygosity_display = serializers.CharField(source='get_zygosity_display', read_only=True)

    class Meta:
        model = VariantCall
        fields = [
            'id', 'result', 'gene_target', 'gene_target_symbol',
            'chromosome', 'position', 'reference_allele', 'alternate_allele',
            'hgvs_cdna', 'hgvs_protein', 'classification', 'classification_display',
            'zygosity', 'zygosity_display', 'functional_consequence', 'variant_type',
            'dbsnp_id', 'clinvar_id', 'cosmic_id', 'allele_frequency', 'population_frequency',
            'is_reportable', 'notes'
        ]


class MolecularResultSerializer(serializers.ModelSerializer):
    """Serializer for MolecularResult model."""
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True)
    test_panel_name = serializers.CharField(source='test_panel.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interpretation_display = serializers.CharField(source='get_interpretation_display', read_only=True)
    pcr_results = PCRResultSerializer(many=True, read_only=True)
    sequencing_results = SequencingResultSerializer(many=True, read_only=True)
    variant_calls = VariantCallSerializer(many=True, read_only=True)

    class Meta:
        model = MolecularResult
        fields = [
            'id', 'sample', 'sample_id', 'test_panel', 'test_panel_name',
            'status', 'status_display', 'interpretation', 'interpretation_display',
            'summary', 'clinical_significance', 'recommendations', 'limitations',
            'performed_by', 'performed_date', 'reviewed_by', 'reviewed_date',
            'approved_by', 'approved_date', 'report_generated', 'report_file',
            'pcr_results', 'sequencing_results', 'variant_calls',
            'created_at', 'updated_at'
        ]


class MolecularResultListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MolecularResult list views."""
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True)
    test_panel_name = serializers.CharField(source='test_panel.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interpretation_display = serializers.CharField(source='get_interpretation_display', read_only=True)

    class Meta:
        model = MolecularResult
        fields = [
            'id', 'sample_id', 'test_panel_name', 'status_display',
            'interpretation_display', 'performed_date', 'approved_date'
        ]


# QC Serializers

class QCMetricDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for QCMetricDefinition model."""
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)

    class Meta:
        model = QCMetricDefinition
        fields = [
            'id', 'name', 'code', 'description', 'metric_type', 'metric_type_display',
            'min_value', 'max_value', 'target_value', 'warning_min', 'warning_max',
            'is_critical', 'is_active'
        ]


class ControlSampleSerializer(serializers.ModelSerializer):
    """Serializer for ControlSample model."""
    control_type_display = serializers.CharField(source='get_control_type_display', read_only=True)

    class Meta:
        model = ControlSample
        fields = [
            'id', 'name', 'control_type', 'control_type_display',
            'lot_number', 'expected_result', 'expected_value_min', 'expected_value_max',
            'gene_target', 'test_panel', 'expiration_date', 'is_active'
        ]


class QCRecordSerializer(serializers.ModelSerializer):
    """Serializer for QCRecord model."""
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = QCRecord
        fields = [
            'id', 'instrument_run', 'plate', 'metric', 'metric_name',
            'control_sample', 'numeric_value', 'text_value',
            'status', 'status_display', 'recorded_at', 'recorded_by',
            'reviewed_at', 'reviewed_by', 'notes'
        ]

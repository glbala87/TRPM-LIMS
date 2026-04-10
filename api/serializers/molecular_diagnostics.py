"""
Serializers for molecular_diagnostics app models.

NOTE: All Meta.fields lists below have been audited against the actual
model fields. If you change a model, regenerate the model field map with
`python manage.py shell` and update the matching serializer.
"""
from rest_framework import serializers
from molecular_diagnostics.models import (
    MolecularSample, MolecularSampleType, MolecularTestPanel, GeneTarget,
    MolecularResult, PCRResult, SequencingResult, VariantCall,
    PCRPlate, PlateWell, InstrumentRun, NGSLibrary, NGSPool,
    QCMetricDefinition, ControlSample, QCRecord,
    WorkflowDefinition, WorkflowStep, SampleHistory
)


# ---------------------------------------------------------------------------
# Sample Type
# ---------------------------------------------------------------------------
class MolecularSampleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MolecularSampleType
        fields = [
            'id', 'name', 'code', 'description', 'storage_temperature',
            'stability_hours', 'collection_instructions', 'is_active',
        ]


# ---------------------------------------------------------------------------
# Gene Target
# ---------------------------------------------------------------------------
class GeneTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneTarget
        fields = [
            'id', 'symbol', 'name', 'chromosome', 'genomic_coordinates',
            'transcript_id', 'clinical_significance', 'description', 'is_active',
        ]


class GeneTargetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneTarget
        fields = ['id', 'symbol', 'name', 'chromosome', 'clinical_significance', 'is_active']


# ---------------------------------------------------------------------------
# Test Panel
# ---------------------------------------------------------------------------
class MolecularTestPanelSerializer(serializers.ModelSerializer):
    gene_targets = GeneTargetListSerializer(many=True, read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)

    class Meta:
        model = MolecularTestPanel
        fields = [
            'id', 'name', 'code', 'description', 'test_type', 'test_type_display',
            'methodology', 'gene_targets', 'sample_requirements', 'tat_hours',
            'min_concentration_ng_ul', 'min_volume_ul', 'requires_extraction',
            'workflow', 'is_active', 'created_at', 'updated_at',
        ]


class MolecularTestPanelListSerializer(serializers.ModelSerializer):
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    gene_count = serializers.SerializerMethodField()

    class Meta:
        model = MolecularTestPanel
        fields = ['id', 'name', 'code', 'test_type_display', 'tat_hours', 'gene_count', 'is_active']

    def get_gene_count(self, obj):
        return obj.gene_targets.count()


# ---------------------------------------------------------------------------
# Sample
# ---------------------------------------------------------------------------
class MolecularSampleSerializer(serializers.ModelSerializer):
    sample_type_name = serializers.CharField(source='sample_type.name', read_only=True)
    workflow_status_display = serializers.CharField(source='get_workflow_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    storage_location_display = serializers.SerializerMethodField()

    class Meta:
        model = MolecularSample
        fields = [
            'id', 'sample_id', 'lab_order', 'sample_type', 'sample_type_name',
            'workflow_status', 'workflow_status_display', 'current_step',
            'test_panel', 'priority', 'priority_display',
            'collection_datetime', 'received_datetime',
            'storage_location', 'storage_location_display',
            'parent_sample', 'derivation_type', 'aliquot_number',
            'volume_ul', 'concentration_ng_ul', 'a260_280_ratio',
            'notes', 'is_active', 'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = ['id', 'sample_id', 'created_at', 'updated_at']

    def get_storage_location_display(self, obj):
        if obj.storage_location:
            return str(obj.storage_location)
        return None


class MolecularSampleListSerializer(serializers.ModelSerializer):
    sample_type_name = serializers.CharField(source='sample_type.name', read_only=True)
    workflow_status_display = serializers.CharField(source='get_workflow_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = MolecularSample
        fields = [
            'id', 'sample_id', 'sample_type_name', 'workflow_status', 'workflow_status_display',
            'priority', 'priority_display', 'received_datetime', 'is_active',
        ]


class MolecularSampleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MolecularSample
        fields = [
            'lab_order', 'sample_type', 'priority', 'collection_datetime',
            'volume_ul', 'notes', 'parent_sample', 'derivation_type',
        ]


class SampleTransitionSerializer(serializers.Serializer):
    """Workflow transition payload — kept generic since the choices live on the model."""
    new_status = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    qc_passed = serializers.BooleanField(required=False)
    qc_notes = serializers.CharField(required=False, allow_blank=True)


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------
class WorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow', 'name', 'code', 'order', 'description',
            'status_on_entry', 'requires_qc', 'qc_metrics',
            'estimated_duration_hours', 'is_terminal', 'allowed_transitions',
            'required_instruments',
        ]


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = ['id', 'name', 'code', 'description', 'is_active', 'steps', 'created_at', 'updated_at']


class SampleHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = SampleHistory
        fields = [
            'id', 'sample', 'from_status', 'to_status', 'from_step', 'to_step',
            'user', 'user_name', 'timestamp', 'notes', 'instrument_run',
            'qc_passed', 'qc_notes',
        ]


# ---------------------------------------------------------------------------
# Instrument runs / plates / NGS
# ---------------------------------------------------------------------------
class InstrumentRunSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InstrumentRun
        fields = [
            'id', 'run_id', 'instrument', 'instrument_name', 'status', 'status_display',
            'protocol_name', 'protocol_version', 'run_parameters',
            'run_date', 'start_time', 'end_time', 'operator', 'notes',
            'created_at', 'updated_at',
        ]


class InstrumentRunListSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InstrumentRun
        fields = ['id', 'run_id', 'instrument_name', 'status', 'status_display',
                  'start_time', 'end_time']


class PlateWellSerializer(serializers.ModelSerializer):
    sample_label = serializers.CharField(source='sample.sample_id', read_only=True)
    control_type_display = serializers.CharField(source='get_control_type_display', read_only=True)

    class Meta:
        model = PlateWell
        fields = [
            'id', 'plate', 'position', 'sample', 'sample_label',
            'control_sample', 'control_type', 'control_type_display',
            'replicate_number',
        ]


class PCRPlateSerializer(serializers.ModelSerializer):
    plate_type_display = serializers.CharField(source='get_plate_type_display', read_only=True)
    wells = PlateWellSerializer(many=True, read_only=True)

    class Meta:
        model = PCRPlate
        fields = [
            'id', 'barcode', 'plate_type', 'plate_type_display', 'name',
            'instrument_run', 'created_at', 'created_by', 'notes', 'wells',
        ]


class PCRPlateListSerializer(serializers.ModelSerializer):
    plate_type_display = serializers.CharField(source='get_plate_type_display', read_only=True)
    sample_count = serializers.SerializerMethodField()

    class Meta:
        model = PCRPlate
        fields = ['id', 'barcode', 'name', 'plate_type_display', 'instrument_run',
                  'created_at', 'sample_count']

    def get_sample_count(self, obj):
        return obj.wells.filter(sample__isnull=False).count()


class NGSLibrarySerializer(serializers.ModelSerializer):
    sample_label = serializers.CharField(source='sample.sample_id', read_only=True)

    class Meta:
        model = NGSLibrary
        fields = [
            'id', 'library_id', 'sample', 'sample_label', 'index_sequence', 'index_name',
            'concentration_ng_ul', 'fragment_size_bp', 'molarity_nm',
            'prep_date', 'prep_kit', 'prepared_by', 'qc_passed', 'notes',
        ]


class NGSPoolSerializer(serializers.ModelSerializer):
    libraries = NGSLibrarySerializer(many=True, read_only=True)

    class Meta:
        model = NGSPool
        fields = [
            'id', 'pool_id', 'libraries', 'concentration_ng_ul', 'molarity_nm',
            'volume_ul', 'pool_date', 'pooled_by', 'instrument_run', 'notes',
        ]


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
class PCRResultSerializer(serializers.ModelSerializer):
    target_gene_symbol = serializers.CharField(source='target_gene.symbol', read_only=True)

    class Meta:
        model = PCRResult
        fields = [
            'id', 'molecular_result', 'target_gene', 'target_gene_symbol',
            'is_detected', 'ct_value', 'quantity', 'quantity_unit',
            'fluorescence_channel', 'amplification_curve',
            'replicate_number', 'well_position',
        ]


class SequencingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingResult
        fields = [
            'id', 'molecular_result', 'total_reads', 'mapped_reads', 'mean_coverage',
            'coverage_uniformity', 'q30_percentage', 'quality_score',
            'on_target_percentage', 'duplicate_percentage',
            'trace_score', 'sequence_length', 'run_file',
        ]


class VariantCallSerializer(serializers.ModelSerializer):
    classification_display = serializers.CharField(source='get_classification_display', read_only=True)
    zygosity_display = serializers.CharField(source='get_zygosity_display', read_only=True)

    class Meta:
        model = VariantCall
        fields = [
            'id', 'molecular_result', 'gene',
            'chromosome', 'position', 'ref_allele', 'alt_allele',
            'hgvs_c', 'hgvs_p', 'classification', 'classification_display',
            'zygosity', 'zygosity_display', 'consequence', 'variant_type',
            'dbsnp_id', 'clinvar_id', 'cosmic_id', 'allele_frequency',
            'read_depth', 'population_frequency', 'is_reportable',
            'interpretation', 'notes',
        ]


class MolecularResultSerializer(serializers.ModelSerializer):
    sample_label = serializers.CharField(source='sample.sample_id', read_only=True)
    test_panel_name = serializers.CharField(source='test_panel.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interpretation_display = serializers.CharField(source='get_interpretation_display', read_only=True)
    pcr_results = PCRResultSerializer(many=True, read_only=True)
    sequencing_result = SequencingResultSerializer(read_only=True)
    variant_calls = VariantCallSerializer(many=True, read_only=True)

    class Meta:
        model = MolecularResult
        fields = [
            'id', 'sample', 'sample_label', 'test_panel', 'test_panel_name',
            'status', 'status_display', 'interpretation', 'interpretation_display',
            'result_summary', 'clinical_significance', 'recommendations', 'limitations',
            'performed_by', 'performed_at', 'reviewed_by', 'reviewed_at',
            'approved_by', 'approved_at', 'report_generated', 'report_generated_at',
            'report_file', 'pcr_results', 'sequencing_result', 'variant_calls',
            'notes', 'created_at', 'updated_at',
        ]


class MolecularResultListSerializer(serializers.ModelSerializer):
    sample_label = serializers.CharField(source='sample.sample_id', read_only=True)
    test_panel_name = serializers.CharField(source='test_panel.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    interpretation_display = serializers.CharField(source='get_interpretation_display', read_only=True)

    class Meta:
        model = MolecularResult
        fields = [
            'id', 'sample_label', 'test_panel_name', 'status', 'status_display',
            'interpretation_display', 'performed_at', 'approved_at',
        ]


# ---------------------------------------------------------------------------
# QC
# ---------------------------------------------------------------------------
class QCMetricDefinitionSerializer(serializers.ModelSerializer):
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)

    class Meta:
        model = QCMetricDefinition
        fields = [
            'id', 'name', 'code', 'description', 'metric_type', 'metric_type_display',
            'unit', 'min_acceptable', 'max_acceptable', 'target_value',
            'warning_min', 'warning_max', 'applicable_test_types',
            'is_critical', 'is_active',
        ]


class ControlSampleSerializer(serializers.ModelSerializer):
    control_type_display = serializers.CharField(source='get_control_type_display', read_only=True)

    class Meta:
        model = ControlSample
        fields = [
            'id', 'name', 'control_type', 'control_type_display',
            'lot_number', 'expected_result', 'expected_value_min', 'expected_value_max',
            'target_gene', 'test_panel', 'expiration_date',
            'storage_temperature', 'is_active', 'notes',
        ]


class QCRecordSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = QCRecord
        fields = [
            'id', 'instrument_run', 'pcr_plate', 'metric', 'metric_name',
            'control_sample', 'value', 'value_text',
            'status', 'status_display', 'passed',
            'recorded_at', 'recorded_by', 'reviewed_at', 'reviewed_by', 'notes',
        ]

"""
Serializers for single_cell app models.
"""
from rest_framework import serializers
from single_cell.models import (
    SingleCellSampleType, SingleCellSample, FeatureBarcode,
    FeatureBarcodePanel, SingleCellLibrary, CellCluster
)


class SingleCellSampleTypeSerializer(serializers.ModelSerializer):
    """Serializer for SingleCellSampleType model."""

    class Meta:
        model = SingleCellSampleType
        fields = ['id', 'code', 'name', 'description', 'target_cell_count', 'min_viability', 'is_active']


class FeatureBarcodeSerializer(serializers.ModelSerializer):
    """Serializer for FeatureBarcode model."""
    feature_type_display = serializers.CharField(source='get_feature_type_display', read_only=True)

    class Meta:
        model = FeatureBarcode
        fields = [
            'id', 'name', 'barcode_sequence', 'feature_type', 'feature_type_display',
            'target_antigen', 'clone', 'vendor', 'catalog_number', 'is_active'
        ]


class FeatureBarcodePanelSerializer(serializers.ModelSerializer):
    """Serializer for FeatureBarcodePanel model."""
    feature_barcodes = FeatureBarcodeSerializer(many=True, read_only=True)
    barcode_count = serializers.SerializerMethodField()

    class Meta:
        model = FeatureBarcodePanel
        fields = ['id', 'name', 'description', 'feature_barcodes', 'barcode_count', 'is_active']

    def get_barcode_count(self, obj):
        return obj.feature_barcodes.count()


class SingleCellLibrarySerializer(serializers.ModelSerializer):
    """Serializer for SingleCellLibrary model."""
    library_type_display = serializers.CharField(source='get_library_type_display', read_only=True)

    class Meta:
        model = SingleCellLibrary
        fields = [
            'id', 'single_cell_sample', 'ngs_library', 'library_type', 'library_type_display',
            'feature_barcode_panel', 'estimated_cells', 'fraction_reads_in_cells', 'created_at'
        ]


class CellClusterSerializer(serializers.ModelSerializer):
    """Serializer for CellCluster model."""

    class Meta:
        model = CellCluster
        fields = [
            'id', 'single_cell_sample', 'cluster_id', 'cluster_name', 'cell_count',
            'cell_type', 'markers', 'mean_genes', 'mean_umi'
        ]


class SingleCellSampleSerializer(serializers.ModelSerializer):
    """Serializer for SingleCellSample model."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sample_type_name = serializers.CharField(source='sample_type.name', read_only=True)
    libraries = SingleCellLibrarySerializer(many=True, read_only=True)
    clusters = CellClusterSerializer(many=True, read_only=True)

    class Meta:
        model = SingleCellSample
        fields = [
            'id', 'sample_id', 'molecular_sample', 'sample_type', 'sample_type_name',
            'platform', 'platform_display', 'status', 'status_display',
            'initial_cell_count', 'cell_concentration', 'viability_percent',
            'target_cell_recovery', 'actual_cell_recovery', 'is_nuclei', 'nuclei_concentration',
            'chip_id', 'chip_position', 'capture_time',
            'mean_reads_per_cell', 'median_genes_per_cell', 'median_umi_per_cell', 'sequencing_saturation',
            'notes', 'libraries', 'clusters', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SingleCellSampleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SingleCellSample list views."""
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SingleCellSample
        fields = [
            'id', 'sample_id', 'platform_display', 'status_display',
            'initial_cell_count', 'viability_percent', 'created_at'
        ]

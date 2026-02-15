# single_cell/admin.py

from django.contrib import admin
from .models import (
    SingleCellSampleType, SingleCellSample, FeatureBarcode,
    FeatureBarcodePanel, SingleCellLibrary, CellCluster
)


@admin.register(SingleCellSampleType)
class SingleCellSampleTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'target_cell_count', 'min_viability', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


class SingleCellLibraryInline(admin.TabularInline):
    model = SingleCellLibrary
    extra = 0
    fields = ['ngs_library', 'library_type', 'estimated_cells', 'fraction_reads_in_cells']


class CellClusterInline(admin.TabularInline):
    model = CellCluster
    extra = 0
    fields = ['cluster_id', 'cluster_name', 'cell_count', 'cell_type']


@admin.register(SingleCellSample)
class SingleCellSampleAdmin(admin.ModelAdmin):
    list_display = [
        'sample_id', 'molecular_sample', 'platform', 'status',
        'initial_cell_count', 'viability_percent', 'created_at'
    ]
    list_filter = ['platform', 'status', 'sample_type', 'is_nuclei']
    search_fields = ['sample_id', 'molecular_sample__sample_id', 'chip_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SingleCellLibraryInline, CellClusterInline]

    fieldsets = (
        (None, {
            'fields': ('sample_id', 'molecular_sample', 'sample_type', 'platform', 'status')
        }),
        ('Cell Metrics', {
            'fields': (
                'initial_cell_count', 'cell_concentration', 'viability_percent',
                'target_cell_recovery', 'actual_cell_recovery',
                'is_nuclei', 'nuclei_concentration'
            )
        }),
        ('Capture Info', {
            'fields': ('chip_id', 'chip_position', 'capture_time')
        }),
        ('Quality Metrics', {
            'fields': (
                'mean_reads_per_cell', 'median_genes_per_cell',
                'median_umi_per_cell', 'sequencing_saturation'
            ),
            'classes': ('collapse',)
        }),
        ('Notes & Timestamps', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FeatureBarcode)
class FeatureBarcodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode_sequence', 'feature_type', 'target_antigen', 'vendor', 'is_active']
    list_filter = ['feature_type', 'vendor', 'is_active']
    search_fields = ['name', 'barcode_sequence', 'target_antigen', 'clone']


@admin.register(FeatureBarcodePanel)
class FeatureBarcodePanelAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    filter_horizontal = ['feature_barcodes']

    def barcode_count(self, obj):
        return obj.feature_barcodes.count()
    barcode_count.short_description = 'Barcodes'


@admin.register(SingleCellLibrary)
class SingleCellLibraryAdmin(admin.ModelAdmin):
    list_display = [
        'single_cell_sample', 'ngs_library', 'library_type',
        'estimated_cells', 'fraction_reads_in_cells'
    ]
    list_filter = ['library_type']
    search_fields = ['single_cell_sample__sample_id', 'ngs_library__library_id']


@admin.register(CellCluster)
class CellClusterAdmin(admin.ModelAdmin):
    list_display = ['single_cell_sample', 'cluster_id', 'cluster_name', 'cell_count', 'cell_type']
    list_filter = ['cell_type']
    search_fields = ['single_cell_sample__sample_id', 'cluster_id', 'cell_type']

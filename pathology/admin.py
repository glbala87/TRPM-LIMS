# pathology/admin.py
"""
Django admin configuration for pathology module.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    PathologyType, InflammationType, TumorSite, TumorMorphology,
    SpecimenType, StainingProtocol,
    Histology, HistologyBlock, HistologySlide,
    Pathology, PathologyAddendum,
)


# Reference Models
@admin.register(PathologyType)
class PathologyTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'requires_gross', 'requires_microscopic', 'is_active']
    list_filter = ['requires_gross', 'requires_microscopic', 'is_active']
    search_fields = ['code', 'name']


@admin.register(InflammationType)
class InflammationTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(TumorSite)
class TumorSiteAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'body_system', 'parent', 'is_active']
    list_filter = ['body_system', 'is_active']
    search_fields = ['code', 'name']
    autocomplete_fields = ['parent']


@admin.register(TumorMorphology)
class TumorMorphologyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'behavior', 'full_code', 'is_active']
    list_filter = ['behavior', 'is_active']
    search_fields = ['code', 'name']


@admin.register(SpecimenType)
class SpecimenTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'collection_method', 'fixative', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(StainingProtocol)
class StainingProtocolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'stain_type', 'antibody', 'is_active']
    list_filter = ['stain_type', 'is_active']
    search_fields = ['code', 'name', 'antibody']


# Histology
class HistologySlideInline(admin.TabularInline):
    model = HistologySlide
    extra = 0
    readonly_fields = ['created_at']
    autocomplete_fields = ['stain']


class HistologyBlockInline(admin.TabularInline):
    model = HistologyBlock
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Histology)
class HistologyAdmin(admin.ModelAdmin):
    list_display = ['histology_id', 'patient_name', 'specimen_type', 'status_display', 'block_count', 'slide_count', 'is_stat', 'received_datetime']
    list_filter = ['status', 'specimen_type', 'fixation_type', 'is_stat', 'laboratory']
    search_fields = ['histology_id', 'surgical_number', 'lab_order__patient__first_name', 'lab_order__patient__last_name']
    readonly_fields = ['histology_id', 'created_at', 'updated_at']
    date_hierarchy = 'received_datetime'
    autocomplete_fields = ['laboratory', 'lab_order', 'molecular_sample', 'specimen_type', 'specimen_site', 'created_by']
    inlines = [HistologyBlockInline]

    fieldsets = (
        ('Identification', {
            'fields': ('histology_id', 'surgical_number', 'accession_number', 'h_and_e_barcode')
        }),
        ('Source', {
            'fields': ('laboratory', 'lab_order', 'molecular_sample')
        }),
        ('Specimen', {
            'fields': ('specimen_type', 'specimen_site', 'clinical_history')
        }),
        ('Fixation', {
            'fields': ('fixation_type', 'fixation_start', 'fixation_end')
        }),
        ('Processing', {
            'fields': ('block_count', 'slide_count')
        }),
        ('Quality', {
            'fields': ('tumor_cell_content', 'necrosis_percentage', 'tissue_adequacy')
        }),
        ('Gross', {
            'fields': ('gross_description', 'gross_measurements', 'gross_weight', 'gross_photo_count')
        }),
        ('Workflow', {
            'fields': ('status', 'is_stat', 'received_datetime', 'grossing_datetime', 'processed_datetime')
        }),
        ('Notes', {
            'fields': ('notes', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def patient_name(self, obj):
        return str(obj.patient)
    patient_name.short_description = 'Patient'

    def status_display(self, obj):
        colors = {
            'RECEIVED': '#3182ce',
            'GROSSING': '#805ad5',
            'PROCESSING': '#d69e2e',
            'STAINING': '#38a169',
            'READY': '#2f855a',
            'IN_REVIEW': '#d69e2e',
            'REPORTED': '#276749',
            'CANCELLED': '#718096',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(HistologyBlock)
class HistologyBlockAdmin(admin.ModelAdmin):
    list_display = ['histology', 'block_id', 'barcode', 'tissue_description', 'is_decalcified']
    list_filter = ['is_decalcified']
    search_fields = ['histology__histology_id', 'block_id', 'barcode']
    autocomplete_fields = ['histology', 'embedded_by']
    inlines = [HistologySlideInline]


@admin.register(HistologySlide)
class HistologySlideAdmin(admin.ModelAdmin):
    list_display = ['block', 'slide_number', 'stain', 'quality', 'is_scanned', 'requires_recut']
    list_filter = ['stain', 'quality', 'is_scanned', 'requires_recut']
    search_fields = ['block__histology__histology_id', 'barcode']
    autocomplete_fields = ['block', 'stain', 'stained_by']


# Pathology Report
class PathologyAddendumInline(admin.TabularInline):
    model = PathologyAddendum
    extra = 0
    readonly_fields = ['addendum_number', 'signed_date']


@admin.register(Pathology)
class PathologyAdmin(admin.ModelAdmin):
    list_display = ['pathology_id', 'patient', 'pathology_type', 'tnm_display', 'stage_group', 'status_display', 'pathologist', 'signed_date']
    list_filter = ['status', 'pathology_type', 'grade', 'margin_status', 'laboratory']
    search_fields = ['pathology_id', 'patient__first_name', 'patient__last_name', 'diagnosis']
    readonly_fields = ['pathology_id', 'tnm_stage', 'clinical_tnm_stage', 'signature_hash', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['laboratory', 'patient', 'histology', 'lab_order', 'pathology_type', 'tumor_site', 'tumor_morphology', 'pathologist', 'amended_by', 'created_by']
    inlines = [PathologyAddendumInline]

    fieldsets = (
        ('Identification', {
            'fields': ('pathology_id', 'laboratory', 'patient', 'lab_order', 'histology', 'pathology_type')
        }),
        ('Tumor Classification', {
            'fields': ('tumor_site', 'tumor_morphology')
        }),
        ('Pathological Staging', {
            'fields': ('t_stage', 'n_stage', 'm_stage', 'stage_group', 'tnm_stage', 'staging_system')
        }),
        ('Clinical Staging', {
            'fields': ('clinical_t_stage', 'clinical_n_stage', 'clinical_m_stage', 'clinical_stage_group', 'clinical_tnm_stage'),
            'classes': ('collapse',)
        }),
        ('Grade', {
            'fields': ('grade',)
        }),
        ('Margins', {
            'fields': ('margin_status', 'closest_margin_mm', 'margin_notes')
        }),
        ('Invasion', {
            'fields': ('lymphovascular_invasion', 'perineural_invasion')
        }),
        ('Lymph Nodes', {
            'fields': ('lymph_nodes_examined', 'lymph_nodes_positive')
        }),
        ('Report', {
            'fields': ('diagnosis', 'microscopic_description', 'gross_description', 'comment', 'clinical_correlation')
        }),
        ('IHC/Molecular', {
            'fields': ('ihc_results', 'molecular_findings'),
            'classes': ('collapse',)
        }),
        ('Synoptic Data', {
            'fields': ('synoptic_data',),
            'classes': ('collapse',)
        }),
        ('Workflow', {
            'fields': ('status',)
        }),
        ('Sign-off', {
            'fields': ('pathologist', 'signed_date', 'signature_hash')
        }),
        ('Amendment', {
            'fields': ('amended_by', 'amended_date', 'amendment_reason', 'original_diagnosis'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('is_active', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tnm_display(self, obj):
        return obj.tnm_stage or '-'
    tnm_display.short_description = 'pTNM'

    def status_display(self, obj):
        colors = {
            'DRAFT': '#718096',
            'PRELIMINARY': '#d69e2e',
            'PENDING_REVIEW': '#805ad5',
            'FINAL': '#38a169',
            'AMENDED': '#3182ce',
            'CANCELLED': '#c53030',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(PathologyAddendum)
class PathologyAddendumAdmin(admin.ModelAdmin):
    list_display = ['pathology', 'addendum_number', 'author', 'signed_date']
    search_fields = ['pathology__pathology_id', 'content']
    autocomplete_fields = ['pathology', 'author']

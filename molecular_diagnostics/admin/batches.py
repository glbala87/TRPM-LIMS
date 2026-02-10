# molecular_diagnostics/admin/batches.py

from django.contrib import admin
from django.utils.html import format_html
from ..models import InstrumentRun, PCRPlate, PlateWell, NGSLibrary, NGSPool


class PlateWellInline(admin.TabularInline):
    model = PlateWell
    extra = 0
    fields = ['position', 'sample', 'control_type', 'control_sample', 'replicate_number']
    autocomplete_fields = ['sample', 'control_sample']
    ordering = ['position']


@admin.register(InstrumentRun)
class InstrumentRunAdmin(admin.ModelAdmin):
    list_display = [
        'run_id', 'instrument', 'run_date', 'operator',
        'status_display', 'duration_display'
    ]
    list_filter = ['status', 'instrument', 'run_date']
    search_fields = ['run_id', 'instrument__name', 'operator__username']
    readonly_fields = ['run_id', 'created_at', 'updated_at']
    date_hierarchy = 'run_date'

    fieldsets = (
        ('Run Information', {
            'fields': ('run_id', 'instrument', 'run_date', 'operator')
        }),
        ('Status', {
            'fields': ('status', 'start_time', 'end_time')
        }),
        ('Protocol', {
            'fields': ('protocol_name', 'protocol_version')
        }),
        ('Parameters', {
            'fields': ('run_parameters',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        colors = {
            'PLANNED': '#3182ce',
            'IN_PROGRESS': '#d69e2e',
            'COMPLETED': '#38a169',
            'FAILED': '#c53030',
            'CANCELLED': '#718096',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def duration_display(self, obj):
        if obj.duration_hours:
            return f"{obj.duration_hours:.1f}h"
        return "-"
    duration_display.short_description = 'Duration'


@admin.register(PCRPlate)
class PCRPlateAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'plate_type', 'instrument_run', 'well_summary', 'created_at']
    list_filter = ['plate_type', 'created_at']
    search_fields = ['barcode', 'name']
    inlines = [PlateWellInline]

    fieldsets = (
        ('Plate Information', {
            'fields': ('barcode', 'name', 'plate_type')
        }),
        ('Run', {
            'fields': ('instrument_run',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def well_summary(self, obj):
        total = obj.well_count
        occupied = obj.wells.exclude(control_type='EMPTY').count()
        return f"{occupied}/{total} wells"
    well_summary.short_description = 'Wells'


@admin.register(NGSLibrary)
class NGSLibraryAdmin(admin.ModelAdmin):
    list_display = [
        'library_id', 'sample', 'index_name', 'concentration_ng_ul',
        'fragment_size_bp', 'qc_passed', 'prep_date'
    ]
    list_filter = ['qc_passed', 'prep_date', 'prep_kit']
    search_fields = ['library_id', 'sample__sample_id', 'index_sequence']
    autocomplete_fields = ['sample', 'prep_kit']
    date_hierarchy = 'prep_date'

    fieldsets = (
        ('Library Information', {
            'fields': ('library_id', 'sample')
        }),
        ('Index', {
            'fields': ('index_sequence', 'index_name')
        }),
        ('Metrics', {
            'fields': ('concentration_ng_ul', 'fragment_size_bp', 'molarity_nm')
        }),
        ('Preparation', {
            'fields': ('prep_date', 'prep_kit', 'prepared_by')
        }),
        ('QC', {
            'fields': ('qc_passed', 'notes')
        }),
    )


@admin.register(NGSPool)
class NGSPoolAdmin(admin.ModelAdmin):
    list_display = [
        'pool_id', 'library_count', 'concentration_ng_ul',
        'instrument_run', 'pool_date'
    ]
    list_filter = ['pool_date']
    search_fields = ['pool_id']
    filter_horizontal = ['libraries']
    date_hierarchy = 'pool_date'

    fieldsets = (
        ('Pool Information', {
            'fields': ('pool_id', 'libraries')
        }),
        ('Metrics', {
            'fields': ('concentration_ng_ul', 'molarity_nm', 'volume_ul')
        }),
        ('Sequencing', {
            'fields': ('instrument_run',)
        }),
        ('Preparation', {
            'fields': ('pool_date', 'pooled_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

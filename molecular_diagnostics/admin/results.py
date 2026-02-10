# molecular_diagnostics/admin/results.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from ..models import MolecularResult, PCRResult, SequencingResult, VariantCall


class PCRResultInline(admin.TabularInline):
    model = PCRResult
    extra = 0
    fields = ['target_gene', 'ct_value', 'is_detected', 'quantity', 'quantity_unit']
    autocomplete_fields = ['target_gene']


class VariantCallInline(admin.TabularInline):
    model = VariantCall
    extra = 0
    fields = ['gene', 'hgvs_c', 'hgvs_p', 'classification', 'is_reportable']
    autocomplete_fields = ['gene']


@admin.register(MolecularResult)
class MolecularResultAdmin(admin.ModelAdmin):
    list_display = [
        'sample', 'test_panel', 'status_display', 'interpretation',
        'approved_by', 'report_status', 'created_at'
    ]
    list_filter = ['status', 'interpretation', 'report_generated', 'test_panel']
    search_fields = ['sample__sample_id', 'test_panel__code']
    readonly_fields = ['created_at', 'updated_at', 'report_generated_at']
    date_hierarchy = 'created_at'
    inlines = [PCRResultInline, VariantCallInline]

    fieldsets = (
        ('Sample & Test', {
            'fields': ('sample', 'test_panel')
        }),
        ('Status', {
            'fields': ('status', 'interpretation')
        }),
        ('Results', {
            'fields': ('result_summary', 'clinical_significance', 'recommendations', 'limitations')
        }),
        ('Workflow', {
            'fields': (
                ('performed_by', 'performed_at'),
                ('reviewed_by', 'reviewed_at'),
                ('approved_by', 'approved_at'),
            )
        }),
        ('Report', {
            'fields': ('report_generated', 'report_generated_at', 'report_file')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_results', 'generate_reports']

    def status_display(self, obj):
        colors = {
            'PENDING': '#3182ce',
            'PRELIMINARY': '#d69e2e',
            'FINAL': '#38a169',
            'AMENDED': '#805ad5',
            'CANCELLED': '#718096',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def report_status(self, obj):
        if obj.report_generated:
            return format_html('<span style="color: green;">Generated</span>')
        return format_html('<span style="color: gray;">Not generated</span>')
    report_status.short_description = 'Report'

    @admin.action(description='Approve selected results')
    def approve_results(self, request, queryset):
        count = 0
        for result in queryset:
            if result.status in ['PENDING', 'PRELIMINARY']:
                result.approve(request.user)
                count += 1
        self.message_user(request, f'{count} results approved')

    @admin.action(description='Generate reports for selected results')
    def generate_reports(self, request, queryset):
        from ..services.report_generator import ReportGenerator

        try:
            generator = ReportGenerator()
        except ImportError as e:
            self.message_user(request, str(e), level=messages.ERROR)
            return

        count = 0
        for result in queryset:
            if result.is_reportable:
                try:
                    generator.generate_report(result, request.user)
                    count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'Error generating report for {result.sample.sample_id}: {e}',
                        level=messages.ERROR
                    )

        self.message_user(request, f'{count} reports generated')


@admin.register(PCRResult)
class PCRResultAdmin(admin.ModelAdmin):
    list_display = [
        'molecular_result', 'target_gene', 'ct_value',
        'is_detected', 'quantity', 'replicate_number'
    ]
    list_filter = ['is_detected', 'target_gene']
    search_fields = [
        'molecular_result__sample__sample_id', 'target_gene__symbol'
    ]
    autocomplete_fields = ['molecular_result', 'target_gene']


@admin.register(SequencingResult)
class SequencingResultAdmin(admin.ModelAdmin):
    list_display = [
        'molecular_result', 'total_reads', 'mapped_reads',
        'mean_coverage', 'q30_percentage'
    ]
    search_fields = ['molecular_result__sample__sample_id']

    fieldsets = (
        ('Result', {
            'fields': ('molecular_result',)
        }),
        ('Read Metrics', {
            'fields': ('total_reads', 'mapped_reads', 'on_target_percentage', 'duplicate_percentage')
        }),
        ('Quality Metrics', {
            'fields': ('mean_coverage', 'coverage_uniformity', 'quality_score', 'q30_percentage')
        }),
        ('Sanger-specific', {
            'fields': ('trace_score', 'sequence_length'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('run_file',)
        }),
    )


@admin.register(VariantCall)
class VariantCallAdmin(admin.ModelAdmin):
    list_display = [
        'gene', 'hgvs_display', 'classification_display',
        'zygosity', 'allele_frequency', 'is_reportable'
    ]
    list_filter = ['classification', 'zygosity', 'is_reportable', 'gene']
    search_fields = [
        'gene__symbol', 'hgvs_c', 'hgvs_p',
        'molecular_result__sample__sample_id'
    ]
    autocomplete_fields = ['molecular_result', 'gene']

    fieldsets = (
        ('Result', {
            'fields': ('molecular_result', 'gene')
        }),
        ('Variant', {
            'fields': ('chromosome', 'position', 'ref_allele', 'alt_allele')
        }),
        ('Nomenclature', {
            'fields': ('hgvs_c', 'hgvs_p', 'variant_type', 'consequence')
        }),
        ('Classification', {
            'fields': ('classification', 'zygosity')
        }),
        ('Metrics', {
            'fields': ('allele_frequency', 'read_depth', 'population_frequency')
        }),
        ('External IDs', {
            'fields': ('dbsnp_id', 'clinvar_id', 'cosmic_id'),
            'classes': ('collapse',)
        }),
        ('Reporting', {
            'fields': ('is_reportable', 'interpretation', 'notes')
        }),
    )

    def hgvs_display(self, obj):
        if obj.hgvs_c and obj.hgvs_p:
            return f"{obj.hgvs_c} ({obj.hgvs_p})"
        return obj.hgvs_c or obj.hgvs_p or f"{obj.ref_allele}>{obj.alt_allele}"
    hgvs_display.short_description = 'Variant'

    def classification_display(self, obj):
        colors = {
            'PATHOGENIC': '#c53030',
            'LIKELY_PATHOGENIC': '#dd6b20',
            'VUS': '#d69e2e',
            'LIKELY_BENIGN': '#38a169',
            'BENIGN': '#2f855a',
        }
        color = colors.get(obj.classification, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_classification_display()
        )
    classification_display.short_description = 'Classification'

# molecular_diagnostics/admin/annotations.py
"""
Admin interface for variant annotations.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from molecular_diagnostics.models import VariantAnnotation, AnnotationCache


@admin.register(AnnotationCache)
class AnnotationCacheAdmin(admin.ModelAdmin):
    """Admin interface for annotation cache entries."""

    list_display = [
        'variant_key',
        'dbsnp_id',
        'has_clinvar',
        'has_gnomad',
        'hit_count',
        'last_hit_at',
        'updated_at',
    ]
    list_filter = [
        'clinvar_fetched_at',
        'gnomad_fetched_at',
        'created_at',
    ]
    search_fields = [
        'variant_key',
        'dbsnp_id',
        'hgvs_notation',
    ]
    readonly_fields = [
        'variant_key',
        'hit_count',
        'last_hit_at',
        'created_at',
        'updated_at',
        'clinvar_data_preview',
        'gnomad_data_preview',
    ]
    ordering = ['-hit_count', '-updated_at']

    fieldsets = (
        ('Variant Identification', {
            'fields': ('variant_key', 'hgvs_notation', 'dbsnp_id')
        }),
        ('ClinVar Data', {
            'fields': ('clinvar_fetched_at', 'clinvar_data_preview'),
            'classes': ('collapse',),
        }),
        ('gnomAD Data', {
            'fields': ('gnomad_fetched_at', 'gnomad_data_preview'),
            'classes': ('collapse',),
        }),
        ('Usage Statistics', {
            'fields': ('hit_count', 'last_hit_at', 'created_at', 'updated_at'),
        }),
    )

    def has_clinvar(self, obj):
        return bool(obj.clinvar_data)
    has_clinvar.boolean = True
    has_clinvar.short_description = 'ClinVar'

    def has_gnomad(self, obj):
        return bool(obj.gnomad_data)
    has_gnomad.boolean = True
    has_gnomad.short_description = 'gnomAD'

    def clinvar_data_preview(self, obj):
        if not obj.clinvar_data:
            return "No data"
        import json
        return format_html(
            '<pre style="max-height: 300px; overflow: auto;">{}</pre>',
            json.dumps(obj.clinvar_data, indent=2)
        )
    clinvar_data_preview.short_description = 'ClinVar Data (JSON)'

    def gnomad_data_preview(self, obj):
        if not obj.gnomad_data:
            return "No data"
        import json
        return format_html(
            '<pre style="max-height: 300px; overflow: auto;">{}</pre>',
            json.dumps(obj.gnomad_data, indent=2)
        )
    gnomad_data_preview.short_description = 'gnomAD Data (JSON)'

    actions = ['clear_clinvar_cache', 'clear_gnomad_cache', 'clear_all_cache']

    @admin.action(description='Clear ClinVar cache for selected entries')
    def clear_clinvar_cache(self, request, queryset):
        queryset.update(clinvar_data={}, clinvar_fetched_at=None)
        self.message_user(request, f"Cleared ClinVar cache for {queryset.count()} entries.")

    @admin.action(description='Clear gnomAD cache for selected entries')
    def clear_gnomad_cache(self, request, queryset):
        queryset.update(gnomad_data={}, gnomad_fetched_at=None)
        self.message_user(request, f"Cleared gnomAD cache for {queryset.count()} entries.")

    @admin.action(description='Clear all cache for selected entries')
    def clear_all_cache(self, request, queryset):
        queryset.update(
            clinvar_data={},
            clinvar_fetched_at=None,
            gnomad_data={},
            gnomad_fetched_at=None
        )
        self.message_user(request, f"Cleared all cache for {queryset.count()} entries.")


@admin.register(VariantAnnotation)
class VariantAnnotationAdmin(admin.ModelAdmin):
    """Admin interface for variant annotations."""

    list_display = [
        'variant_display',
        'annotation_status',
        'clinical_significance_badge',
        'review_stars_display',
        'population_frequency_display',
        'is_rare_display',
        'updated_at',
    ]
    list_filter = [
        'annotation_status',
        'clinical_significance',
        'review_status',
        ('review_status_stars', admin.EmptyFieldListFilter),
        'clinvar_fetched_at',
        'gnomad_fetched_at',
    ]
    search_fields = [
        'variant_call__gene__symbol',
        'variant_call__hgvs_c',
        'variant_call__hgvs_p',
        'clinvar_variation_id',
        'variant_call__dbsnp_id',
    ]
    readonly_fields = [
        'variant_call',
        'cache_entry',
        'annotation_status',
        'error_message',
        'clinvar_fetched_at',
        'gnomad_fetched_at',
        'conditions_display',
        'submitters_display',
        'populations_display',
        'gene_constraint_display',
        'created_at',
        'updated_at',
    ]
    raw_id_fields = ['variant_call', 'cache_entry', 'annotated_by']
    ordering = ['-updated_at']

    fieldsets = (
        ('Variant', {
            'fields': ('variant_call', 'cache_entry', 'annotation_status', 'error_message')
        }),
        ('ClinVar - Clinical Significance', {
            'fields': (
                'clinvar_variation_id',
                'clinvar_allele_id',
                'clinical_significance',
                'clinical_significance_raw',
                'review_status',
                'review_status_stars',
                'last_evaluated',
                'submission_count',
                'clinvar_fetched_at',
            ),
        }),
        ('ClinVar - Conditions & Submitters', {
            'fields': ('conditions_display', 'submitters_display', 'pubmed_ids'),
            'classes': ('collapse',),
        }),
        ('gnomAD - Allele Frequencies', {
            'fields': (
                'genome_af',
                'exome_af',
                'genome_ac',
                'genome_an',
                'genome_homozygotes',
                'exome_ac',
                'exome_an',
                'exome_homozygotes',
                'max_population_af',
                'max_population',
                'gnomad_fetched_at',
            ),
        }),
        ('gnomAD - Population Details', {
            'fields': ('populations_display', 'flags'),
            'classes': ('collapse',),
        }),
        ('Gene Constraint', {
            'fields': ('gene_constraint_display',),
            'classes': ('collapse',),
        }),
        ('Additional Data', {
            'fields': ('in_silico_predictions',),
            'classes': ('collapse',),
        }),
        ('Audit', {
            'fields': ('annotated_by', 'created_at', 'updated_at'),
        }),
    )

    def variant_display(self, obj):
        vc = obj.variant_call
        url = reverse('admin:molecular_diagnostics_variantcall_change', args=[vc.id])
        return format_html(
            '<a href="{}">{}: {}</a>',
            url,
            vc.gene.symbol if vc.gene else 'Unknown',
            vc.hgvs_c or f"{vc.ref_allele}>{vc.alt_allele}"
        )
    variant_display.short_description = 'Variant'

    def clinical_significance_badge(self, obj):
        colors = {
            'PATHOGENIC': '#dc3545',
            'LIKELY_PATHOGENIC': '#fd7e14',
            'UNCERTAIN_SIGNIFICANCE': '#ffc107',
            'LIKELY_BENIGN': '#20c997',
            'BENIGN': '#28a745',
            'CONFLICTING': '#6c757d',
        }
        color = colors.get(obj.clinical_significance, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_clinical_significance_display() or 'Not Set'
        )
    clinical_significance_badge.short_description = 'Significance'

    def review_stars_display(self, obj):
        if obj.review_status_stars is None:
            return '-'
        filled = '★' * obj.review_status_stars
        empty = '☆' * (4 - obj.review_status_stars)
        return format_html(
            '<span style="color: #ffc107;">{}</span><span style="color: #ccc;">{}</span>',
            filled, empty
        )
    review_stars_display.short_description = 'Review'

    def population_frequency_display(self, obj):
        freq = obj.combined_frequency
        if freq is None:
            return '-'
        if freq < 0.0001:
            return format_html('<span style="color: #28a745;">&lt;0.01%</span>')
        elif freq < 0.01:
            return format_html('<span style="color: #20c997;">{:.4%}</span>', float(freq))
        elif freq < 0.05:
            return format_html('<span style="color: #ffc107;">{:.2%}</span>', float(freq))
        else:
            return format_html('<span style="color: #dc3545;">{:.2%}</span>', float(freq))
    population_frequency_display.short_description = 'Pop. Freq.'

    def is_rare_display(self, obj):
        if obj.is_rare is None:
            return '-'
        return obj.is_rare
    is_rare_display.boolean = True
    is_rare_display.short_description = 'Rare'

    def conditions_display(self, obj):
        if not obj.conditions:
            return "No conditions"
        import json
        return format_html(
            '<pre style="max-height: 200px; overflow: auto;">{}</pre>',
            json.dumps(obj.conditions, indent=2)
        )
    conditions_display.short_description = 'Associated Conditions'

    def submitters_display(self, obj):
        if not obj.submitters:
            return "No submitters"
        import json
        return format_html(
            '<pre style="max-height: 200px; overflow: auto;">{}</pre>',
            json.dumps(obj.submitters, indent=2)
        )
    submitters_display.short_description = 'ClinVar Submitters'

    def populations_display(self, obj):
        if not obj.populations:
            return "No population data"
        import json
        return format_html(
            '<pre style="max-height: 200px; overflow: auto;">{}</pre>',
            json.dumps(obj.populations, indent=2)
        )
    populations_display.short_description = 'Population Frequencies'

    def gene_constraint_display(self, obj):
        if not obj.gene_constraint:
            return "No constraint data"
        import json
        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.gene_constraint, indent=2)
        )
    gene_constraint_display.short_description = 'Gene Constraint Metrics'

    actions = ['trigger_annotation', 'refresh_annotation', 'clear_annotation']

    @admin.action(description='Trigger annotation for selected variants')
    def trigger_annotation(self, request, queryset):
        from molecular_diagnostics.tasks import annotate_variant_task

        count = 0
        for annotation in queryset:
            annotate_variant_task.delay(annotation.variant_call_id)
            count += 1

        self.message_user(request, f"Triggered annotation for {count} variants.")

    @admin.action(description='Refresh annotation (force)')
    def refresh_annotation(self, request, queryset):
        from molecular_diagnostics.tasks import annotate_variant_task

        count = 0
        for annotation in queryset:
            annotate_variant_task.delay(annotation.variant_call_id, force_refresh=True)
            count += 1

        self.message_user(request, f"Triggered refresh for {count} variants.")

    @admin.action(description='Clear annotation data')
    def clear_annotation(self, request, queryset):
        queryset.update(
            annotation_status='PENDING',
            clinical_significance='',
            review_status='',
            clinvar_variation_id='',
            clinvar_fetched_at=None,
            genome_af=None,
            exome_af=None,
            gnomad_fetched_at=None,
            error_message='',
        )
        self.message_user(request, f"Cleared annotation data for {queryset.count()} variants.")

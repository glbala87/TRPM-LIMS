# pharmacogenomics/admin.py
"""
Admin interface for pharmacogenomics models.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    PGxGene, StarAllele, Phenotype, Drug, DrugGeneInteraction,
    DrugRecommendation, PGxPanel, PGxResult, PGxDrugResult
)


@admin.register(PGxGene)
class PGxGeneAdmin(admin.ModelAdmin):
    list_display = [
        'symbol', 'name', 'category', 'uses_activity_score',
        'copy_number_relevant', 'allele_count', 'is_active'
    ]
    list_filter = ['category', 'uses_activity_score', 'copy_number_relevant', 'is_active']
    search_fields = ['symbol', 'name', 'ensembl_id', 'ncbi_gene_id']
    ordering = ['symbol']

    fieldsets = (
        ('Gene Information', {
            'fields': ('symbol', 'name', 'category', 'description')
        }),
        ('External References', {
            'fields': ('ensembl_id', 'ncbi_gene_id', 'pharmvar_id', 'gene_target'),
            'classes': ('collapse',),
        }),
        ('Genomic Location', {
            'fields': ('chromosome', 'start_position', 'end_position', 'reference_sequence'),
            'classes': ('collapse',),
        }),
        ('PGx Settings', {
            'fields': ('uses_activity_score', 'copy_number_relevant', 'clinical_importance')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def allele_count(self, obj):
        return obj.alleles.count()
    allele_count.short_description = 'Alleles'


class StarAlleleInline(admin.TabularInline):
    model = StarAllele
    extra = 0
    fields = ['name', 'function', 'activity_score', 'is_reference', 'is_active']
    ordering = ['name']


@admin.register(StarAllele)
class StarAlleleAdmin(admin.ModelAdmin):
    list_display = [
        'allele_display', 'gene', 'function', 'activity_score',
        'is_reference', 'is_active'
    ]
    list_filter = ['gene', 'function', 'is_reference', 'is_active']
    search_fields = ['name', 'gene__symbol', 'pharmvar_id']
    ordering = ['gene__symbol', 'name']
    raw_id_fields = ['gene']

    fieldsets = (
        ('Allele Information', {
            'fields': ('gene', 'name', 'function', 'activity_score', 'is_reference')
        }),
        ('Defining Variants', {
            'fields': ('defining_variants',),
        }),
        ('External References', {
            'fields': ('pharmvar_id', 'cpic_allele_id'),
            'classes': ('collapse',),
        }),
        ('Population Data', {
            'fields': ('population_frequencies',),
            'classes': ('collapse',),
        }),
        ('Clinical', {
            'fields': ('description', 'clinical_significance')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def allele_display(self, obj):
        return f"{obj.gene.symbol}{obj.name}"
    allele_display.short_description = 'Allele'


@admin.register(Phenotype)
class PhenotypeAdmin(admin.ModelAdmin):
    list_display = [
        'gene', 'code', 'name', 'activity_score_range', 'sort_order'
    ]
    list_filter = ['gene', 'code']
    search_fields = ['gene__symbol', 'name']
    ordering = ['gene__symbol', 'sort_order']

    def activity_score_range(self, obj):
        if obj.activity_score_min is not None and obj.activity_score_max is not None:
            return f"{obj.activity_score_min} - {obj.activity_score_max}"
        return "-"
    activity_score_range.short_description = 'AS Range'


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'drug_class', 'has_cpic_guideline', 'has_fda_label',
        'cpic_level', 'interaction_count', 'is_active'
    ]
    list_filter = ['drug_class', 'has_cpic_guideline', 'has_fda_label', 'cpic_level', 'is_active']
    search_fields = ['name', 'rxnorm_id', 'drugbank_id']
    ordering = ['name']

    fieldsets = (
        ('Drug Information', {
            'fields': ('name', 'brand_names', 'drug_class')
        }),
        ('External References', {
            'fields': ('rxnorm_id', 'drugbank_id', 'atc_code'),
            'classes': ('collapse',),
        }),
        ('Clinical Information', {
            'fields': ('description', 'mechanism_of_action')
        }),
        ('PGx Information', {
            'fields': ('has_cpic_guideline', 'has_fda_label', 'cpic_level')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def interaction_count(self, obj):
        return obj.gene_interactions.count()
    interaction_count.short_description = 'Gene Interactions'


class DrugRecommendationInline(admin.TabularInline):
    model = DrugRecommendation
    extra = 0
    fields = ['phenotype', 'action', 'recommendation_strength', 'is_active']


@admin.register(DrugGeneInteraction)
class DrugGeneInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'drug', 'gene', 'interaction_type', 'evidence_level', 'is_active'
    ]
    list_filter = ['gene', 'interaction_type', 'evidence_level', 'is_active']
    search_fields = ['drug__name', 'gene__symbol']
    ordering = ['drug__name', 'gene__symbol']
    raw_id_fields = ['drug', 'gene']
    inlines = [DrugRecommendationInline]

    fieldsets = (
        ('Interaction', {
            'fields': ('drug', 'gene', 'interaction_type', 'evidence_level')
        }),
        ('CPIC Information', {
            'fields': ('cpic_guideline_url', 'cpic_publication_pmid'),
            'classes': ('collapse',),
        }),
        ('Clinical Information', {
            'fields': ('description', 'clinical_summary')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(DrugRecommendation)
class DrugRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'drug_gene_display', 'phenotype', 'action_badge',
        'recommendation_strength', 'is_active'
    ]
    list_filter = ['action', 'recommendation_strength', 'is_active']
    search_fields = [
        'interaction__drug__name',
        'interaction__gene__symbol',
        'phenotype__name'
    ]
    raw_id_fields = ['interaction', 'phenotype']

    def drug_gene_display(self, obj):
        return f"{obj.interaction.drug.name} / {obj.interaction.gene.symbol}"
    drug_gene_display.short_description = 'Drug / Gene'

    def action_badge(self, obj):
        colors = {
            'STANDARD': '#28a745',
            'REDUCE': '#ffc107',
            'INCREASE': '#17a2b8',
            'AVOID': '#dc3545',
            'ALTERNATIVE': '#fd7e14',
            'MONITOR': '#6c757d',
            'CAUTION': '#ffc107',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = 'Action'


@admin.register(PGxPanel)
class PGxPanelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'gene_count', 'molecular_panel', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    filter_horizontal = ['genes']
    raw_id_fields = ['molecular_panel']

    def gene_count(self, obj):
        return obj.genes.count()
    gene_count.short_description = 'Genes'


class PGxDrugResultInline(admin.TabularInline):
    model = PGxDrugResult
    extra = 0
    fields = ['drug', 'action', 'is_actionable']
    readonly_fields = ['drug', 'action', 'is_actionable']


@admin.register(PGxResult)
class PGxResultAdmin(admin.ModelAdmin):
    list_display = [
        'result_display', 'gene', 'diplotype', 'phenotype_badge',
        'activity_score', 'status', 'created_at'
    ]
    list_filter = ['status', 'gene', 'phenotype']
    search_fields = [
        'molecular_result__sample__sample_id',
        'gene__symbol',
        'diplotype'
    ]
    ordering = ['-created_at']
    raw_id_fields = ['molecular_result', 'gene', 'panel', 'allele1', 'allele2', 'phenotype']
    readonly_fields = [
        'diplotype_display', 'detected_variants', 'calling_confidence',
        'called_at', 'reviewed_at', 'created_at', 'updated_at'
    ]
    inlines = [PGxDrugResultInline]

    fieldsets = (
        ('Result', {
            'fields': ('molecular_result', 'gene', 'panel', 'status')
        }),
        ('Diplotype', {
            'fields': ('allele1', 'allele2', 'diplotype', 'copy_number', 'has_hybrid')
        }),
        ('Phenotype', {
            'fields': ('activity_score', 'phenotype')
        }),
        ('Calling Details', {
            'fields': ('detected_variants', 'calling_method', 'calling_confidence'),
            'classes': ('collapse',),
        }),
        ('Clinical', {
            'fields': ('clinical_summary', 'interpretation', 'notes')
        }),
        ('Audit', {
            'fields': ('called_by', 'called_at', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def result_display(self, obj):
        return obj.molecular_result.sample.sample_id
    result_display.short_description = 'Sample'

    def phenotype_badge(self, obj):
        if not obj.phenotype:
            return '-'
        colors = {
            'PM': '#dc3545',
            'IM': '#ffc107',
            'NM': '#28a745',
            'RM': '#17a2b8',
            'UM': '#6f42c1',
        }
        color = colors.get(obj.phenotype.code, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.phenotype.name
        )
    phenotype_badge.short_description = 'Phenotype'

    actions = ['call_diplotypes', 'generate_recommendations']

    @admin.action(description='Call diplotypes for selected results')
    def call_diplotypes(self, request, queryset):
        from pharmacogenomics.services import DiplotypeService
        service = DiplotypeService()

        for result in queryset:
            try:
                service.recalculate_phenotype(result)
            except Exception as e:
                self.message_user(request, f"Failed for {result}: {e}", level='ERROR')

        self.message_user(request, f"Processed {queryset.count()} results.")

    @admin.action(description='Generate drug recommendations')
    def generate_recommendations(self, request, queryset):
        from pharmacogenomics.services import RecommendationService
        service = RecommendationService()

        count = 0
        for result in queryset.filter(status='CALLED'):
            recommendations = service.generate_recommendations(result)
            count += len(recommendations)

        self.message_user(request, f"Generated {count} recommendations.")


@admin.register(PGxDrugResult)
class PGxDrugResultAdmin(admin.ModelAdmin):
    list_display = [
        'pgx_result', 'drug', 'action', 'is_actionable'
    ]
    list_filter = ['action', 'is_actionable']
    search_fields = ['pgx_result__gene__symbol', 'drug__name']
    raw_id_fields = ['pgx_result', 'drug', 'recommendation']

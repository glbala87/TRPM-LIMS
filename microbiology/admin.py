# microbiology/admin.py
"""
Django admin configuration for microbiology module.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    TestMethod, BreakpointType, Host, SiteOfInfection, ASTGuideline,
    Kingdom, Phylum, OrganismClass, Order, Family, Genus, Organism,
    AntibioticClass, Antibiotic,
    Breakpoint,
    ASTPanel, ASTMPanelAntibiotic,
    MicrobiologySample, OrganismResult, ASTResult,
)


# Reference Models
@admin.register(TestMethod)
class TestMethodAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(BreakpointType)
class BreakpointTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'species', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'species']


@admin.register(SiteOfInfection)
class SiteOfInfectionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(ASTGuideline)
class ASTGuidelineAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'version', 'is_current', 'is_active']
    list_filter = ['name', 'is_current', 'is_active']
    search_fields = ['name', 'version']


# Taxonomy Models
@admin.register(Kingdom)
class KingdomAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(Phylum)
class PhylumAdmin(admin.ModelAdmin):
    list_display = ['name', 'kingdom', 'code']
    list_filter = ['kingdom']
    search_fields = ['name', 'code']


@admin.register(OrganismClass)
class OrganismClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'phylum', 'code']
    list_filter = ['phylum__kingdom']
    search_fields = ['name', 'code']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['name', 'organism_class', 'code']
    list_filter = ['organism_class__phylum__kingdom']
    search_fields = ['name', 'code']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'code']
    search_fields = ['name', 'code']


@admin.register(Genus)
class GenusAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'code']
    search_fields = ['name', 'code']


@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    list_display = ['organism_id', 'full_name', 'organism_type', 'gram_stain', 'whonet_org_code', 'is_active']
    list_filter = ['organism_type', 'gram_stain', 'is_pathogen', 'kingdom', 'is_active']
    search_fields = ['species', 'whonet_org_code', 'sct_code', 'genus__name']
    readonly_fields = ['organism_id', 'created_at', 'updated_at']
    autocomplete_fields = ['kingdom', 'phylum', 'organism_class', 'order', 'family', 'genus']

    fieldsets = (
        ('Identification', {
            'fields': ('organism_id', 'species', 'subspecies', 'common_name')
        }),
        ('Taxonomy', {
            'fields': ('kingdom', 'phylum', 'organism_class', 'order', 'family', 'genus')
        }),
        ('Codes', {
            'fields': ('whonet_org_code', 'sct_code', 'ncbi_tax_id')
        }),
        ('Characteristics', {
            'fields': ('organism_type', 'morphology', 'gram_stain', 'anaerobe', 'facultative_anaerobe')
        }),
        ('Clinical', {
            'fields': ('is_pathogen', 'is_opportunistic', 'biosafety_level')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


# Antibiotic Models
@admin.register(AntibioticClass)
class AntibioticClassAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent_class', 'is_active']
    list_filter = ['is_active', 'parent_class']
    search_fields = ['code', 'name']


@admin.register(Antibiotic)
class AntibioticAdmin(admin.ModelAdmin):
    list_display = ['abbreviation', 'name', 'antibiotic_class', 'whonet_abx_code', 'potency', 'is_active']
    list_filter = ['antibiotic_class', 'human_use', 'veterinary_use', 'is_active']
    search_fields = ['name', 'abbreviation', 'whonet_abx_code', 'atc_code']
    readonly_fields = ['antibiotic_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Info', {
            'fields': ('antibiotic_id', 'name', 'abbreviation', 'antibiotic_class')
        }),
        ('Codes', {
            'fields': ('whonet_abx_code', 'eucast_code', 'clsi_code', 'atc_code')
        }),
        ('LOINC Codes', {
            'fields': ('loinc_disk', 'loinc_mic', 'loinc_etest'),
            'classes': ('collapse',)
        }),
        ('Testing', {
            'fields': ('potency', 'disk_content_ug')
        }),
        ('Usage', {
            'fields': ('human_use', 'veterinary_use', 'screening_drug', 'confirmatory_drug')
        }),
        ('Spectrum', {
            'fields': ('spectrum_gram_positive', 'spectrum_gram_negative', 'spectrum_anaerobes', 'spectrum_fungi'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


# Breakpoint
@admin.register(Breakpoint)
class BreakpointAdmin(admin.ModelAdmin):
    list_display = ['guideline', 'antibiotic', 'organism_display', 'test_method', 'breakpoint_summary', 'is_active']
    list_filter = ['guideline', 'test_method', 'is_active']
    search_fields = ['organism__species', 'organism_group', 'antibiotic__name']
    autocomplete_fields = ['guideline', 'test_method', 'organism', 'antibiotic', 'host', 'site_of_infection']

    def organism_display(self, obj):
        return obj.organism.abbreviated_name if obj.organism else obj.organism_group
    organism_display.short_description = 'Organism'

    def breakpoint_summary(self, obj):
        if obj.susceptible_mic:
            return f"S<={obj.susceptible_mic} R>={obj.resistant_mic}"
        elif obj.susceptible_disk:
            return f"S>={obj.susceptible_disk} R<={obj.resistant_disk}"
        return "-"
    breakpoint_summary.short_description = 'Breakpoints'


# Panel
class ASTMPanelAntibioticInline(admin.TabularInline):
    model = ASTMPanelAntibiotic
    extra = 1
    autocomplete_fields = ['antibiotic']


@admin.register(ASTPanel)
class ASTPanelAdmin(admin.ModelAdmin):
    list_display = ['panel_id', 'code', 'name', 'laboratory', 'panel_type', 'antibiotic_count', 'is_active']
    list_filter = ['laboratory', 'panel_type', 'is_active']
    search_fields = ['code', 'name']
    readonly_fields = ['panel_id', 'created_at', 'updated_at']
    filter_horizontal = ['organisms']
    inlines = [ASTMPanelAntibioticInline]


# Results
class OrganismResultInline(admin.TabularInline):
    model = OrganismResult
    extra = 0
    readonly_fields = ['result_id', 'created_at']
    autocomplete_fields = ['organism', 'ast_panel']


@admin.register(MicrobiologySample)
class MicrobiologySampleAdmin(admin.ModelAdmin):
    list_display = ['sample_id', 'specimen_type', 'status_display', 'growth_observed', 'received_datetime']
    list_filter = ['status', 'specimen_type', 'growth_observed', 'laboratory']
    search_fields = ['sample_id', 'lab_order__patient__first_name', 'lab_order__patient__last_name']
    readonly_fields = ['sample_id', 'created_at', 'updated_at']
    date_hierarchy = 'received_datetime'
    inlines = [OrganismResultInline]

    def status_display(self, obj):
        colors = {
            'RECEIVED': '#3182ce',
            'IN_PROCESS': '#805ad5',
            'AST_PENDING': '#d69e2e',
            'AST_COMPLETE': '#38a169',
            'REPORTED': '#276749',
            'CANCELLED': '#718096',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'


class ASTResultInline(admin.TabularInline):
    model = ASTResult
    extra = 0
    readonly_fields = ['created_at']
    autocomplete_fields = ['antibiotic']


@admin.register(OrganismResult)
class OrganismResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'sample', 'organism', 'quantity', 'identification_method', 'is_significant']
    list_filter = ['identification_method', 'is_significant', 'is_contaminant', 'quantity']
    search_fields = ['result_id', 'sample__sample_id', 'organism__species']
    readonly_fields = ['result_id', 'created_at', 'updated_at']
    autocomplete_fields = ['sample', 'organism', 'ast_panel']
    inlines = [ASTResultInline]


@admin.register(ASTResult)
class ASTResultAdmin(admin.ModelAdmin):
    list_display = ['organism_result', 'antibiotic', 'raw_value', 'interpretation_display', 'test_method', 'is_reported']
    list_filter = ['interpretation', 'test_method', 'is_manual_override', 'is_reported']
    search_fields = ['organism_result__result_id', 'antibiotic__name']
    autocomplete_fields = ['organism_result', 'antibiotic', 'interpretation_guideline', 'breakpoint_used']

    def interpretation_display(self, obj):
        colors = {
            'S': '#38a169',
            'I': '#d69e2e',
            'R': '#c53030',
            'SDD': '#805ad5',
            'NS': '#c53030',
            'NI': '#718096',
        }
        color = colors.get(obj.interpretation, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_interpretation_display()
        )
    interpretation_display.short_description = 'Interpretation'

# molecular_diagnostics/admin/tests.py

from django.contrib import admin
from ..models import GeneTarget, MolecularTestPanel


@admin.register(GeneTarget)
class GeneTargetAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'chromosome', 'is_active']
    list_filter = ['is_active', 'chromosome']
    search_fields = ['symbol', 'name', 'transcript_id']
    ordering = ['symbol']

    fieldsets = (
        ('Gene Information', {
            'fields': ('name', 'symbol', 'description')
        }),
        ('Genomic Details', {
            'fields': ('chromosome', 'genomic_coordinates', 'transcript_id')
        }),
        ('Clinical', {
            'fields': ('clinical_significance',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(MolecularTestPanel)
class MolecularTestPanelAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'test_type', 'tat_hours',
        'gene_count', 'is_active'
    ]
    list_filter = ['test_type', 'is_active', 'requires_extraction']
    search_fields = ['name', 'code']
    filter_horizontal = ['gene_targets', 'reagent_kits']
    ordering = ['name']

    fieldsets = (
        ('Test Information', {
            'fields': ('name', 'code', 'test_type', 'description')
        }),
        ('Gene Targets', {
            'fields': ('gene_targets',)
        }),
        ('Methodology', {
            'fields': ('methodology', 'sample_requirements', 'requires_extraction')
        }),
        ('SLA', {
            'fields': ('tat_hours',)
        }),
        ('Requirements', {
            'fields': ('min_concentration_ng_ul', 'min_volume_ul')
        }),
        ('Workflow & Reagents', {
            'fields': ('workflow', 'reagent_kits'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def gene_count(self, obj):
        return obj.gene_targets.count()
    gene_count.short_description = 'Genes'

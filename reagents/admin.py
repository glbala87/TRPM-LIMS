# reagents/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Reagent, ReagentCategory, ReagentUsage, MolecularReagent
from .forms import ReagentForm  # Import the ReagentForm

# Reagent Category Admin
class ReagentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

# Reagent Admin
class ReagentAdmin(admin.ModelAdmin):
    form = ReagentForm  # Specify the form to use in the admin

    list_display = ('name', 'category', 'vendor', 'item_received_date', 'expiration_date', 'quantity_in_stock', 'on_order')
    list_filter = ('category', 'vendor', 'on_order')
    search_fields = ('name', 'lot_number', 'category')
    ordering = ('name',)

    def reorder_check(self, obj):
        return obj.is_below_reorder_level()
    reorder_check.boolean = True
    reorder_check.short_description = 'Below Reorder Level'

# Reagent Usage Admin
class ReagentUsageAdmin(admin.ModelAdmin):
    list_display = ('reagent', 'quantity_used', 'usage_date', 'used_in_lab_order')
    list_filter = ('usage_date', 'used_in_lab_order')
    search_fields = ('reagent__name', 'used_in_lab_order__id')
    ordering = ('usage_date',)

# Molecular Reagent Admin
@admin.register(MolecularReagent)
class MolecularReagentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'lot_number', 'manufacturer',
        'storage_temperature', 'expiration_status', 'stock_status', 'is_active'
    ]
    list_filter = ['category', 'storage_temperature', 'is_active', 'is_validated']
    search_fields = ['name', 'lot_number', 'catalog_number', 'sequence']
    filter_horizontal = ['linked_test_panels', 'linked_gene_targets']
    date_hierarchy = 'received_date'

    fieldsets = (
        ('Reagent Information', {
            'fields': ('name', 'catalog_number', 'lot_number', 'category')
        }),
        ('Supplier', {
            'fields': ('manufacturer', 'supplier')
        }),
        ('Primer/Probe Details', {
            'fields': ('sequence', 'tm_celsius', 'gc_content', 'modification_5prime', 'modification_3prime'),
            'classes': ('collapse',),
            'description': 'For primers and probes only'
        }),
        ('Concentration & Storage', {
            'fields': (
                ('concentration', 'concentration_unit'),
                'storage_temperature', 'storage_location'
            )
        }),
        ('Stock Management', {
            'fields': (
                ('initial_volume_ul', 'current_volume_ul'),
                ('reactions_per_kit', 'reactions_remaining')
            )
        }),
        ('Dates', {
            'fields': (
                'received_date', 'opened_date', 'expiration_date',
                'stability_after_opening_days'
            )
        }),
        ('Linked Tests', {
            'fields': ('linked_test_panels', 'linked_gene_targets')
        }),
        ('Validation', {
            'fields': ('is_validated', 'validation_date', 'validation_notes')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
    )

    def expiration_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">EXPIRED</span>')
        return obj.effective_expiration
    expiration_status.short_description = 'Expiration'

    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: orange;">LOW</span>')
        return format_html('<span style="color: green;">OK</span>')
    stock_status.short_description = 'Stock'


# Registering models to admin interface
admin.site.register(ReagentCategory, ReagentCategoryAdmin)
admin.site.register(Reagent, ReagentAdmin)
admin.site.register(ReagentUsage, ReagentUsageAdmin)

# reagents/models.py

from django.db import models
from django.utils import timezone


MOLECULAR_CATEGORY_CHOICES = [
    ('PRIMER', 'Primer'),
    ('PROBE', 'Probe'),
    ('ENZYME_KIT', 'Enzyme Kit'),
    ('LIBRARY_PREP', 'Library Prep Kit'),
    ('EXTRACTION_KIT', 'Extraction Kit'),
    ('MASTER_MIX', 'Master Mix'),
    ('INDEX_KIT', 'Index/Barcode Kit'),
    ('CONTROL', 'Control Material'),
    ('BUFFER', 'Buffer/Solution'),
    ('OTHER', 'Other'),
]


class ReagentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Reagent(models.Model):
    VENDOR_CHOICES = [
        ('BIG', 'BIG'),
        ('SMALL', 'SMALL'),
    ]
    
    CATEGORY_CHOICES = [
        ('BIOASSAY_SNIBE', 'BIOASSAY SNIBE'),
        ('MAGLUMI_SNIBE', 'MAGLUMI SNIBE'),
        ('BIG', 'BIG'),
    ]
    
    item_received_date = models.DateField(null=True, blank=True)  # Temporarily allow null
    expiration_date = models.DateField()
    lot_number = models.CharField(max_length=50, null=True, blank=True)  # Temporarily allow null
    name = models.CharField(max_length=200)
    vendor = models.CharField(max_length=5, choices=VENDOR_CHOICES, null=True, blank=True)  # Temporarily allow null
    received_qty = models.IntegerField(null=True, blank=True)  # Temporarily allow null
    opening_quantity = models.IntegerField(null=True, blank=True)  # Temporarily allow null
    quantity_in_stock = models.IntegerField()
    on_order = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f'{self.name} ({self.lot_number}) - {self.vendor}'
    
    def is_below_reorder_level(self):
        return self.quantity_in_stock <= self.opening_quantity

# Reagent Usage model as before
class ReagentUsage(models.Model):
    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()  # Quantity used
    used_in_lab_order = models.ForeignKey('lab_management.LabOrder', on_delete=models.SET_NULL, null=True, blank=True)
    usage_date = models.DateField(auto_now_add=True)  # Date the reagent was used

    def __str__(self):
        return f"{self.quantity_used} {self.reagent.name} used on {self.usage_date}"


class MolecularReagent(models.Model):
    """Reagents specific to molecular diagnostics"""

    STORAGE_TEMP_CHOICES = [
        ('MINUS80', '-80°C'),
        ('MINUS20', '-20°C'),
        ('REFRIGERATED', '2-8°C'),
        ('ROOM_TEMP', 'Room Temperature'),
    ]

    name = models.CharField(max_length=200)
    catalog_number = models.CharField(max_length=100, blank=True)
    lot_number = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=MOLECULAR_CATEGORY_CHOICES,
        default='OTHER'
    )

    manufacturer = models.CharField(max_length=200, blank=True)
    supplier = models.CharField(max_length=200, blank=True)

    # For primers and probes
    sequence = models.CharField(
        max_length=500,
        blank=True,
        help_text="Nucleotide sequence (for primers/probes)"
    )
    tm_celsius = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Melting temperature in °C"
    )
    gc_content = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GC content percentage"
    )
    modification_5prime = models.CharField(
        max_length=100,
        blank=True,
        help_text="5' modification (e.g., FAM, HEX)"
    )
    modification_3prime = models.CharField(
        max_length=100,
        blank=True,
        help_text="3' modification (e.g., BHQ1, TAMRA)"
    )

    # Concentration and storage
    concentration = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    concentration_unit = models.CharField(
        max_length=20,
        blank=True,
        help_text="e.g., µM, ng/µL, Units/µL"
    )
    storage_temperature = models.CharField(
        max_length=20,
        choices=STORAGE_TEMP_CHOICES,
        default='MINUS20'
    )
    storage_location = models.CharField(max_length=200, blank=True)

    # Stock management
    initial_volume_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Initial volume in µL"
    )
    current_volume_ul = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current remaining volume in µL"
    )
    reactions_per_kit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of reactions (for kits)"
    )
    reactions_remaining = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    # Dates
    received_date = models.DateField(default=timezone.now)
    opened_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField()
    stability_after_opening_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Days stable after opening"
    )

    # Associated tests
    linked_test_panels = models.ManyToManyField(
        'molecular_diagnostics.MolecularTestPanel',
        related_name='reagents',
        blank=True
    )
    linked_gene_targets = models.ManyToManyField(
        'molecular_diagnostics.GeneTarget',
        related_name='reagents',
        blank=True,
        help_text="Gene targets this reagent is used for"
    )

    is_active = models.BooleanField(default=True)
    is_validated = models.BooleanField(
        default=False,
        help_text="Has this reagent been validated for use?"
    )
    validation_date = models.DateField(null=True, blank=True)
    validation_notes = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Molecular Reagent"
        verbose_name_plural = "Molecular Reagents"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.lot_number}) - {self.get_category_display()}"

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now().date()

    @property
    def is_low_stock(self):
        if self.reactions_remaining is not None:
            return self.reactions_remaining < 10
        if self.current_volume_ul is not None and self.initial_volume_ul:
            return self.current_volume_ul / self.initial_volume_ul < 0.2
        return False

    @property
    def effective_expiration(self):
        """Return the earlier of expiration date or stability-after-opening date"""
        if self.opened_date and self.stability_after_opening_days:
            from datetime import timedelta
            stability_expiry = self.opened_date + timedelta(days=self.stability_after_opening_days)
            return min(stability_expiry, self.expiration_date)
        return self.expiration_date

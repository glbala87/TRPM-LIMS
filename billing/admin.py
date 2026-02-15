# billing/admin.py

from django.contrib import admin
from .models import (
    PriceList, ServicePrice, Client,
    Invoice, InvoiceItem, Payment, QuotationRequest
)


class ServicePriceInline(admin.TabularInline):
    model = ServicePrice
    extra = 0
    fields = ['service_code', 'service_name', 'unit_price', 'cost_price', 'is_active']


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'currency', 'effective_from', 'effective_to', 'is_default', 'is_active']
    list_filter = ['currency', 'is_default', 'is_active']
    search_fields = ['code', 'name']
    inlines = [ServicePriceInline]

    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description', 'currency')
        }),
        ('Validity', {
            'fields': ('effective_from', 'effective_to')
        }),
        ('Status', {
            'fields': ('is_default', 'is_active')
        }),
    )


@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = [
        'service_code', 'service_name', 'price_list', 'unit_price',
        'cost_price', 'volume_discount_enabled', 'is_active'
    ]
    list_filter = ['price_list', 'volume_discount_enabled', 'is_active']
    search_fields = ['service_code', 'service_name']
    raw_id_fields = ['test_panel']

    fieldsets = (
        (None, {
            'fields': ('price_list', 'service_code', 'service_name', 'description', 'test_panel')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'cost_price', 'min_quantity')
        }),
        ('Volume Discounts', {
            'fields': ('volume_discount_enabled', 'volume_discount_tiers'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'client_id', 'name', 'client_type', 'payment_terms',
        'discount_percent', 'is_active'
    ]
    list_filter = ['client_type', 'payment_terms', 'is_active', 'country']
    search_fields = ['client_id', 'name', 'email', 'contact_name']
    readonly_fields = ['client_id', 'created_at']

    fieldsets = (
        (None, {
            'fields': ('client_id', 'name', 'client_type')
        }),
        ('Contact', {
            'fields': ('contact_name', 'email', 'phone', 'address', 'city', 'country')
        }),
        ('Billing', {
            'fields': ('tax_id', 'price_list', 'payment_terms', 'credit_limit', 'discount_percent')
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'discount_percent', 'line_total']
    readonly_fields = ['line_total']
    raw_id_fields = ['service_price', 'molecular_sample']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['payment_id', 'amount', 'payment_method', 'payment_date', 'reference_number']
    readonly_fields = ['payment_id']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'client', 'status', 'invoice_date',
        'due_date', 'total_amount', 'paid_amount', 'balance_due'
    ]
    list_filter = ['status', 'invoice_date']
    search_fields = ['invoice_number', 'client__name', 'client__client_id']
    readonly_fields = [
        'invoice_number', 'subtotal', 'tax_amount', 'total_amount',
        'paid_amount', 'balance_due', 'created_at'
    ]
    inlines = [InvoiceItemInline, PaymentInline]
    date_hierarchy = 'invoice_date'

    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'client', 'price_list', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'sent_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'discount_amount', 'tax_rate', 'tax_amount', 'total_amount', 'paid_amount', 'balance_due')
        }),
        ('Details', {
            'fields': ('billing_address', 'notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_sent', 'recalculate_totals']

    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.filter(status='PENDING').update(status='SENT', sent_date=timezone.now().date())
        self.message_user(request, f"Marked {queryset.count()} invoices as sent.")
    mark_as_sent.short_description = "Mark selected invoices as sent"

    def recalculate_totals(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_totals()
            invoice.save()
        self.message_user(request, f"Recalculated totals for {queryset.count()} invoices.")
    recalculate_totals.short_description = "Recalculate invoice totals"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'discount_percent', 'line_total']
    list_filter = ['invoice__status']
    search_fields = ['invoice__invoice_number', 'description']
    raw_id_fields = ['service_price', 'molecular_sample']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'invoice', 'amount', 'payment_method',
        'payment_date', 'received_by'
    ]
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_id', 'invoice__invoice_number', 'reference_number']
    readonly_fields = ['payment_id', 'created_at']
    date_hierarchy = 'payment_date'

    fieldsets = (
        (None, {
            'fields': ('payment_id', 'invoice', 'amount', 'payment_method', 'payment_date')
        }),
        ('Details', {
            'fields': ('reference_number', 'notes')
        }),
        ('Audit', {
            'fields': ('received_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuotationRequest)
class QuotationRequestAdmin(admin.ModelAdmin):
    list_display = [
        'quote_number', 'client', 'status', 'quote_date',
        'valid_until', 'total_amount', 'converted_to_invoice'
    ]
    list_filter = ['status', 'quote_date']
    search_fields = ['quote_number', 'client__name']
    readonly_fields = ['quote_number', 'created_at']

    fieldsets = (
        (None, {
            'fields': ('quote_number', 'client', 'status')
        }),
        ('Dates', {
            'fields': ('quote_date', 'valid_until')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'discount_amount', 'total_amount')
        }),
        ('Details', {
            'fields': ('terms_and_conditions', 'notes'),
            'classes': ('collapse',)
        }),
        ('Conversion', {
            'fields': ('converted_to_invoice',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

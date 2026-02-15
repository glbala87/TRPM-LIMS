# transfers/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Transfer, TransferItem


class TransferItemInline(admin.TabularInline):
    """Inline admin for transfer items."""
    model = TransferItem
    extra = 1
    fields = [
        'sample_id', 'quantity', 'container_type', 'storage_position',
        'condition_on_departure', 'is_received', 'has_discrepancy'
    ]
    readonly_fields = ['is_received']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'RECEIVED':
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    """Admin interface for Transfer model."""

    list_display = [
        'transfer_number', 'source_location', 'destination_location',
        'status_badge', 'transfer_date', 'courier', 'tracking_number',
        'shipment_conditions', 'items_count', 'initiated_by'
    ]
    list_filter = [
        'status', 'shipment_conditions', 'courier',
        ('transfer_date', admin.DateFieldListFilter),
    ]
    search_fields = [
        'transfer_number', 'source_location', 'destination_location',
        'tracking_number', 'courier'
    ]
    readonly_fields = [
        'transfer_number', 'created_at', 'updated_at',
        'actual_arrival_date', 'total_items', 'total_quantity'
    ]
    date_hierarchy = 'transfer_date'
    inlines = [TransferItemInline]

    fieldsets = (
        ('Transfer Information', {
            'fields': (
                'transfer_number', 'status',
                ('source_location', 'destination_location'),
            )
        }),
        ('Dates', {
            'fields': (
                'transfer_date', 'expected_arrival_date', 'actual_arrival_date'
            )
        }),
        ('Shipping Details', {
            'fields': (
                ('courier', 'tracking_number'),
                'shipment_conditions',
            )
        }),
        ('Personnel', {
            'fields': (
                ('initiated_by', 'received_by'),
            )
        }),
        ('Notes', {
            'fields': ('notes', 'special_instructions'),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('total_items', 'total_quantity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_in_transit', 'mark_received', 'cancel_transfers']

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'PENDING': '#f59e0b',      # Amber
            'IN_TRANSIT': '#3b82f6',   # Blue
            'RECEIVED': '#10b981',     # Green
            'CANCELLED': '#ef4444',    # Red
        }
        color = colors.get(obj.status, '#6b7280')

        # Check if overdue
        if obj.is_overdue:
            icon = ' (OVERDUE)'
            color = '#ef4444'
        else:
            icon = ''

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}{}</span>',
            color, obj.get_status_display(), icon
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def items_count(self, obj):
        """Display count of items in the transfer."""
        count = obj.total_items
        quantity = obj.total_quantity
        return f"{count} items ({quantity} samples)"
    items_count.short_description = 'Items'

    def mark_in_transit(self, request, queryset):
        """Mark selected transfers as in transit."""
        updated = 0
        for transfer in queryset.filter(status='PENDING'):
            transfer.mark_in_transit(request.user)
            updated += 1
        self.message_user(
            request,
            f"{updated} transfer(s) marked as in transit."
        )
    mark_in_transit.short_description = "Mark selected transfers as In Transit"

    def mark_received(self, request, queryset):
        """Mark selected transfers as received."""
        updated = 0
        for transfer in queryset.filter(status='IN_TRANSIT'):
            transfer.mark_received(request.user)
            updated += 1
        self.message_user(
            request,
            f"{updated} transfer(s) marked as received."
        )
    mark_received.short_description = "Mark selected transfers as Received"

    def cancel_transfers(self, request, queryset):
        """Cancel selected transfers."""
        updated = 0
        for transfer in queryset.exclude(status__in=['RECEIVED', 'CANCELLED']):
            transfer.cancel(reason="Cancelled by admin")
            updated += 1
        self.message_user(
            request,
            f"{updated} transfer(s) cancelled."
        )
    cancel_transfers.short_description = "Cancel selected transfers"

    def get_queryset(self, request):
        """Optimize queries with prefetch."""
        return super().get_queryset(request).prefetch_related('items')


@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    """Admin interface for TransferItem model."""

    list_display = [
        'sample_id', 'transfer_link', 'quantity', 'container_type',
        'is_received_badge', 'has_discrepancy_badge', 'received_at'
    ]
    list_filter = [
        'is_received', 'has_discrepancy',
        ('transfer__transfer_date', admin.DateFieldListFilter),
        'transfer__status'
    ]
    search_fields = [
        'sample_id', 'transfer__transfer_number',
        'transfer__source_location', 'transfer__destination_location'
    ]
    readonly_fields = ['received_at']

    fieldsets = (
        ('Item Information', {
            'fields': (
                'transfer', 'sample_id', 'lab_order', 'quantity'
            )
        }),
        ('Container Details', {
            'fields': (
                'container_type', 'storage_position'
            )
        }),
        ('Condition', {
            'fields': (
                'condition_on_departure', 'condition_on_arrival'
            )
        }),
        ('Receipt Status', {
            'fields': (
                'is_received', 'received_at', 'received_by'
            )
        }),
        ('Discrepancy', {
            'fields': (
                'has_discrepancy', 'discrepancy_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def transfer_link(self, obj):
        """Link to the parent transfer."""
        url = reverse('admin:transfers_transfer_change', args=[obj.transfer.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.transfer.transfer_number
        )
    transfer_link.short_description = 'Transfer'
    transfer_link.admin_order_field = 'transfer__transfer_number'

    def is_received_badge(self, obj):
        """Display received status as a badge."""
        if obj.is_received:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">Yes</span>'
            )
        return format_html(
            '<span style="color: #6b7280;">No</span>'
        )
    is_received_badge.short_description = 'Received'
    is_received_badge.admin_order_field = 'is_received'

    def has_discrepancy_badge(self, obj):
        """Display discrepancy status as a badge."""
        if obj.has_discrepancy:
            return format_html(
                '<span style="background-color: #ef4444; color: white; '
                'padding: 2px 8px; border-radius: 8px; font-size: 11px;">Yes</span>'
            )
        return format_html(
            '<span style="color: #10b981;">No</span>'
        )
    has_discrepancy_badge.short_description = 'Discrepancy'
    has_discrepancy_badge.admin_order_field = 'has_discrepancy'

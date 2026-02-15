"""
Admin configuration for the Compliance app.

Provides admin interfaces for managing consent protocols and patient consents.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ConsentProtocol, PatientConsent


@admin.register(ConsentProtocol)
class ConsentProtocolAdmin(admin.ModelAdmin):
    """Admin interface for ConsentProtocol model."""

    list_display = [
        'name',
        'version',
        'protocol_type',
        'effective_date',
        'expiration_date',
        'is_active',
        'irb_status',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'protocol_type',
        'requires_witness',
        'effective_date',
        'irb_approval_date',
    ]
    search_fields = [
        'name',
        'version',
        'description',
        'irb_number',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_expired',
        'is_irb_expired',
    ]
    ordering = ['-effective_date', 'name']
    date_hierarchy = 'effective_date'

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'version',
                'protocol_type',
                'description',
            )
        }),
        ('IRB Information', {
            'fields': (
                'irb_number',
                'irb_approval_date',
                'irb_expiration_date',
            )
        }),
        ('Dates and Status', {
            'fields': (
                'effective_date',
                'expiration_date',
                'is_active',
            )
        }),
        ('Requirements', {
            'fields': (
                'requires_witness',
                'requires_legal_representative',
                'minimum_age',
            )
        }),
        ('Document', {
            'fields': (
                'document',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def irb_status(self, obj):
        """Display IRB approval status with color coding."""
        if not obj.irb_number:
            return format_html('<span style="color: gray;">No IRB</span>')

        if obj.is_irb_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        elif obj.irb_expiration_date:
            days_until = (obj.irb_expiration_date - timezone.now().date()).days
            if days_until <= 30:
                return format_html(
                    '<span style="color: orange;">Expires in {} days</span>',
                    days_until
                )
        return format_html('<span style="color: green;">Active</span>')

    irb_status.short_description = 'IRB Status'

    def save_model(self, request, obj, form, change):
        """Set created_by on creation."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PatientConsent)
class PatientConsentAdmin(admin.ModelAdmin):
    """Admin interface for PatientConsent model."""

    list_display = [
        'patient',
        'protocol',
        'status_display',
        'consent_date',
        'consented_by',
        'is_active',
        'validity_status',
    ]
    list_filter = [
        'status',
        'is_active',
        'consent_method',
        'protocol__protocol_type',
        'consent_date',
    ]
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__OP_NO',
        'protocol__name',
        'witness_name',
        'representative_name',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'is_valid',
    ]
    ordering = ['-consent_date', '-created_at']
    date_hierarchy = 'consent_date'
    autocomplete_fields = ['patient', 'protocol']
    raw_id_fields = ['consented_by', 'withdrawn_by']

    fieldsets = (
        ('Patient and Protocol', {
            'fields': (
                'patient',
                'protocol',
            )
        }),
        ('Consent Information', {
            'fields': (
                'status',
                'consent_date',
                'consent_method',
                'consented_by',
            )
        }),
        ('Witness Information', {
            'fields': (
                'witness_name',
                'witness_signature_date',
            ),
            'classes': ('collapse',)
        }),
        ('Legal Representative', {
            'fields': (
                'representative_name',
                'representative_relationship',
            ),
            'classes': ('collapse',)
        }),
        ('Withdrawal Information', {
            'fields': (
                'withdrawal_date',
                'withdrawal_reason',
                'withdrawn_by',
            ),
            'classes': ('collapse',)
        }),
        ('Document and Notes', {
            'fields': (
                'signed_document',
                'notes',
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_withdrawn', 'mark_as_active']

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'PENDING': 'orange',
            'CONSENTED': 'green',
            'DECLINED': 'gray',
            'WITHDRAWN': 'red',
            'EXPIRED': 'darkred',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    def validity_status(self, obj):
        """Display validity status."""
        if obj.is_valid:
            return format_html('<span style="color: green;">Valid</span>')
        return format_html('<span style="color: red;">Invalid</span>')

    validity_status.short_description = 'Validity'

    def mark_as_withdrawn(self, request, queryset):
        """Bulk action to mark consents as withdrawn."""
        count = 0
        for consent in queryset.filter(status='CONSENTED'):
            consent.withdraw_consent(
                withdrawn_by=request.user,
                reason='Bulk withdrawal via admin'
            )
            count += 1
        self.message_user(
            request,
            f'{count} consent(s) marked as withdrawn.'
        )

    mark_as_withdrawn.short_description = 'Mark selected consents as withdrawn'

    def mark_as_active(self, request, queryset):
        """Bulk action to mark consents as active."""
        count = queryset.filter(status='CONSENTED').update(is_active=True)
        self.message_user(
            request,
            f'{count} consent(s) marked as active.'
        )

    mark_as_active.short_description = 'Mark selected consents as active'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'patient',
            'protocol',
            'consented_by',
            'withdrawn_by'
        )

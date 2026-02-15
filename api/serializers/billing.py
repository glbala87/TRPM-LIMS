"""
Serializers for billing app models.
"""
from rest_framework import serializers
from billing.models import (
    PriceList, ServicePrice, Client,
    Invoice, InvoiceItem, Payment, QuotationRequest
)


class PriceListSerializer(serializers.ModelSerializer):
    """Serializer for PriceList model."""

    class Meta:
        model = PriceList
        fields = [
            'id', 'code', 'name', 'description', 'currency',
            'effective_from', 'effective_to', 'is_default', 'is_active'
        ]


class ServicePriceSerializer(serializers.ModelSerializer):
    """Serializer for ServicePrice model."""
    price_list_name = serializers.CharField(source='price_list.name', read_only=True)

    class Meta:
        model = ServicePrice
        fields = [
            'id', 'price_list', 'price_list_name', 'test_panel', 'service_code', 'service_name',
            'description', 'unit_price', 'cost_price', 'min_quantity',
            'volume_discount_enabled', 'volume_discount_tiers', 'is_active'
        ]


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    client_type_display = serializers.CharField(source='get_client_type_display', read_only=True)
    payment_terms_display = serializers.CharField(source='get_payment_terms_display', read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'client_id', 'name', 'client_type', 'client_type_display',
            'contact_name', 'email', 'phone', 'address', 'city', 'country',
            'tax_id', 'price_list', 'payment_terms', 'payment_terms_display',
            'credit_limit', 'discount_percent', 'is_active', 'created_at', 'notes'
        ]
        read_only_fields = ['id', 'client_id', 'created_at']


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Client list views."""
    client_type_display = serializers.CharField(source='get_client_type_display', read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'client_id', 'name', 'client_type_display', 'email', 'is_active']


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model."""

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'service_price', 'molecular_sample',
            'description', 'quantity', 'unit_price', 'discount_percent', 'line_total'
        ]
        read_only_fields = ['id', 'line_total']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'invoice', 'amount', 'payment_method', 'payment_method_display',
            'payment_date', 'reference_number', 'notes', 'received_by', 'created_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name', 'price_list',
            'status', 'status_display',
            'invoice_date', 'due_date', 'sent_date',
            'subtotal', 'discount_amount', 'tax_rate', 'tax_amount',
            'total_amount', 'paid_amount', 'balance_due',
            'billing_address', 'notes', 'internal_notes',
            'items', 'payments', 'created_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'subtotal', 'tax_amount',
            'total_amount', 'paid_amount', 'balance_due', 'created_at'
        ]


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Invoice list views."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'status_display',
            'invoice_date', 'due_date', 'total_amount', 'balance_due'
        ]


class QuotationRequestSerializer(serializers.ModelSerializer):
    """Serializer for QuotationRequest model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = QuotationRequest
        fields = [
            'id', 'quote_number', 'client', 'client_name', 'status', 'status_display',
            'quote_date', 'valid_until',
            'subtotal', 'discount_amount', 'total_amount',
            'terms_and_conditions', 'notes',
            'converted_to_invoice', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'quote_number', 'created_at']

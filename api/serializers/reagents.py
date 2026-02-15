"""
Serializers for reagents app models.
"""
from rest_framework import serializers
from reagents.models import Reagent, ReagentCategory, ReagentUsage, MolecularReagent


class ReagentCategorySerializer(serializers.ModelSerializer):
    """Serializer for ReagentCategory model."""

    class Meta:
        model = ReagentCategory
        fields = ['id', 'name', 'description']


class ReagentSerializer(serializers.ModelSerializer):
    """Serializer for Reagent model."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Reagent
        fields = [
            'id', 'name', 'category', 'category_display', 'vendor', 'lot_number',
            'stock_quantity', 'unit', 'expiration_date', 'storage_location',
            'on_order', 'is_low_stock', 'is_expired', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_low_stock(self, obj):
        return obj.stock_quantity < 10

    def get_is_expired(self, obj):
        if obj.expiration_date:
            from django.utils import timezone
            return obj.expiration_date < timezone.now().date()
        return False


class ReagentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Reagent list views."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Reagent
        fields = ['id', 'name', 'category_display', 'lot_number', 'stock_quantity', 'expiration_date']


class ReagentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Reagent records."""

    class Meta:
        model = Reagent
        fields = [
            'name', 'category', 'vendor', 'lot_number', 'stock_quantity',
            'unit', 'expiration_date', 'storage_location', 'notes'
        ]


class ReagentUsageSerializer(serializers.ModelSerializer):
    """Serializer for ReagentUsage model."""
    reagent_name = serializers.CharField(source='reagent.name', read_only=True)

    class Meta:
        model = ReagentUsage
        fields = ['id', 'reagent', 'reagent_name', 'lab_order', 'quantity_used', 'usage_date']
        read_only_fields = ['id', 'usage_date']


class MolecularReagentSerializer(serializers.ModelSerializer):
    """Serializer for MolecularReagent model."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    storage_temperature_display = serializers.CharField(source='get_storage_temperature_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    effective_expiration = serializers.DateField(read_only=True)
    test_panels = serializers.StringRelatedField(many=True, read_only=True)
    gene_targets = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = MolecularReagent
        fields = [
            'id', 'name', 'category', 'category_display', 'catalog_number', 'lot_number',
            'vendor', 'sequence', 'tm', 'gc_content', 'modification_5_prime', 'modification_3_prime',
            'storage_temperature', 'storage_temperature_display', 'storage_location',
            'initial_volume_ul', 'current_volume_ul', 'reactions_remaining',
            'received_date', 'opened_date', 'expiration_date', 'stability_days_after_opening',
            'effective_expiration', 'is_validated', 'validation_date', 'validated_by',
            'is_expired', 'is_low_stock', 'test_panels', 'gene_targets',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MolecularReagentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MolecularReagent list views."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = MolecularReagent
        fields = [
            'id', 'name', 'category_display', 'catalog_number', 'lot_number',
            'current_volume_ul', 'expiration_date', 'is_expired', 'is_low_stock', 'is_validated'
        ]


class MolecularReagentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MolecularReagent records."""

    class Meta:
        model = MolecularReagent
        fields = [
            'name', 'category', 'catalog_number', 'lot_number', 'vendor',
            'sequence', 'tm', 'gc_content', 'modification_5_prime', 'modification_3_prime',
            'storage_temperature', 'storage_location', 'initial_volume_ul',
            'received_date', 'expiration_date', 'stability_days_after_opening',
            'notes'
        ]

    def create(self, validated_data):
        # Set current_volume_ul to initial_volume_ul on creation
        validated_data['current_volume_ul'] = validated_data.get('initial_volume_ul')
        return super().create(validated_data)


class ReagentInventorySerializer(serializers.Serializer):
    """Serializer for reagent inventory summary."""
    total_reagents = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    expiring_soon_count = serializers.IntegerField()
    on_order_count = serializers.IntegerField()

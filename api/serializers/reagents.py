"""
Serializers for reagents app models.
Field lists are aligned with the actual model definitions in reagents/models.py.
"""
from rest_framework import serializers
from reagents.models import Reagent, ReagentCategory, ReagentUsage, MolecularReagent


class ReagentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReagentCategory
        fields = ['id', 'name', 'description']


class ReagentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Reagent
        fields = [
            'id', 'name', 'category', 'category_name', 'vendor', 'lot_number',
            'received_qty', 'opening_quantity', 'quantity_in_stock',
            'item_received_date', 'expiration_date',
            'on_order', 'is_low_stock', 'is_expired',
        ]
        read_only_fields = ['id']

    def get_is_low_stock(self, obj):
        return (obj.quantity_in_stock or 0) < 10

    def get_is_expired(self, obj):
        if obj.expiration_date:
            from django.utils import timezone
            return obj.expiration_date < timezone.now().date()
        return False


class ReagentListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Reagent
        fields = ['id', 'name', 'category_name', 'lot_number', 'quantity_in_stock', 'expiration_date']


class ReagentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = [
            'name', 'category', 'vendor', 'lot_number',
            'received_qty', 'opening_quantity', 'quantity_in_stock',
            'item_received_date', 'expiration_date',
        ]


class ReagentUsageSerializer(serializers.ModelSerializer):
    reagent_name = serializers.CharField(source='reagent.name', read_only=True)

    class Meta:
        model = ReagentUsage
        fields = ['id', 'reagent', 'reagent_name', 'used_in_lab_order', 'quantity_used', 'usage_date']
        read_only_fields = ['id', 'usage_date']


class MolecularReagentSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    storage_temperature_display = serializers.CharField(source='get_storage_temperature_display', read_only=True)
    test_panels = serializers.StringRelatedField(many=True, read_only=True, source='linked_test_panels')
    gene_targets = serializers.StringRelatedField(many=True, read_only=True, source='linked_gene_targets')

    class Meta:
        model = MolecularReagent
        fields = [
            'id', 'name', 'category', 'category_display', 'catalog_number', 'lot_number',
            'manufacturer', 'supplier', 'sequence', 'tm_celsius', 'gc_content',
            'modification_5prime', 'modification_3prime',
            'concentration', 'concentration_unit',
            'storage_temperature', 'storage_temperature_display', 'storage_location',
            'initial_volume_ul', 'current_volume_ul',
            'reactions_per_kit', 'reactions_remaining',
            'received_date', 'opened_date', 'expiration_date',
            'stability_after_opening_days',
            'is_active', 'is_validated', 'validation_date', 'validation_notes',
            'test_panels', 'gene_targets',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MolecularReagentListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = MolecularReagent
        fields = [
            'id', 'name', 'category_display', 'catalog_number', 'lot_number',
            'current_volume_ul', 'expiration_date', 'is_validated',
        ]


class MolecularReagentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MolecularReagent
        fields = [
            'name', 'category', 'catalog_number', 'lot_number',
            'manufacturer', 'supplier', 'sequence', 'tm_celsius', 'gc_content',
            'modification_5prime', 'modification_3prime',
            'concentration', 'concentration_unit',
            'storage_temperature', 'storage_location', 'initial_volume_ul',
            'received_date', 'expiration_date', 'stability_after_opening_days',
            'notes',
        ]

    def create(self, validated_data):
        # Mirror initial volume to current volume on creation.
        validated_data.setdefault('current_volume_ul', validated_data.get('initial_volume_ul'))
        return super().create(validated_data)


class ReagentInventorySerializer(serializers.Serializer):
    total_reagents = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    expiring_soon_count = serializers.IntegerField()
    on_order_count = serializers.IntegerField()

"""
Serializers for storage app models.
Field lists are aligned with the actual model definitions in storage/models.py.
"""
from rest_framework import serializers
from storage.models import StorageUnit, StorageRack, StoragePosition, StorageLog


class StoragePositionSerializer(serializers.ModelSerializer):
    full_location = serializers.SerializerMethodField()

    class Meta:
        model = StoragePosition
        fields = [
            'id', 'rack', 'position', 'row', 'column',
            'is_occupied', 'is_reserved',
            'stored_at', 'stored_by', 'notes', 'full_location',
        ]
        read_only_fields = ['id', 'stored_at']

    def get_full_location(self, obj):
        return str(obj)


class StoragePositionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoragePosition
        fields = ['id', 'position', 'is_occupied', 'is_reserved']


class StorageRackSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    positions = StoragePositionListSerializer(many=True, read_only=True)

    class Meta:
        model = StorageRack
        fields = [
            'id', 'unit', 'unit_name', 'rack_id', 'name', 'shelf_number',
            'rows', 'columns', 'rack_type', 'notes', 'is_active', 'positions',
        ]


class StorageRackListSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = StorageRack
        fields = ['id', 'name', 'rack_id', 'unit_name', 'rows', 'columns', 'is_active']


class StorageRackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageRack
        fields = ['unit', 'rack_id', 'name', 'shelf_number', 'rack_type', 'rows', 'columns', 'notes']

    def create(self, validated_data):
        rack = super().create(validated_data)
        # Auto-create empty positions for the rack grid.
        for row in range(rack.rows or 0):
            for col in range(rack.columns or 0):
                position_label = (
                    rack.get_position_label(row, col)
                    if hasattr(rack, 'get_position_label')
                    else f"R{row + 1}C{col + 1}"
                )
                StoragePosition.objects.create(
                    rack=rack,
                    position=position_label,
                    row=row,
                    column=col,
                )
        return rack


class StorageUnitSerializer(serializers.ModelSerializer):
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    racks = StorageRackListSerializer(many=True, read_only=True)

    class Meta:
        model = StorageUnit
        fields = [
            'id', 'name', 'code', 'unit_type', 'unit_type_display',
            'status', 'status_display', 'location',
            'temperature_min', 'temperature_max', 'temperature_target',
            'manufacturer', 'model', 'serial_number',
            'capacity_description', 'has_temperature_monitoring', 'has_alarm',
            'notes', 'is_active', 'racks', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StorageUnitListSerializer(serializers.ModelSerializer):
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StorageUnit
        fields = [
            'id', 'name', 'code', 'unit_type_display', 'status_display',
            'location', 'temperature_target',
        ]


class StorageUnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageUnit
        fields = [
            'name', 'code', 'unit_type', 'location',
            'temperature_min', 'temperature_max', 'temperature_target',
            'manufacturer', 'model', 'serial_number',
            'capacity_description', 'has_temperature_monitoring', 'has_alarm', 'notes',
        ]


class StorageLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    from_location = serializers.CharField(source='from_position.__str__', read_only=True)
    to_location = serializers.CharField(source='to_position.__str__', read_only=True)

    class Meta:
        model = StorageLog
        fields = [
            'id', 'position', 'sample_id', 'action', 'action_display',
            'from_position', 'from_location', 'to_position', 'to_location',
            'performed_by', 'performed_by_name', 'reason', 'notes', 'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class StorageLogListSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = StorageLog
        fields = ['id', 'sample_id', 'action_display', 'timestamp']


# Action serializers — these stay generic since they aren't backed by models.
class StoreSampleSerializer(serializers.Serializer):
    sample_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class MoveSampleSerializer(serializers.Serializer):
    to_position_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class RetrieveSampleSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)

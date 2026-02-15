"""
Serializers for storage app models.
"""
from rest_framework import serializers
from storage.models import StorageUnit, StorageRack, StoragePosition, StorageLog


class StoragePositionSerializer(serializers.ModelSerializer):
    """Serializer for StoragePosition model."""
    full_location = serializers.CharField(read_only=True)
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True, allow_null=True)

    class Meta:
        model = StoragePosition
        fields = [
            'id', 'rack', 'position_label', 'row', 'column',
            'is_occupied', 'is_reserved', 'sample', 'sample_id',
            'stored_at', 'stored_by', 'full_location'
        ]
        read_only_fields = ['id', 'is_occupied', 'stored_at', 'full_location']


class StoragePositionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for StoragePosition list views."""
    full_location = serializers.CharField(read_only=True)

    class Meta:
        model = StoragePosition
        fields = ['id', 'position_label', 'is_occupied', 'is_reserved', 'full_location']


class StorageRackSerializer(serializers.ModelSerializer):
    """Serializer for StorageRack model."""
    unit_name = serializers.CharField(source='storage_unit.name', read_only=True)
    total_positions = serializers.IntegerField(read_only=True)
    occupied_positions = serializers.IntegerField(read_only=True)
    available_positions = serializers.IntegerField(read_only=True)
    positions = StoragePositionListSerializer(many=True, read_only=True)

    class Meta:
        model = StorageRack
        fields = [
            'id', 'storage_unit', 'unit_name', 'name', 'rack_type',
            'rows', 'columns', 'total_positions', 'occupied_positions',
            'available_positions', 'description', 'positions'
        ]


class StorageRackListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for StorageRack list views."""
    unit_name = serializers.CharField(source='storage_unit.name', read_only=True)
    available_positions = serializers.IntegerField(read_only=True)

    class Meta:
        model = StorageRack
        fields = ['id', 'name', 'unit_name', 'rows', 'columns', 'available_positions']


class StorageRackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StorageRack records."""

    class Meta:
        model = StorageRack
        fields = ['storage_unit', 'name', 'rack_type', 'rows', 'columns', 'description']

    def create(self, validated_data):
        rack = super().create(validated_data)
        # Auto-create positions for the rack
        for row in range(rack.rows):
            for col in range(rack.columns):
                position_label = rack.get_position_label(row, col)
                StoragePosition.objects.create(
                    rack=rack,
                    position_label=position_label,
                    row=row,
                    column=col
                )
        return rack


class StorageUnitSerializer(serializers.ModelSerializer):
    """Serializer for StorageUnit model."""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    temperature_range = serializers.CharField(read_only=True)
    total_positions = serializers.IntegerField(read_only=True)
    occupied_positions = serializers.IntegerField(read_only=True)
    available_positions = serializers.IntegerField(read_only=True)
    racks = StorageRackListSerializer(many=True, read_only=True)

    class Meta:
        model = StorageUnit
        fields = [
            'id', 'name', 'unit_type', 'unit_type_display', 'status', 'status_display',
            'location', 'current_temperature', 'temperature_range',
            'min_temperature', 'max_temperature', 'temperature_alarm_enabled',
            'capacity_description', 'total_positions', 'occupied_positions',
            'available_positions', 'description', 'racks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StorageUnitListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for StorageUnit list views."""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    available_positions = serializers.IntegerField(read_only=True)

    class Meta:
        model = StorageUnit
        fields = [
            'id', 'name', 'unit_type_display', 'status_display',
            'location', 'current_temperature', 'available_positions'
        ]


class StorageUnitCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StorageUnit records."""

    class Meta:
        model = StorageUnit
        fields = [
            'name', 'unit_type', 'location', 'min_temperature', 'max_temperature',
            'temperature_alarm_enabled', 'capacity_description', 'description'
        ]


class StorageLogSerializer(serializers.ModelSerializer):
    """Serializer for StorageLog model."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True, allow_null=True)
    from_location = serializers.CharField(source='from_position.full_location', read_only=True, allow_null=True)
    to_location = serializers.CharField(source='to_position.full_location', read_only=True, allow_null=True)

    class Meta:
        model = StorageLog
        fields = [
            'id', 'sample', 'sample_id', 'action', 'action_display',
            'from_position', 'from_location', 'to_position', 'to_location',
            'user', 'user_name', 'reason', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class StorageLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for StorageLog list views."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    sample_id = serializers.CharField(source='sample.sample_id', read_only=True, allow_null=True)

    class Meta:
        model = StorageLog
        fields = ['id', 'sample_id', 'action_display', 'timestamp']


class StoreSampleSerializer(serializers.Serializer):
    """Serializer for storing a sample in a position."""
    sample_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class MoveSampleSerializer(serializers.Serializer):
    """Serializer for moving a sample to a new position."""
    to_position_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class RetrieveSampleSerializer(serializers.Serializer):
    """Serializer for retrieving a sample from storage."""
    reason = serializers.CharField(required=False, allow_blank=True)

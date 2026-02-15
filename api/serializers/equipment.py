"""
Serializers for equipment app models.
"""
from rest_framework import serializers
from equipment.models import Instrument, InstrumentType, MaintenanceRecord


class InstrumentTypeSerializer(serializers.ModelSerializer):
    """Serializer for InstrumentType model."""

    class Meta:
        model = InstrumentType
        fields = [
            'id', 'name', 'manufacturer', 'model_number', 'description',
            'maintenance_interval_days', 'calibration_interval_days', 'is_active'
        ]


class InstrumentSerializer(serializers.ModelSerializer):
    """Serializer for Instrument model."""
    instrument_type_name = serializers.CharField(source='instrument_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_maintenance_due = serializers.BooleanField(read_only=True)
    is_calibration_due = serializers.BooleanField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    warranty_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'instrument_type', 'instrument_type_name',
            'serial_number', 'asset_number', 'status', 'status_display',
            'location', 'firmware_version', 'software_version',
            'installation_date', 'warranty_expiration_date', 'warranty_valid',
            'last_maintenance_date', 'next_maintenance_date', 'is_maintenance_due',
            'last_calibration_date', 'next_calibration_date', 'is_calibration_due',
            'service_contact', 'specifications', 'notes', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstrumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Instrument list views."""
    instrument_type_name = serializers.CharField(source='instrument_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_maintenance_due = serializers.BooleanField(read_only=True)

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'instrument_type_name', 'serial_number',
            'status', 'status_display', 'location', 'is_maintenance_due'
        ]


class InstrumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Instrument records."""

    class Meta:
        model = Instrument
        fields = [
            'name', 'instrument_type', 'serial_number', 'asset_number',
            'location', 'firmware_version', 'software_version',
            'installation_date', 'warranty_expiration_date',
            'service_contact', 'specifications', 'notes'
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceRecord model."""
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'instrument', 'instrument_name', 'maintenance_type', 'maintenance_type_display',
            'status', 'status_display', 'description', 'scheduled_date', 'completed_date',
            'performed_by', 'service_provider', 'parts_replaced', 'certificate_file',
            'cost', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaintenanceRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MaintenanceRecord list views."""
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'instrument_name', 'maintenance_type_display',
            'status_display', 'scheduled_date', 'completed_date'
        ]


class MaintenanceRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MaintenanceRecord records."""

    class Meta:
        model = MaintenanceRecord
        fields = [
            'instrument', 'maintenance_type', 'description', 'scheduled_date',
            'service_provider', 'cost', 'notes'
        ]


class InstrumentMaintenanceHistorySerializer(serializers.ModelSerializer):
    """Serializer for viewing an instrument's maintenance history."""
    maintenance_records = MaintenanceRecordListSerializer(many=True, read_only=True, source='maintenancerecord_set')

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'serial_number', 'last_maintenance_date',
            'next_maintenance_date', 'last_calibration_date', 'next_calibration_date',
            'maintenance_records'
        ]

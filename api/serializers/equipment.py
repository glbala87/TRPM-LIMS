"""
Serializers for equipment app models.
Field lists are aligned with the actual model definitions in equipment/models.py.
"""
from rest_framework import serializers
from equipment.models import Instrument, InstrumentType, MaintenanceRecord


class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = [
            'id', 'name', 'code', 'manufacturer', 'description',
            'maintenance_interval_days', 'calibration_interval_days', 'is_active',
        ]


class InstrumentSerializer(serializers.ModelSerializer):
    instrument_type_name = serializers.CharField(source='instrument_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'instrument_type', 'instrument_type_name',
            'serial_number', 'asset_number', 'manufacturer', 'model',
            'status', 'status_display', 'location',
            'firmware_version', 'software_version',
            'purchase_date', 'installation_date', 'warranty_expiration',
            'last_maintenance', 'next_maintenance',
            'last_calibration', 'next_calibration',
            'contact_person', 'contact_phone', 'contact_email',
            'specifications', 'notes', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstrumentListSerializer(serializers.ModelSerializer):
    instrument_type_name = serializers.CharField(source='instrument_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'instrument_type_name', 'serial_number',
            'status', 'status_display', 'location', 'next_maintenance',
        ]


class InstrumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = [
            'name', 'instrument_type', 'serial_number', 'asset_number',
            'manufacturer', 'model', 'location',
            'firmware_version', 'software_version',
            'purchase_date', 'installation_date', 'warranty_expiration',
            'contact_person', 'contact_phone', 'contact_email',
            'specifications', 'notes',
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'instrument', 'instrument_name', 'maintenance_type', 'maintenance_type_display',
            'status', 'status_display', 'description',
            'scheduled_date', 'performed_at', 'completed_at',
            'performed_by', 'performed_by_user', 'service_provider',
            'findings', 'actions_taken', 'parts_replaced',
            'certificate', 'certificate_number', 'passed',
            'cost', 'next_due', 'notes', 'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at']


class MaintenanceRecordListSerializer(serializers.ModelSerializer):
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'instrument_name', 'maintenance_type_display',
            'status_display', 'scheduled_date', 'completed_at',
        ]


class MaintenanceRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'instrument', 'maintenance_type', 'description', 'scheduled_date',
            'service_provider', 'cost', 'notes',
        ]


class InstrumentMaintenanceHistorySerializer(serializers.ModelSerializer):
    maintenance_records = MaintenanceRecordListSerializer(many=True, read_only=True)

    class Meta:
        model = Instrument
        fields = [
            'id', 'name', 'serial_number',
            'last_maintenance', 'next_maintenance',
            'last_calibration', 'next_calibration',
            'maintenance_records',
        ]

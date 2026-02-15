"""
Serializers for sensors app models.
"""
from rest_framework import serializers
from sensors.models import (
    SensorType, MonitoringDevice, SensorReading,
    SensorAlert, AlertNotificationRule
)


class SensorTypeSerializer(serializers.ModelSerializer):
    """Serializer for SensorType model."""
    measurement_type_display = serializers.CharField(source='get_measurement_type_display', read_only=True)

    class Meta:
        model = SensorType
        fields = [
            'id', 'name', 'measurement_type', 'measurement_type_display',
            'unit', 'min_value', 'max_value', 'description', 'is_active'
        ]


class SensorReadingSerializer(serializers.ModelSerializer):
    """Serializer for SensorReading model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            'id', 'device', 'device_name', 'timestamp', 'value',
            'status', 'status_display', 'raw_data'
        ]
        read_only_fields = ['id', 'status']


class MonitoringDeviceSerializer(serializers.ModelSerializer):
    """Serializer for MonitoringDevice model."""
    sensor_type_name = serializers.CharField(source='sensor_type.name', read_only=True)
    sensor_unit = serializers.CharField(source='sensor_type.unit', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_in_alarm = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringDevice
        fields = [
            'id', 'device_id', 'name', 'sensor_type', 'sensor_type_name', 'sensor_unit',
            'mac_address', 'ip_address', 'storage_unit', 'location_description',
            'reading_interval_minutes', 'alert_enabled',
            'warning_min', 'warning_max', 'critical_min', 'critical_max',
            'status', 'status_display', 'is_in_alarm',
            'last_reading', 'last_reading_value',
            'installed_date', 'calibration_date', 'next_calibration_date',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'last_reading', 'last_reading_value', 'created_at']

    def get_is_in_alarm(self, obj):
        return obj.is_in_alarm()


class MonitoringDeviceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MonitoringDevice list views."""
    sensor_type_name = serializers.CharField(source='sensor_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MonitoringDevice
        fields = [
            'id', 'device_id', 'name', 'sensor_type_name', 'status_display',
            'last_reading_value', 'last_reading', 'alert_enabled'
        ]


class SensorAlertSerializer(serializers.ModelSerializer):
    """Serializer for SensorAlert model."""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = SensorAlert
        fields = [
            'id', 'device', 'device_name', 'reading', 'severity', 'severity_display',
            'status', 'status_display', 'message',
            'triggered_at', 'acknowledged_at', 'acknowledged_by',
            'resolved_at', 'resolved_by', 'resolution_notes',
            'notification_sent', 'notification_sent_at'
        ]
        read_only_fields = ['id', 'triggered_at']


class SensorAlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SensorAlert list views."""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = SensorAlert
        fields = [
            'id', 'device_name', 'severity_display', 'status_display', 'triggered_at'
        ]


class AlertNotificationRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertNotificationRule model."""

    class Meta:
        model = AlertNotificationRule
        fields = [
            'id', 'name', 'sensor_types', 'devices', 'severity_levels',
            'notify_users', 'notify_emails', 'notify_sms', 'is_active', 'created_at'
        ]

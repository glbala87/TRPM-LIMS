"""Smoke tests for sensors app."""
import decimal
import pytest
from sensors.models import SensorType, MonitoringDevice, SensorReading

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_sensor_type_create():
    s = SensorType.objects.create(name='Freezer temp', measurement_type='TEMPERATURE', unit='C')
    assert s.pk is not None


def test_monitoring_device_and_reading():
    st = SensorType.objects.create(name='Freezer temp', measurement_type='TEMPERATURE', unit='C')
    dev = MonitoringDevice.objects.create(device_id='DEV-001', name='Freezer A', sensor_type=st)
    r = SensorReading.objects.create(device=dev, value=decimal.Decimal('-80.0'))
    assert dev.pk is not None
    assert r.pk is not None
    assert r.device == dev

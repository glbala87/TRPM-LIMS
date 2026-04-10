"""Smoke tests for equipment app."""
import datetime as dt
import pytest
from equipment.models import InstrumentType, Instrument, MaintenanceRecord

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_instrument_type_create():
    t = InstrumentType.objects.create(name='qPCR', code='QPCR')
    assert t.pk is not None


def test_instrument_and_maintenance_record():
    t = InstrumentType.objects.create(name='qPCR', code='QPCR')
    inst = Instrument.objects.create(
        name='QuantStudio 3', instrument_type=t, serial_number='SN123',
    )
    rec = MaintenanceRecord.objects.create(
        instrument=inst,
        maintenance_type='PREVENTIVE',
        scheduled_date=dt.date.today(),
    )
    assert inst.pk is not None
    assert rec.pk is not None
    assert rec.instrument == inst

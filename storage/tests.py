"""Smoke tests for storage app."""
import pytest
from storage.models import StorageUnit, StorageRack, StoragePosition

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_storage_unit_create():
    u = StorageUnit.objects.create(name='Freezer A', code='FRZ-A', unit_type='FREEZER_MINUS80')
    assert u.pk is not None


def test_rack_and_position():
    u = StorageUnit.objects.create(name='Freezer A', code='FRZ-A', unit_type='FREEZER_MINUS80')
    rack = StorageRack.objects.create(unit=u, rack_id='R1', name='Rack 1', rows=4, columns=4)
    pos = StoragePosition.objects.create(rack=rack, position='R1-A1', row=0, column=0)
    assert rack.pk is not None
    assert pos.pk is not None
    assert pos.rack == rack

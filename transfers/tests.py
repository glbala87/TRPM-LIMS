"""Smoke tests for transfers app."""
import pytest
from transfers.models import Transfer, TransferItem

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_transfer_and_item():
    t = Transfer.objects.create(
        transfer_number='TRF-001',
        source_location='Room 101',
        destination_location='Room 202',
    )
    item = TransferItem.objects.create(transfer=t, sample_id='S-0001')
    assert t.pk is not None
    assert item.pk is not None
    assert item.transfer == t

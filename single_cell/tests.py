"""Smoke tests for single_cell app."""
import pytest
from single_cell.models import SingleCellSampleType, FeatureBarcode

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_sample_type_create():
    t = SingleCellSampleType.objects.create(name='PBMC', code='PBMC')
    assert t.pk is not None


def test_feature_barcode_create():
    fb = FeatureBarcode.objects.create(name='TotalSeq A0001', barcode_sequence='AAACCCGGG')
    assert fb.pk is not None

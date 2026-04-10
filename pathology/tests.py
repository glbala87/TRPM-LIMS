"""Smoke tests for pathology app."""
import pytest
from pathology.models import PathologyType, TumorSite

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_pathology_type_create():
    t = PathologyType.objects.create(code='HISTO', name='Histology')
    assert t.pk is not None


def test_tumor_site_create():
    s = TumorSite.objects.create(code='BREAST', name='Breast')
    assert s.pk is not None

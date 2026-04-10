"""Smoke tests for data_exchange app."""
import pytest
from data_exchange.models import ExportTemplate

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_export_template_create():
    t = ExportTemplate.objects.create(name='Patient CSV', data_type='PATIENT')
    assert t.pk is not None

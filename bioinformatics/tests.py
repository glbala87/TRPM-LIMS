"""Smoke tests for bioinformatics app."""
import pytest
from bioinformatics.models import Pipeline

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_pipeline_create():
    p = Pipeline.objects.create(name='WGS GATK', code='WGS-GATK', version='1.0')
    assert p.pk is not None
    assert p.code == 'WGS-GATK'

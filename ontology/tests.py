"""Smoke tests for ontology app."""
import pytest
from ontology.models import OntologySource, DiseaseOntology, AnatomicalSite

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_ontology_source_and_disease():
    src = OntologySource.objects.create(name='DOID', code='DOID')
    d = DiseaseOntology.objects.create(source=src, code='DOID:1612', name='Breast cancer')
    assert d.pk is not None
    assert d.source == src


def test_anatomical_site_create():
    s = AnatomicalSite.objects.create(code='BREAST', name='Breast')
    assert s.pk is not None

"""Smoke tests for tenants app."""
import pytest
from tenants.models import Organization, Laboratory

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_organization_create():
    o = Organization.objects.create(name='Acme Health', code='ACME')
    assert o.pk is not None


def test_laboratory_create():
    o = Organization.objects.create(name='Acme Health', code='ACME')
    lab = Laboratory.objects.create(organization=o, name='Main Lab', code='MAIN')
    assert lab.pk is not None
    assert lab.organization == o

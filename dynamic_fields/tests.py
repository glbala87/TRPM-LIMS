"""Smoke tests for dynamic_fields app."""
import pytest
from dynamic_fields.models import FieldCategory

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_field_category_create():
    c = FieldCategory.objects.create(name='Clinical', code='CLIN')
    assert c.pk is not None
    assert c.code == 'CLIN'

"""Smoke tests for reagents app."""
import datetime as dt
import pytest
from reagents.models import ReagentCategory, Reagent

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_reagent_category_create():
    c = ReagentCategory.objects.create(name='Buffers')
    assert c.pk is not None


def test_reagent_create():
    r = Reagent.objects.create(
        name='Tris buffer',
        category='Buffers',
        quantity_in_stock=100,
        expiration_date=dt.date(2027, 1, 1),
    )
    assert r.pk is not None
    assert r.quantity_in_stock == 100

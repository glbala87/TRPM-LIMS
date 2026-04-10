"""Smoke tests for billing app."""
import datetime as dt
import pytest
from billing.models import PriceList, ServicePrice, Client

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_price_list_and_service_price():
    pl = PriceList.objects.create(
        name='Standard 2026', code='STD-2026', effective_from=dt.date(2026, 1, 1),
    )
    sp = ServicePrice.objects.create(
        price_list=pl,
        service_code='CBC',
        service_name='Complete Blood Count',
        unit_price='10.00',
    )
    assert sp.pk is not None
    assert sp.price_list == pl


def test_client_create():
    c = Client.objects.create(client_id='CL-001', name='Acme Health')
    assert c.pk is not None

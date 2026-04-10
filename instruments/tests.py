"""Smoke tests for instruments app."""
import pytest
from django.apps import apps

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_app_registers():
    assert apps.get_app_config('instruments') is not None


def test_instrument_connection_imports():
    from instruments.models import InstrumentConnection  # noqa: F401

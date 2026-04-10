"""Smoke tests for messaging app."""
import pytest
from django.apps import apps

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_app_registers():
    assert apps.get_app_config('messaging') is not None


def test_models_importable():
    from messaging.models import MessageThread, Message  # noqa: F401

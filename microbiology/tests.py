"""Smoke tests for microbiology app."""
import pytest
from microbiology.models import TestMethod, Host, BreakpointType

# Tell pytest not to collect the TestMethod Django model as a test class
# (its name starts with `Test`).
TestMethod.__test__ = False

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_test_method_create():
    m = TestMethod.objects.create(code='DISC', name='Disc diffusion')
    assert m.pk is not None


def test_host_create():
    h = Host.objects.create(code='HUM', name='Human')
    assert h.pk is not None


def test_breakpoint_type_create():
    b = BreakpointType.objects.create(code='CLSI', name='CLSI standard')
    assert b.pk is not None

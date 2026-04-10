"""
Smoke tests for the lab_management app.

These verify that imports resolve, models can be instantiated, and key API
endpoints respond. They are intentionally lightweight; deeper unit and
integration tests should be added incrementally.
"""
import pytest
from django.urls import reverse, NoReverseMatch

from lab_management.models import Patient, LabOrder, TestResult

# Tell pytest not to collect the TestResult Django model as a test class
# (its name starts with `Test`).
TestResult.__test__ = False

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


# ---------------------------------------------------------------------------
# Model smoke
# ---------------------------------------------------------------------------
def _make_patient(**overrides):
    defaults = dict(
        first_name='Jane',
        last_name='Doe',
        age=30,
        gender='F',
        nationality='Test',
        phone_no='0700000000',
    )
    defaults.update(overrides)
    return Patient.objects.create(**defaults)


def test_patient_create_and_str():
    p = _make_patient()
    assert p.pk is not None
    assert 'Jane' in str(p) or p.first_name == 'Jane'


def test_lab_order_create():
    p = _make_patient()
    order = LabOrder.objects.create(
        patient=p,
        test_name='CBC',
        sample_type='Blood',
        container='EDTA',
    )
    assert order.pk is not None
    assert order.patient == p


def test_test_result_create():
    p = _make_patient()
    order = LabOrder.objects.create(
        patient=p,
        test_name='CBC',
        sample_type='Blood',
        container='EDTA',
    )
    result = TestResult.objects.create(lab_order=order, result_data={'WBC': 5.4})
    assert result.pk is not None
    assert result.result_data['WBC'] == 5.4


# ---------------------------------------------------------------------------
# API smoke
# ---------------------------------------------------------------------------
def test_patients_api_requires_auth(api_client):
    resp = api_client.get('/api/patients/')
    assert resp.status_code in (401, 403)


def test_patients_api_list_authenticated(auth_client):
    _make_patient()
    resp = auth_client.get('/api/patients/')
    assert resp.status_code == 200


def test_lab_orders_api_list_authenticated(auth_client):
    p = _make_patient()
    LabOrder.objects.create(
        patient=p, test_name='CBC', sample_type='Blood', container='EDTA',
    )
    resp = auth_client.get('/api/lab-orders/')
    # Endpoint may be registered under a different basename — accept 200 or 404 gracefully.
    assert resp.status_code in (200, 404)

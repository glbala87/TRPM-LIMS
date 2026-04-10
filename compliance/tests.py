"""
Smoke tests for the compliance app.

Verifies consent protocol and patient consent models work end-to-end.
"""
import datetime as dt

import pytest

from compliance.models import ConsentProtocol, PatientConsent
from lab_management.models import Patient


pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def _make_patient():
    return Patient.objects.create(
        first_name='Con',
        last_name='Sent',
        age=25,
        gender='F',
        nationality='Test',
        phone_no='0700000002',
    )


def test_consent_protocol_create():
    proto = ConsentProtocol.objects.create(
        name='Research IC v1',
        version='1.0',
        description='Smoke-test protocol',
        irb_number='IRB-TEST-001',
        effective_date=dt.date.today(),
    )
    assert proto.pk is not None
    assert proto.is_active is True  # default


def test_patient_consent_create_and_link():
    proto = ConsentProtocol.objects.create(
        name='Research IC v1',
        version='1.0',
        description='Smoke-test protocol',
        irb_number='IRB-TEST-001',
        effective_date=dt.date.today(),
    )
    patient = _make_patient()
    consent = PatientConsent.objects.create(patient=patient, protocol=proto)
    assert consent.pk is not None
    assert consent.patient == patient
    assert consent.protocol == proto
    assert consent.is_active is True  # default


# ---------------------------------------------------------------------------
# 21 CFR Part 11 electronic signature scaffolding
# ---------------------------------------------------------------------------
def test_electronic_signature_sign_and_verify(user):
    from compliance.models import ElectronicSignature
    from django.core.exceptions import ValidationError

    patient = _make_patient()
    sig = ElectronicSignature.sign(
        record=patient,
        signer=user,
        reason='APPROVAL',
        meaning='I approve this record for release.',
    )
    assert sig.pk is not None
    assert sig.signer_username == user.username
    assert sig.reason == 'APPROVAL'
    assert sig.integrity_hash, 'Integrity hash must be computed on save'
    assert sig.verify_integrity() is True
    # Snapshot captured the record state.
    assert sig.record_snapshot['first_name'] == 'Con'


class _FakeRequest:
    """Minimal stand-in for a DRF Request in unit tests of enforce_esignature."""
    def __init__(self, user, data=None):
        self.user = user
        self.data = data or {}
        self.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'pytest'}


def test_enforcement_off_allows_unsigned(user):
    """When ENABLE_PART11 is off, enforce_esignature accepts no-payload calls."""
    from compliance.enforcement import enforce_esignature
    from django.test import override_settings

    patient = _make_patient()
    req = _FakeRequest(user=user)
    with override_settings(ENABLE_PART11=False):
        result = enforce_esignature(request=req, record=patient)
    assert result is None


def test_enforcement_on_requires_password(user):
    """When ENABLE_PART11 is on, the signature payload is required."""
    from compliance.enforcement import enforce_esignature
    from django.test import override_settings
    from rest_framework.exceptions import ValidationError

    patient = _make_patient()
    req = _FakeRequest(user=user)
    with override_settings(ENABLE_PART11=True):
        with pytest.raises(ValidationError):
            enforce_esignature(request=req, record=patient)


def test_electronic_signature_is_immutable(user):
    from compliance.models import ElectronicSignature
    from django.core.exceptions import ValidationError

    patient = _make_patient()
    sig = ElectronicSignature.sign(
        record=patient, signer=user,
        reason='REVIEW', meaning='Reviewed for accuracy.',
    )
    sig.notes = 'tampered'
    with pytest.raises(ValidationError):
        sig.save()
    with pytest.raises(ValidationError):
        sig.delete()

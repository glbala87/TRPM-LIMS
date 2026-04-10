"""
Smoke tests for the audit app.

Verifies the AuditLog and AuditTrail models work and that the audit middleware
is wired in. Deeper assertions about which actions create which entries should
be added incrementally.
"""
import pytest
from django.contrib.contenttypes.models import ContentType

from audit.models import AuditLog, AuditTrail
from lab_management.models import Patient


pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_audit_log_create():
    log = AuditLog.objects.create(
        username='tester',
        action='CREATE',
        object_repr='Patient #1',
        request_path='/patients/',
        request_method='POST',
    )
    assert log.pk is not None
    assert log.action == 'CREATE'


def test_audit_log_links_to_user(user):
    log = AuditLog.objects.create(
        user=user,
        username=user.username,
        action='UPDATE',
        object_repr='Test',
        request_path='/',
        request_method='GET',
    )
    assert log.user == user


def test_audit_trail_auto_snapshot_on_auditable_model():
    """Creating a Patient (an auditable model) should auto-create an AuditTrail snapshot."""
    p = Patient.objects.create(
        first_name='Audit', last_name='Trail', age=40, gender='M',
        nationality='Test', phone_no='0700000001',
    )
    ct = ContentType.objects.get_for_model(Patient)
    trails = AuditTrail.objects.filter(content_type=ct, object_id=p.pk)
    assert trails.exists(), "Expected the audit signal to create a snapshot for Patient"
    latest = trails.order_by('-version').first()
    assert latest.snapshot['first_name'] == 'Audit'


def test_middleware_does_not_break_authenticated_request(auth_client):
    """The audit middleware should not crash on a normal authenticated request."""
    resp = auth_client.get('/api/patients/')
    assert resp.status_code in (200, 401, 403, 404)

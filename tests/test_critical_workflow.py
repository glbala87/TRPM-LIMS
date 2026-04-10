"""
End-to-end integration test for the most critical LIMS workflow:

  Patient registration → Lab order → Molecular sample → Result entry →
  Result review → Result approval (with e-signature) → Verify audit trail

This test exercises the happy path through the domain models (not via HTTP
for speed) and asserts that audit/compliance artefacts are created.
"""
import datetime as dt
import pytest

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from lab_management.models import Patient, LabOrder
from molecular_diagnostics.models import (
    GeneTarget, MolecularSampleType, MolecularTestPanel, MolecularSample,
    MolecularResult,
)
from audit.models import AuditLog, AuditTrail
from compliance.models import ElectronicSignature

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def director(db):
    return User.objects.create_user(
        username='director', email='dir@lab.org', password='Director-Pass-123!',
    )


@pytest.fixture
def tech(db):
    return User.objects.create_user(
        username='tech', email='tech@lab.org', password='Tech-Pass-123!',
    )


@pytest.fixture
def basic_setup(db):
    """Set up the reference data needed for a molecular workflow."""
    gene = GeneTarget.objects.create(
        symbol='BRCA1', name='Breast Cancer 1',
        chromosome='17', genomic_coordinates='chr17:43044295-43170245',
        transcript_id='NM_007294.4',
    )
    st = MolecularSampleType.objects.create(
        name='EDTA Blood', code='EDTA-BL', storage_temperature='4C',
    )
    panel = MolecularTestPanel.objects.create(
        name='BRCA Panel', code='BRCA-P', test_type='NGS',
        methodology='Targeted', sample_requirements='10 ng', tat_hours=72,
    )
    panel.gene_targets.add(gene)
    return {'gene': gene, 'sample_type': st, 'panel': panel}


def test_full_critical_workflow(tech, director, basic_setup):
    """
    Patient → Lab order → Molecular sample → Result → Review → Approve →
    E-signature → Audit trail asserted.
    """
    # 1. Patient registration
    patient = Patient.objects.create(
        first_name='Test', last_name='Patient', age=45, gender='F',
        nationality='Test', phone_no='0700000099',
    )
    assert patient.pk

    # 2. Lab order
    order = LabOrder.objects.create(
        patient=patient, test_name='BRCA Panel', sample_type='Blood', container='EDTA',
    )
    assert order.pk

    # 3. Molecular sample
    sample = MolecularSample.objects.create(
        sample_id='MOL-INT-001',
        lab_order=order,
        sample_type=basic_setup['sample_type'],
        test_panel=basic_setup['panel'],
    )
    assert sample.pk

    # 4. Result entry
    from django.utils import timezone
    result = MolecularResult.objects.create(
        sample=sample,
        test_panel=basic_setup['panel'],
        status='PENDING',
    )
    assert result.pk

    # 5. Review (without Part 11 enforcement)
    result.reviewed_by = tech
    result.reviewed_at = timezone.now()
    result.status = 'PRELIMINARY'
    result.save()
    assert result.status == 'PRELIMINARY'

    # 6. Approval WITH electronic signature (simulating Part 11)
    sig = ElectronicSignature.sign(
        record=result,
        signer=director,
        reason='APPROVAL',
        meaning='I approve this result for release to the patient/clinician.',
    )
    result.approved_by = director
    result.approved_at = timezone.now()
    result.status = 'FINAL'
    result.save()

    # 7. Assertions
    assert result.status == 'FINAL'
    assert sig.pk is not None
    assert sig.verify_integrity()
    assert sig.signer_username == 'director'
    assert sig.record_snapshot['status'] == 'PRELIMINARY'  # snapshot before the FINAL save

    # 8. Audit trail — check that AuditLog/AuditTrail captured events
    ct = ContentType.objects.get_for_model(Patient)
    patient_logs = AuditLog.objects.filter(content_type=ct, object_id=patient.pk)
    assert patient_logs.exists(), 'Patient CREATE should be logged'

    result_ct = ContentType.objects.get_for_model(MolecularResult)
    result_logs = AuditLog.objects.filter(content_type=result_ct, object_id=result.pk)
    assert result_logs.count() >= 2, 'Result should have CREATE + at least one UPDATE log'

    # 9. Signature is immutable
    from django.core.exceptions import ValidationError
    sig.notes = 'tampered'
    with pytest.raises(ValidationError):
        sig.save()

"""
Smoke tests for the molecular_diagnostics app.

NOTE: there is an existing models/tests.py file in this app that defines
production models (legacy filename); we put smoke tests here in test_smoke.py
to avoid colliding with that file.
"""
import pytest

from molecular_diagnostics.models import (
    GeneTarget,
    MolecularSampleType,
    MolecularTestPanel,
    ControlSample,
)


pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_gene_target_create():
    g = GeneTarget.objects.create(
        symbol='BRCA1',
        name='Breast Cancer 1',
        chromosome='17',
        genomic_coordinates='chr17:43044295-43170245',
        transcript_id='NM_007294.4',
    )
    assert g.pk is not None
    assert 'BRCA1' in str(g)


def test_molecular_sample_type_create():
    st = MolecularSampleType.objects.create(
        name='EDTA Blood',
        code='EDTA-BL',
        storage_temperature='4C',
        stability_hours=72,
    )
    assert st.pk is not None
    assert st.code == 'EDTA-BL'


def test_test_panel_create_and_link_genes():
    g = GeneTarget.objects.create(
        symbol='TP53',
        name='Tumor protein p53',
        chromosome='17',
        genomic_coordinates='chr17:7668421-7687550',
        transcript_id='NM_000546.6',
    )
    panel = MolecularTestPanel.objects.create(
        name='Hereditary Cancer Panel',
        code='HCP-1',
        test_type='NGS',
        methodology='Targeted sequencing',
        sample_requirements='10 ng DNA',
        tat_hours=72,
    )
    panel.gene_targets.add(g)
    assert panel.gene_targets.count() == 1
    assert panel.gene_targets.first() == g


def test_control_sample_create():
    g = GeneTarget.objects.create(
        symbol='KRAS',
        name='KRAS proto-oncogene',
        chromosome='12',
        genomic_coordinates='chr12:25205246-25250929',
        transcript_id='NM_004985.5',
    )
    control = ControlSample.objects.create(
        name='KRAS G12D positive control',
        control_type='POSITIVE',
        lot_number='LOT-001',
        expected_result='Detected',
        target_gene=g,
    )
    assert control.pk is not None
    assert control.target_gene == g


def test_molecular_api_requires_auth(api_client):
    resp = api_client.get('/api/gene-targets/')
    assert resp.status_code in (401, 403, 404)

"""Smoke tests for analytics app."""
import pytest
from analytics.models import DashboardWidget, Report

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_dashboard_widget_create():
    w = DashboardWidget.objects.create(
        name='Samples per day',
        widget_type='LINE_CHART',
        data_source='molecular_diagnostics.MolecularSample',
    )
    assert w.pk is not None


def test_report_create():
    r = Report.objects.create(name='Monthly summary', report_type='SAMPLE_SUMMARY')
    assert r.pk is not None

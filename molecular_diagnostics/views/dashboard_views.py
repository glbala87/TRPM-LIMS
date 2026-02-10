# molecular_diagnostics/views/dashboard_views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from ..models import MolecularSample, MolecularTestPanel
from ..services.tat_monitor import TATMonitor


@login_required
def dashboard(request):
    """Main molecular diagnostics dashboard"""
    today = timezone.now().date()

    # Sample counts by status
    status_counts = MolecularSample.objects.values('workflow_status').annotate(
        count=Count('id')
    )

    # Samples received today
    received_today = MolecularSample.objects.filter(
        received_datetime__date=today
    ).count()

    # Samples completed today
    completed_today = MolecularSample.objects.filter(
        workflow_status='REPORTED',
        updated_at__date=today
    ).count()

    # At-risk samples (approaching TAT SLA)
    tat_monitor = TATMonitor()
    at_risk_samples = tat_monitor.get_at_risk_samples()

    context = {
        'status_counts': {item['workflow_status']: item['count'] for item in status_counts},
        'received_today': received_today,
        'completed_today': completed_today,
        'at_risk_samples': at_risk_samples[:10],
        'at_risk_count': len(at_risk_samples),
    }

    return render(request, 'molecular_diagnostics/dashboard.html', context)


@login_required
def tat_dashboard(request):
    """Turnaround time monitoring dashboard"""
    tat_monitor = TATMonitor()

    # Get TAT statistics by test panel
    test_panels = MolecularTestPanel.objects.filter(is_active=True)
    panel_stats = []

    for panel in test_panels:
        stats = tat_monitor.get_panel_statistics(panel)
        panel_stats.append({
            'panel': panel,
            'stats': stats
        })

    # Get at-risk and overdue samples
    at_risk_samples = tat_monitor.get_at_risk_samples()
    overdue_samples = tat_monitor.get_overdue_samples()

    context = {
        'panel_stats': panel_stats,
        'at_risk_samples': at_risk_samples,
        'overdue_samples': overdue_samples,
    }

    return render(request, 'molecular_diagnostics/tat_dashboard.html', context)


@login_required
def at_risk_samples(request):
    """View for samples at risk of missing TAT SLA"""
    tat_monitor = TATMonitor()
    samples = tat_monitor.get_at_risk_samples()

    context = {
        'samples': samples,
    }

    return render(request, 'molecular_diagnostics/at_risk_samples.html', context)

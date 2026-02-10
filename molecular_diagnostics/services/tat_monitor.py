# molecular_diagnostics/services/tat_monitor.py

from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DurationField, Avg, Count, Q
from datetime import timedelta
from decimal import Decimal


class TATMonitor:
    """
    Turnaround Time (TAT) monitoring service.

    Tracks samples against their SLA targets and identifies at-risk samples.
    """

    # Warning threshold - percentage of TAT at which to flag as "at risk"
    WARNING_THRESHOLD = 0.75  # 75% of TAT
    CRITICAL_THRESHOLD = 0.90  # 90% of TAT

    def __init__(self):
        self.now = timezone.now()

    def get_sample_tat_status(self, sample):
        """
        Get TAT status for a single sample.

        Returns:
            dict with TAT information including:
            - elapsed_hours: Hours since sample received
            - target_hours: TAT target from test panel
            - remaining_hours: Hours remaining before SLA breach
            - percentage_used: Percentage of TAT consumed
            - status: 'ON_TRACK', 'WARNING', 'CRITICAL', 'OVERDUE', 'COMPLETED'
        """
        if sample.workflow_status == 'REPORTED':
            # Calculate actual TAT for completed samples
            elapsed = sample.get_turnaround_time()
            target = sample.test_panel.tat_hours if sample.test_panel else None

            return {
                'sample': sample,
                'elapsed_hours': elapsed,
                'target_hours': target,
                'remaining_hours': 0,
                'percentage_used': (elapsed / target * 100) if target else None,
                'status': 'COMPLETED',
                'met_sla': elapsed <= target if target else None,
            }

        if sample.workflow_status in ['CANCELLED', 'FAILED']:
            return {
                'sample': sample,
                'status': sample.workflow_status,
                'elapsed_hours': None,
                'target_hours': None,
                'remaining_hours': None,
                'percentage_used': None,
            }

        # Calculate for in-progress samples
        elapsed_hours = sample.get_turnaround_time()
        target_hours = sample.test_panel.tat_hours if sample.test_panel else None

        if target_hours is None:
            return {
                'sample': sample,
                'elapsed_hours': elapsed_hours,
                'target_hours': None,
                'remaining_hours': None,
                'percentage_used': None,
                'status': 'NO_SLA',
            }

        remaining_hours = target_hours - elapsed_hours
        percentage_used = (elapsed_hours / target_hours) * 100

        # Determine status
        if remaining_hours <= 0:
            status = 'OVERDUE'
        elif percentage_used >= self.CRITICAL_THRESHOLD * 100:
            status = 'CRITICAL'
        elif percentage_used >= self.WARNING_THRESHOLD * 100:
            status = 'WARNING'
        else:
            status = 'ON_TRACK'

        return {
            'sample': sample,
            'elapsed_hours': round(elapsed_hours, 1),
            'target_hours': target_hours,
            'remaining_hours': round(remaining_hours, 1),
            'percentage_used': round(percentage_used, 1),
            'status': status,
            'due_datetime': sample.received_datetime + timedelta(hours=target_hours),
        }

    def get_at_risk_samples(self):
        """
        Get all samples at risk of missing their TAT SLA.

        Returns samples in WARNING, CRITICAL, or OVERDUE status.
        """
        from ..models import MolecularSample

        # Get all in-progress samples with test panels
        samples = MolecularSample.objects.filter(
            is_active=True,
            test_panel__isnull=False
        ).exclude(
            workflow_status__in=['REPORTED', 'CANCELLED', 'FAILED']
        ).select_related(
            'lab_order__patient',
            'sample_type',
            'test_panel'
        )

        at_risk = []
        for sample in samples:
            tat_status = self.get_sample_tat_status(sample)
            if tat_status['status'] in ['WARNING', 'CRITICAL', 'OVERDUE']:
                at_risk.append(tat_status)

        # Sort by remaining time (most urgent first)
        at_risk.sort(key=lambda x: x.get('remaining_hours', float('inf')))

        return at_risk

    def get_overdue_samples(self):
        """Get all samples that have exceeded their TAT SLA."""
        at_risk = self.get_at_risk_samples()
        return [s for s in at_risk if s['status'] == 'OVERDUE']

    def get_panel_statistics(self, test_panel, days=30):
        """
        Get TAT statistics for a specific test panel.

        Args:
            test_panel: MolecularTestPanel instance
            days: Number of days to look back

        Returns:
            dict with statistics
        """
        from ..models import MolecularSample

        cutoff_date = self.now - timedelta(days=days)

        # Get completed samples for this panel in the time period
        samples = MolecularSample.objects.filter(
            test_panel=test_panel,
            workflow_status='REPORTED',
            updated_at__gte=cutoff_date
        )

        if not samples.exists():
            return {
                'panel': test_panel,
                'sample_count': 0,
                'avg_tat_hours': None,
                'min_tat_hours': None,
                'max_tat_hours': None,
                'sla_compliance_rate': None,
            }

        # Calculate TAT for each sample
        tat_values = []
        sla_met_count = 0

        for sample in samples:
            tat = sample.get_turnaround_time()
            tat_values.append(tat)
            if tat <= test_panel.tat_hours:
                sla_met_count += 1

        sample_count = len(tat_values)

        return {
            'panel': test_panel,
            'sample_count': sample_count,
            'avg_tat_hours': round(sum(tat_values) / sample_count, 1),
            'min_tat_hours': round(min(tat_values), 1),
            'max_tat_hours': round(max(tat_values), 1),
            'sla_compliance_rate': round((sla_met_count / sample_count) * 100, 1),
            'target_tat_hours': test_panel.tat_hours,
        }

    def get_daily_summary(self, date=None):
        """
        Get TAT summary for a specific date.

        Args:
            date: Date to summarize (defaults to today)

        Returns:
            dict with daily metrics
        """
        from ..models import MolecularSample

        if date is None:
            date = self.now.date()

        # Samples received on this date
        received = MolecularSample.objects.filter(
            received_datetime__date=date
        ).count()

        # Samples completed on this date
        completed = MolecularSample.objects.filter(
            workflow_status='REPORTED',
            updated_at__date=date
        )

        completed_count = completed.count()

        # Calculate SLA compliance for completed samples
        sla_met = 0
        for sample in completed.select_related('test_panel'):
            if sample.test_panel:
                tat = sample.get_turnaround_time()
                if tat <= sample.test_panel.tat_hours:
                    sla_met += 1

        return {
            'date': date,
            'samples_received': received,
            'samples_completed': completed_count,
            'sla_compliance_rate': round((sla_met / completed_count * 100), 1) if completed_count > 0 else None,
        }

    def get_workload_by_status(self):
        """Get current workload distribution by workflow status."""
        from ..models import MolecularSample

        return MolecularSample.objects.filter(
            is_active=True
        ).exclude(
            workflow_status__in=['REPORTED', 'CANCELLED', 'FAILED']
        ).values('workflow_status').annotate(
            count=Count('id')
        ).order_by('workflow_status')

    def get_priority_samples(self):
        """
        Get samples ordered by priority for processing.

        Prioritizes:
        1. STAT samples
        2. URGENT samples approaching TAT
        3. ROUTINE samples approaching TAT
        """
        from ..models import MolecularSample

        samples = MolecularSample.objects.filter(
            is_active=True,
            test_panel__isnull=False
        ).exclude(
            workflow_status__in=['REPORTED', 'CANCELLED', 'FAILED']
        ).select_related(
            'lab_order__patient',
            'sample_type',
            'test_panel'
        )

        # Calculate priority score for each sample
        prioritized = []
        for sample in samples:
            tat_status = self.get_sample_tat_status(sample)

            # Priority score: lower is higher priority
            base_score = {
                'STAT': 0,
                'URGENT': 1000,
                'ROUTINE': 2000,
            }.get(sample.priority, 2000)

            # Adjust by remaining time (0-100 range)
            remaining = tat_status.get('remaining_hours', 999)
            time_urgency = max(0, min(100, 100 - remaining))

            priority_score = base_score - time_urgency

            prioritized.append({
                'sample': sample,
                'priority_score': priority_score,
                'tat_status': tat_status,
            })

        # Sort by priority score
        prioritized.sort(key=lambda x: x['priority_score'])

        return prioritized

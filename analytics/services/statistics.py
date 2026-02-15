# analytics/services/statistics.py

from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional


class SampleStatisticsService:
    """
    Service for calculating sample statistics including counts by status,
    turnaround time (TAT) distributions, and temporal trends.
    """

    def __init__(self):
        # Lazy imports to avoid circular dependencies
        self._molecular_sample = None
        self._lab_order = None
        self._qc_record = None

    @property
    def MolecularSample(self):
        if self._molecular_sample is None:
            from molecular_diagnostics.models import MolecularSample
            self._molecular_sample = MolecularSample
        return self._molecular_sample

    @property
    def LabOrder(self):
        if self._lab_order is None:
            from lab_management.models import LabOrder
            self._lab_order = LabOrder
        return self._lab_order

    @property
    def QCRecord(self):
        if self._qc_record is None:
            from molecular_diagnostics.models import QCRecord
            self._qc_record = QCRecord
        return self._qc_record

    def get_samples_by_status(self, date_from: Optional[timezone.datetime] = None,
                               date_to: Optional[timezone.datetime] = None) -> Dict[str, int]:
        """
        Get count of molecular samples grouped by workflow status.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)

        Returns:
            Dictionary mapping status to count
        """
        queryset = self.MolecularSample.objects.all()

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        status_counts = queryset.values('workflow_status').annotate(
            count=Count('id')
        ).order_by('workflow_status')

        result = {
            'RECEIVED': 0,
            'EXTRACTED': 0,
            'AMPLIFIED': 0,
            'SEQUENCED': 0,
            'ANALYZED': 0,
            'REPORTED': 0,
            'CANCELLED': 0,
            'FAILED': 0,
        }

        for item in status_counts:
            result[item['workflow_status']] = item['count']

        return result

    def get_samples_by_priority(self, date_from: Optional[timezone.datetime] = None,
                                 date_to: Optional[timezone.datetime] = None) -> Dict[str, int]:
        """
        Get count of samples grouped by priority level.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)

        Returns:
            Dictionary mapping priority to count
        """
        queryset = self.MolecularSample.objects.all()

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        priority_counts = queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')

        result = {
            'ROUTINE': 0,
            'URGENT': 0,
            'STAT': 0,
        }

        for item in priority_counts:
            result[item['priority']] = item['count']

        return result

    def get_daily_sample_counts(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily sample counts for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of dictionaries with date and count
        """
        start_date = timezone.now() - timedelta(days=days)

        daily_counts = (
            self.MolecularSample.objects
            .filter(received_datetime__gte=start_date)
            .annotate(date=TruncDate('received_datetime'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        return list(daily_counts)

    def get_weekly_sample_counts(self, weeks: int = 12) -> List[Dict[str, Any]]:
        """
        Get weekly sample counts for the specified number of weeks.

        Args:
            weeks: Number of weeks to look back

        Returns:
            List of dictionaries with week and count
        """
        start_date = timezone.now() - timedelta(weeks=weeks)

        weekly_counts = (
            self.MolecularSample.objects
            .filter(received_datetime__gte=start_date)
            .annotate(week=TruncWeek('received_datetime'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )

        return list(weekly_counts)

    def calculate_tat_statistics(self, date_from: Optional[timezone.datetime] = None,
                                  date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Calculate turnaround time (TAT) statistics for completed samples.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)

        Returns:
            Dictionary with TAT statistics (avg, min, max, percentiles)
        """
        # Get completed samples with TAT calculation
        queryset = self.MolecularSample.objects.filter(
            workflow_status='REPORTED'
        )

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        # Calculate TAT for each sample in Python (since we need the history)
        tat_values = []
        for sample in queryset:
            tat = sample.get_turnaround_time()
            if tat is not None:
                tat_values.append(tat)

        if not tat_values:
            return {
                'average_hours': 0,
                'min_hours': 0,
                'max_hours': 0,
                'median_hours': 0,
                'p90_hours': 0,
                'p95_hours': 0,
                'sample_count': 0,
            }

        tat_values.sort()
        n = len(tat_values)

        def percentile(values, p):
            k = (len(values) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(values) - 1 else f
            return values[f] + (values[c] - values[f]) * (k - f)

        return {
            'average_hours': sum(tat_values) / n,
            'min_hours': min(tat_values),
            'max_hours': max(tat_values),
            'median_hours': percentile(tat_values, 50),
            'p90_hours': percentile(tat_values, 90),
            'p95_hours': percentile(tat_values, 95),
            'sample_count': n,
        }

    def get_tat_distribution(self, date_from: Optional[timezone.datetime] = None,
                              date_to: Optional[timezone.datetime] = None,
                              bucket_hours: int = 4) -> List[Dict[str, Any]]:
        """
        Get turnaround time distribution in buckets.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            bucket_hours: Size of each time bucket in hours

        Returns:
            List of dictionaries with bucket range and count
        """
        queryset = self.MolecularSample.objects.filter(
            workflow_status='REPORTED'
        )

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        # Build distribution buckets
        buckets = {}
        max_bucket = 120  # Maximum 120 hours (5 days)

        for i in range(0, max_bucket, bucket_hours):
            bucket_key = f"{i}-{i + bucket_hours}"
            buckets[bucket_key] = 0
        buckets[f"{max_bucket}+"] = 0

        for sample in queryset:
            tat = sample.get_turnaround_time()
            if tat is not None:
                if tat >= max_bucket:
                    buckets[f"{max_bucket}+"] += 1
                else:
                    bucket_start = int(tat // bucket_hours) * bucket_hours
                    bucket_key = f"{bucket_start}-{bucket_start + bucket_hours}"
                    if bucket_key in buckets:
                        buckets[bucket_key] += 1

        return [
            {'range': key, 'count': count}
            for key, count in buckets.items()
            if count > 0
        ]

    def get_samples_by_sample_type(self, date_from: Optional[timezone.datetime] = None,
                                    date_to: Optional[timezone.datetime] = None) -> List[Dict[str, Any]]:
        """
        Get count of samples grouped by sample type.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)

        Returns:
            List of dictionaries with sample type and count
        """
        queryset = self.MolecularSample.objects.all()

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        type_counts = (
            queryset
            .values('sample_type__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return list(type_counts)

    def get_qc_pass_fail_rates(self, date_from: Optional[timezone.datetime] = None,
                                date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Calculate QC pass/fail rates for the specified period.

        Args:
            date_from: Start date filter (optional)
            date_to: End date filter (optional)

        Returns:
            Dictionary with QC statistics
        """
        queryset = self.QCRecord.objects.all()

        if date_from:
            queryset = queryset.filter(recorded_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(recorded_at__lte=date_to)

        total = queryset.count()
        if total == 0:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warning': 0,
                'pending': 0,
                'pass_rate': 0.0,
                'fail_rate': 0.0,
            }

        status_counts = queryset.values('status').annotate(
            count=Count('id')
        )

        result = {
            'total': total,
            'passed': 0,
            'failed': 0,
            'warning': 0,
            'pending': 0,
        }

        for item in status_counts:
            status = item['status'].lower()
            if status in result:
                result[status] = item['count']

        result['pass_rate'] = (result['passed'] / total) * 100 if total > 0 else 0
        result['fail_rate'] = (result['failed'] / total) * 100 if total > 0 else 0

        return result

    def get_monthly_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get monthly sample statistics for trending.

        Args:
            months: Number of months to look back

        Returns:
            List of monthly statistics
        """
        start_date = timezone.now() - timedelta(days=months * 30)

        monthly_data = (
            self.MolecularSample.objects
            .filter(received_datetime__gte=start_date)
            .annotate(month=TruncMonth('received_datetime'))
            .values('month')
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(workflow_status='REPORTED')),
                failed=Count('id', filter=Q(workflow_status='FAILED')),
            )
            .order_by('month')
        )

        result = []
        for item in monthly_data:
            completion_rate = (item['completed'] / item['total'] * 100) if item['total'] > 0 else 0
            result.append({
                'month': item['month'],
                'total': item['total'],
                'completed': item['completed'],
                'failed': item['failed'],
                'completion_rate': round(completion_rate, 1),
            })

        return result

# analytics/services/metrics.py

from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal


class MetricsService:
    """
    Service for calculating Key Performance Indicators (KPIs) and dashboard metrics
    for laboratory operations.
    """

    def __init__(self):
        # Lazy imports to avoid circular dependencies
        self._molecular_sample = None
        self._lab_order = None
        self._instrument = None
        self._maintenance_record = None
        self._qc_record = None
        self._reagent = None
        self._molecular_reagent = None
        self._storage_unit = None
        self._storage_position = None

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
    def Instrument(self):
        if self._instrument is None:
            from equipment.models import Instrument
            self._instrument = Instrument
        return self._instrument

    @property
    def MaintenanceRecord(self):
        if self._maintenance_record is None:
            from equipment.models import MaintenanceRecord
            self._maintenance_record = MaintenanceRecord
        return self._maintenance_record

    @property
    def QCRecord(self):
        if self._qc_record is None:
            from molecular_diagnostics.models import QCRecord
            self._qc_record = QCRecord
        return self._qc_record

    @property
    def Reagent(self):
        if self._reagent is None:
            from reagents.models import Reagent
            self._reagent = Reagent
        return self._reagent

    @property
    def MolecularReagent(self):
        if self._molecular_reagent is None:
            from reagents.models import MolecularReagent
            self._molecular_reagent = MolecularReagent
        return self._molecular_reagent

    @property
    def StorageUnit(self):
        if self._storage_unit is None:
            from storage.models import StorageUnit
            self._storage_unit = StorageUnit
        return self._storage_unit

    @property
    def StoragePosition(self):
        if self._storage_position is None:
            from storage.models import StoragePosition
            self._storage_position = StoragePosition
        return self._storage_position

    # =====================
    # Sample KPIs
    # =====================

    def get_sample_kpis(self, date_from: Optional[timezone.datetime] = None,
                        date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Calculate sample-related KPIs.

        Returns:
            Dictionary containing sample KPIs
        """
        if date_from is None:
            date_from = timezone.now() - timedelta(days=30)
        if date_to is None:
            date_to = timezone.now()

        queryset = self.MolecularSample.objects.filter(
            received_datetime__gte=date_from,
            received_datetime__lte=date_to
        )

        total_samples = queryset.count()
        completed_samples = queryset.filter(workflow_status='REPORTED').count()
        failed_samples = queryset.filter(workflow_status='FAILED').count()
        in_progress = queryset.filter(
            workflow_status__in=['RECEIVED', 'EXTRACTED', 'AMPLIFIED', 'SEQUENCED', 'ANALYZED']
        ).count()

        # Calculate average TAT for completed samples
        completed = queryset.filter(workflow_status='REPORTED')
        tat_values = []
        for sample in completed:
            tat = sample.get_turnaround_time()
            if tat is not None:
                tat_values.append(tat)

        avg_tat = sum(tat_values) / len(tat_values) if tat_values else 0

        # Completion rate
        completion_rate = (completed_samples / total_samples * 100) if total_samples > 0 else 0

        # Today's samples
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_samples = self.MolecularSample.objects.filter(
            received_datetime__gte=today_start
        ).count()

        # Pending samples (not completed/failed/cancelled)
        pending_samples = self.MolecularSample.objects.filter(
            workflow_status__in=['RECEIVED', 'EXTRACTED', 'AMPLIFIED', 'SEQUENCED', 'ANALYZED']
        ).count()

        # STAT samples pending
        stat_pending = self.MolecularSample.objects.filter(
            priority='STAT',
            workflow_status__in=['RECEIVED', 'EXTRACTED', 'AMPLIFIED', 'SEQUENCED', 'ANALYZED']
        ).count()

        return {
            'total_samples': total_samples,
            'completed_samples': completed_samples,
            'failed_samples': failed_samples,
            'in_progress': in_progress,
            'completion_rate': round(completion_rate, 1),
            'average_tat_hours': round(avg_tat, 1),
            'today_samples': today_samples,
            'pending_samples': pending_samples,
            'stat_pending': stat_pending,
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
            }
        }

    # =====================
    # QC KPIs
    # =====================

    def get_qc_kpis(self, date_from: Optional[timezone.datetime] = None,
                   date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Calculate QC-related KPIs.

        Returns:
            Dictionary containing QC KPIs
        """
        if date_from is None:
            date_from = timezone.now() - timedelta(days=30)
        if date_to is None:
            date_to = timezone.now()

        queryset = self.QCRecord.objects.filter(
            recorded_at__gte=date_from,
            recorded_at__lte=date_to
        )

        total_qc = queryset.count()
        passed = queryset.filter(status='PASSED').count()
        failed = queryset.filter(status='FAILED').count()
        warnings = queryset.filter(status='WARNING').count()
        pending = queryset.filter(status='PENDING').count()

        pass_rate = (passed / total_qc * 100) if total_qc > 0 else 0
        fail_rate = (failed / total_qc * 100) if total_qc > 0 else 0

        # Critical failures (metrics marked as critical)
        critical_failures = queryset.filter(
            status='FAILED',
            metric__is_critical=True
        ).count()

        # QC reviews pending
        pending_reviews = queryset.filter(
            reviewed_at__isnull=True,
            status__in=['PASSED', 'FAILED', 'WARNING']
        ).count()

        return {
            'total_qc_records': total_qc,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'pending': pending,
            'pass_rate': round(pass_rate, 1),
            'fail_rate': round(fail_rate, 1),
            'critical_failures': critical_failures,
            'pending_reviews': pending_reviews,
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
            }
        }

    # =====================
    # Equipment KPIs
    # =====================

    def get_equipment_kpis(self) -> Dict[str, Any]:
        """
        Calculate equipment-related KPIs.

        Returns:
            Dictionary containing equipment KPIs
        """
        total_instruments = self.Instrument.objects.count()
        active_instruments = self.Instrument.objects.filter(status='ACTIVE').count()

        # Status breakdown
        status_counts = self.Instrument.objects.values('status').annotate(
            count=Count('id')
        )
        status_breakdown = {item['status']: item['count'] for item in status_counts}

        # Utilization rate (active / total)
        utilization_rate = (active_instruments / total_instruments * 100) if total_instruments > 0 else 0

        # Maintenance due
        today = timezone.now().date()
        maintenance_due = self.Instrument.objects.filter(
            next_maintenance__lte=today,
            is_active=True
        ).count()

        # Calibration due
        calibration_due = self.Instrument.objects.filter(
            next_calibration__lte=today,
            is_active=True
        ).count()

        # Upcoming maintenance (next 7 days)
        week_ahead = today + timedelta(days=7)
        upcoming_maintenance = self.Instrument.objects.filter(
            next_maintenance__gt=today,
            next_maintenance__lte=week_ahead,
            is_active=True
        ).count()

        # Under maintenance/repair
        under_maintenance = self.Instrument.objects.filter(
            status__in=['MAINTENANCE', 'REPAIR', 'CALIBRATION']
        ).count()

        # Warranty expiring soon (next 30 days)
        month_ahead = today + timedelta(days=30)
        warranty_expiring = self.Instrument.objects.filter(
            warranty_expiration__gt=today,
            warranty_expiration__lte=month_ahead,
            is_active=True
        ).count()

        return {
            'total_instruments': total_instruments,
            'active_instruments': active_instruments,
            'utilization_rate': round(utilization_rate, 1),
            'maintenance_due': maintenance_due,
            'calibration_due': calibration_due,
            'upcoming_maintenance': upcoming_maintenance,
            'under_maintenance': under_maintenance,
            'warranty_expiring': warranty_expiring,
            'status_breakdown': status_breakdown,
        }

    # =====================
    # Reagent KPIs
    # =====================

    def get_reagent_kpis(self) -> Dict[str, Any]:
        """
        Calculate reagent inventory KPIs.

        Returns:
            Dictionary containing reagent KPIs
        """
        total_reagents = self.Reagent.objects.count()
        total_molecular = self.MolecularReagent.objects.count()

        # Low stock items
        low_stock_count = 0
        for reagent in self.Reagent.objects.all():
            if reagent.is_below_reorder_level():
                low_stock_count += 1

        # Expired reagents
        today = timezone.now().date()
        expired_reagents = self.Reagent.objects.filter(
            expiration_date__lt=today
        ).count()

        # Expiring soon (next 30 days)
        month_ahead = today + timedelta(days=30)
        expiring_soon = self.Reagent.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=month_ahead
        ).count()

        # On order
        on_order = self.Reagent.objects.filter(on_order=True).count()

        # Total stock value (if opening_quantity represents value)
        total_stock = self.Reagent.objects.aggregate(
            total=Sum('quantity_in_stock')
        )['total'] or 0

        # Molecular reagents low stock
        molecular_low_stock = 0
        for reagent in self.MolecularReagent.objects.filter(is_active=True):
            if reagent.is_low_stock:
                molecular_low_stock += 1

        # Molecular reagents expired
        molecular_expired = self.MolecularReagent.objects.filter(
            expiration_date__lt=today,
            is_active=True
        ).count()

        # Category breakdown
        category_counts = self.Reagent.objects.values('category').annotate(
            count=Count('id')
        )
        category_breakdown = {item['category']: item['count'] for item in category_counts}

        return {
            'total_reagents': total_reagents,
            'total_molecular_reagents': total_molecular,
            'low_stock_count': low_stock_count,
            'expired_reagents': expired_reagents,
            'expiring_soon': expiring_soon,
            'on_order': on_order,
            'total_stock_units': total_stock,
            'molecular_low_stock': molecular_low_stock,
            'molecular_expired': molecular_expired,
            'category_breakdown': category_breakdown,
        }

    # =====================
    # Storage KPIs
    # =====================

    def get_storage_kpis(self) -> Dict[str, Any]:
        """
        Calculate storage utilization KPIs.

        Returns:
            Dictionary containing storage KPIs
        """
        total_units = self.StorageUnit.objects.count()
        active_units = self.StorageUnit.objects.filter(status='ACTIVE').count()

        # Total positions
        total_positions = self.StoragePosition.objects.count()
        occupied_positions = self.StoragePosition.objects.filter(is_occupied=True).count()
        reserved_positions = self.StoragePosition.objects.filter(is_reserved=True).count()
        available_positions = total_positions - occupied_positions - reserved_positions

        # Utilization rate
        utilization_rate = (occupied_positions / total_positions * 100) if total_positions > 0 else 0

        # Units by type
        type_counts = self.StorageUnit.objects.values('unit_type').annotate(
            count=Count('id')
        )
        type_breakdown = {item['unit_type']: item['count'] for item in type_counts}

        # Units by status
        status_counts = self.StorageUnit.objects.values('status').annotate(
            count=Count('id')
        )
        status_breakdown = {item['status']: item['count'] for item in status_counts}

        # Critical storage (near full - >90% utilized)
        critical_units = []
        for unit in self.StorageUnit.objects.filter(status='ACTIVE'):
            total = unit.total_positions
            occupied = unit.occupied_positions
            if total > 0 and (occupied / total) > 0.9:
                critical_units.append(unit.code)

        return {
            'total_units': total_units,
            'active_units': active_units,
            'total_positions': total_positions,
            'occupied_positions': occupied_positions,
            'reserved_positions': reserved_positions,
            'available_positions': available_positions,
            'utilization_rate': round(utilization_rate, 1),
            'type_breakdown': type_breakdown,
            'status_breakdown': status_breakdown,
            'critical_units_count': len(critical_units),
            'critical_units': critical_units[:5],  # Return up to 5 critical units
        }

    # =====================
    # Combined Dashboard KPIs
    # =====================

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get all dashboard KPIs in a single call.

        Returns:
            Dictionary containing all KPI categories
        """
        return {
            'samples': self.get_sample_kpis(),
            'qc': self.get_qc_kpis(),
            'equipment': self.get_equipment_kpis(),
            'reagents': self.get_reagent_kpis(),
            'storage': self.get_storage_kpis(),
            'generated_at': timezone.now().isoformat(),
        }

    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of critical alerts that need attention.

        Returns:
            List of alert dictionaries with severity and message
        """
        alerts = []
        today = timezone.now().date()

        # STAT samples pending
        stat_pending = self.MolecularSample.objects.filter(
            priority='STAT',
            workflow_status__in=['RECEIVED', 'EXTRACTED', 'AMPLIFIED', 'SEQUENCED', 'ANALYZED']
        ).count()
        if stat_pending > 0:
            alerts.append({
                'severity': 'critical',
                'category': 'samples',
                'title': 'STAT Samples Pending',
                'message': f'{stat_pending} STAT priority sample(s) require immediate attention',
                'icon': 'exclamation-triangle',
            })

        # Expired reagents
        expired = self.Reagent.objects.filter(
            expiration_date__lt=today,
            quantity_in_stock__gt=0
        ).count()
        if expired > 0:
            alerts.append({
                'severity': 'critical',
                'category': 'reagents',
                'title': 'Expired Reagents',
                'message': f'{expired} reagent(s) have expired and should not be used',
                'icon': 'flask',
            })

        # Maintenance overdue
        maintenance_overdue = self.Instrument.objects.filter(
            next_maintenance__lt=today,
            is_active=True
        ).count()
        if maintenance_overdue > 0:
            alerts.append({
                'severity': 'warning',
                'category': 'equipment',
                'title': 'Maintenance Overdue',
                'message': f'{maintenance_overdue} instrument(s) are overdue for maintenance',
                'icon': 'wrench',
            })

        # Calibration overdue
        calibration_overdue = self.Instrument.objects.filter(
            next_calibration__lt=today,
            is_active=True
        ).count()
        if calibration_overdue > 0:
            alerts.append({
                'severity': 'critical',
                'category': 'equipment',
                'title': 'Calibration Overdue',
                'message': f'{calibration_overdue} instrument(s) are overdue for calibration',
                'icon': 'cog',
            })

        # QC failures today
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qc_failures = self.QCRecord.objects.filter(
            recorded_at__gte=today_start,
            status='FAILED'
        ).count()
        if qc_failures > 0:
            alerts.append({
                'severity': 'warning',
                'category': 'qc',
                'title': 'QC Failures Today',
                'message': f'{qc_failures} QC failure(s) recorded today',
                'icon': 'times-circle',
            })

        # Instruments under repair
        under_repair = self.Instrument.objects.filter(status='REPAIR').count()
        if under_repair > 0:
            alerts.append({
                'severity': 'info',
                'category': 'equipment',
                'title': 'Instruments Under Repair',
                'message': f'{under_repair} instrument(s) are currently under repair',
                'icon': 'tools',
            })

        # Low stock reagents
        low_stock = 0
        for reagent in self.Reagent.objects.all():
            if reagent.is_below_reorder_level():
                low_stock += 1
        if low_stock > 0:
            alerts.append({
                'severity': 'warning',
                'category': 'reagents',
                'title': 'Low Stock Alert',
                'message': f'{low_stock} reagent(s) are below reorder level',
                'icon': 'box',
            })

        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return alerts

    def get_today_summary(self) -> Dict[str, Any]:
        """
        Get today's activity summary.

        Returns:
            Dictionary with today's metrics
        """
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Samples received today
        samples_received = self.MolecularSample.objects.filter(
            received_datetime__gte=today_start
        ).count()

        # Samples completed today
        samples_completed = self.MolecularSample.objects.filter(
            workflow_status='REPORTED',
            updated_at__gte=today_start
        ).count()

        # QC records today
        qc_today = self.QCRecord.objects.filter(
            recorded_at__gte=today_start
        ).count()
        qc_passed = self.QCRecord.objects.filter(
            recorded_at__gte=today_start,
            status='PASSED'
        ).count()

        # Maintenance scheduled today
        today = timezone.now().date()
        maintenance_today = self.MaintenanceRecord.objects.filter(
            scheduled_date=today
        ).count()

        return {
            'date': today.isoformat(),
            'samples_received': samples_received,
            'samples_completed': samples_completed,
            'qc_records': qc_today,
            'qc_passed': qc_passed,
            'qc_pass_rate': round((qc_passed / qc_today * 100) if qc_today > 0 else 0, 1),
            'maintenance_scheduled': maintenance_today,
        }

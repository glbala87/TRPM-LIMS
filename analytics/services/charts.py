# analytics/services/charts.py

from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional
import json


class ChartDataService:
    """
    Service for generating chart data for samples, results, equipment,
    and other analytics visualizations.
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

    # =====================
    # Sample Charts
    # =====================

    def get_sample_status_pie_chart(self, date_from: Optional[timezone.datetime] = None,
                                     date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Generate pie chart data for sample status distribution.

        Returns:
            Chart.js compatible data structure
        """
        queryset = self.MolecularSample.objects.all()

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        status_counts = queryset.values('workflow_status').annotate(
            count=Count('id')
        ).order_by('workflow_status')

        status_colors = {
            'RECEIVED': '#3498db',
            'EXTRACTED': '#2ecc71',
            'AMPLIFIED': '#f39c12',
            'SEQUENCED': '#9b59b6',
            'ANALYZED': '#1abc9c',
            'REPORTED': '#27ae60',
            'CANCELLED': '#95a5a6',
            'FAILED': '#e74c3c',
        }

        labels = []
        data = []
        colors = []

        for item in status_counts:
            status = item['workflow_status']
            labels.append(status.replace('_', ' ').title())
            data.append(item['count'])
            colors.append(status_colors.get(status, '#bdc3c7'))

        return {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': 'Samples by Status'
                    }
                }
            }
        }

    def get_sample_trend_line_chart(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate line chart data for sample reception trend over time.

        Args:
            days: Number of days to display

        Returns:
            Chart.js compatible data structure
        """
        start_date = timezone.now() - timedelta(days=days)

        daily_counts = (
            self.MolecularSample.objects
            .filter(received_datetime__gte=start_date)
            .annotate(date=TruncDate('received_datetime'))
            .values('date')
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(workflow_status='REPORTED')),
            )
            .order_by('date')
        )

        labels = []
        total_data = []
        completed_data = []

        for item in daily_counts:
            labels.append(item['date'].strftime('%Y-%m-%d'))
            total_data.append(item['total'])
            completed_data.append(item['completed'])

        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Total Received',
                        'data': total_data,
                        'borderColor': '#3498db',
                        'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                        'fill': True,
                        'tension': 0.4,
                    },
                    {
                        'label': 'Completed',
                        'data': completed_data,
                        'borderColor': '#27ae60',
                        'backgroundColor': 'rgba(39, 174, 96, 0.1)',
                        'fill': True,
                        'tension': 0.4,
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Sample Trend (Last {days} Days)'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                    }
                }
            }
        }

    def get_sample_priority_bar_chart(self, date_from: Optional[timezone.datetime] = None,
                                       date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Generate bar chart data for sample priority distribution.

        Returns:
            Chart.js compatible data structure
        """
        queryset = self.MolecularSample.objects.all()

        if date_from:
            queryset = queryset.filter(received_datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(received_datetime__lte=date_to)

        priority_counts = queryset.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')

        priority_colors = {
            'ROUTINE': '#3498db',
            'URGENT': '#f39c12',
            'STAT': '#e74c3c',
        }

        labels = []
        data = []
        colors = []

        for item in priority_counts:
            priority = item['priority']
            labels.append(priority.title())
            data.append(item['count'])
            colors.append(priority_colors.get(priority, '#bdc3c7'))

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Samples by Priority',
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Samples by Priority'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                    }
                }
            }
        }

    # =====================
    # Results Charts
    # =====================

    def get_qc_results_doughnut_chart(self, date_from: Optional[timezone.datetime] = None,
                                       date_to: Optional[timezone.datetime] = None) -> Dict[str, Any]:
        """
        Generate doughnut chart data for QC pass/fail distribution.

        Returns:
            Chart.js compatible data structure
        """
        queryset = self.QCRecord.objects.all()

        if date_from:
            queryset = queryset.filter(recorded_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(recorded_at__lte=date_to)

        status_counts = queryset.values('status').annotate(
            count=Count('id')
        )

        status_colors = {
            'PASSED': '#27ae60',
            'FAILED': '#e74c3c',
            'WARNING': '#f39c12',
            'PENDING': '#95a5a6',
        }

        labels = []
        data = []
        colors = []

        for item in status_counts:
            status = item['status']
            labels.append(status.title())
            data.append(item['count'])
            colors.append(status_colors.get(status, '#bdc3c7'))

        return {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 2,
                    'borderColor': '#ffffff',
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'bottom',
                    },
                    'title': {
                        'display': True,
                        'text': 'QC Results Distribution'
                    }
                }
            }
        }

    def get_qc_trend_chart(self, weeks: int = 8) -> Dict[str, Any]:
        """
        Generate line chart for QC pass rate trend over time.

        Args:
            weeks: Number of weeks to display

        Returns:
            Chart.js compatible data structure
        """
        start_date = timezone.now() - timedelta(weeks=weeks)

        weekly_data = (
            self.QCRecord.objects
            .filter(recorded_at__gte=start_date)
            .annotate(week=TruncWeek('recorded_at'))
            .values('week')
            .annotate(
                total=Count('id'),
                passed=Count('id', filter=Q(status='PASSED')),
                failed=Count('id', filter=Q(status='FAILED')),
            )
            .order_by('week')
        )

        labels = []
        pass_rates = []

        for item in weekly_data:
            labels.append(item['week'].strftime('%Y-%m-%d'))
            rate = (item['passed'] / item['total'] * 100) if item['total'] > 0 else 0
            pass_rates.append(round(rate, 1))

        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'QC Pass Rate (%)',
                    'data': pass_rates,
                    'borderColor': '#27ae60',
                    'backgroundColor': 'rgba(39, 174, 96, 0.1)',
                    'fill': True,
                    'tension': 0.4,
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'QC Pass Rate Trend (Last {weeks} Weeks)'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100,
                        'title': {
                            'display': True,
                            'text': 'Pass Rate (%)'
                        }
                    }
                }
            }
        }

    # =====================
    # Equipment Charts
    # =====================

    def get_equipment_status_chart(self) -> Dict[str, Any]:
        """
        Generate pie chart data for equipment status distribution.

        Returns:
            Chart.js compatible data structure
        """
        status_counts = self.Instrument.objects.values('status').annotate(
            count=Count('id')
        )

        status_colors = {
            'ACTIVE': '#27ae60',
            'MAINTENANCE': '#f39c12',
            'CALIBRATION': '#3498db',
            'REPAIR': '#e74c3c',
            'RETIRED': '#95a5a6',
            'OUT_OF_SERVICE': '#7f8c8d',
        }

        labels = []
        data = []
        colors = []

        for item in status_counts:
            status = item['status']
            labels.append(status.replace('_', ' ').title())
            data.append(item['count'])
            colors.append(status_colors.get(status, '#bdc3c7'))

        return {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': 'Equipment Status Distribution'
                    }
                }
            }
        }

    def get_equipment_utilization_chart(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate bar chart for equipment utilization based on maintenance records.

        Args:
            days: Number of days to analyze

        Returns:
            Chart.js compatible data structure
        """
        start_date = timezone.now() - timedelta(days=days)

        # Get active instruments with their maintenance counts
        instruments = self.Instrument.objects.filter(is_active=True)[:10]

        labels = []
        maintenance_days = []
        available_days = []

        for instrument in instruments:
            labels.append(instrument.name[:20])

            # Count days under maintenance/calibration/repair in period
            maintenance_count = self.MaintenanceRecord.objects.filter(
                instrument=instrument,
                scheduled_date__gte=start_date.date(),
                status__in=['SCHEDULED', 'IN_PROGRESS', 'COMPLETED']
            ).count()

            # Simplified calculation - each maintenance record represents ~1 day
            maint_days = min(maintenance_count, days)
            avail_days = days - maint_days

            maintenance_days.append(maint_days)
            available_days.append(avail_days)

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Available Days',
                        'data': available_days,
                        'backgroundColor': '#27ae60',
                    },
                    {
                        'label': 'Maintenance Days',
                        'data': maintenance_days,
                        'backgroundColor': '#f39c12',
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Equipment Utilization (Last {days} Days)'
                    }
                },
                'scales': {
                    'x': {
                        'stacked': True,
                    },
                    'y': {
                        'stacked': True,
                        'beginAtZero': True,
                    }
                }
            }
        }

    def get_maintenance_type_chart(self, months: int = 6) -> Dict[str, Any]:
        """
        Generate chart showing maintenance activities by type.

        Args:
            months: Number of months to analyze

        Returns:
            Chart.js compatible data structure
        """
        start_date = timezone.now() - timedelta(days=months * 30)

        type_counts = (
            self.MaintenanceRecord.objects
            .filter(scheduled_date__gte=start_date.date())
            .values('maintenance_type')
            .annotate(count=Count('id'))
        )

        type_colors = {
            'PREVENTIVE': '#27ae60',
            'CORRECTIVE': '#e74c3c',
            'CALIBRATION': '#3498db',
            'QUALIFICATION': '#9b59b6',
            'REPAIR': '#f39c12',
            'UPGRADE': '#1abc9c',
            'INSPECTION': '#34495e',
        }

        labels = []
        data = []
        colors = []

        for item in type_counts:
            mtype = item['maintenance_type']
            labels.append(mtype.replace('_', ' ').title())
            data.append(item['count'])
            colors.append(type_colors.get(mtype, '#bdc3c7'))

        return {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 2,
                    'borderColor': '#ffffff',
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': f'Maintenance by Type (Last {months} Months)'
                    }
                }
            }
        }

    # =====================
    # Reagent Charts
    # =====================

    def get_reagent_stock_chart(self) -> Dict[str, Any]:
        """
        Generate horizontal bar chart for reagent stock levels.

        Returns:
            Chart.js compatible data structure
        """
        reagents = self.Reagent.objects.filter(
            quantity_in_stock__gt=0
        ).order_by('-quantity_in_stock')[:15]

        labels = []
        stock_data = []
        colors = []

        for reagent in reagents:
            labels.append(reagent.name[:25])
            stock_data.append(reagent.quantity_in_stock)

            # Color based on stock level
            if reagent.is_below_reorder_level():
                colors.append('#e74c3c')  # Red for low stock
            else:
                colors.append('#27ae60')  # Green for adequate stock

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Quantity in Stock',
                    'data': stock_data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Reagent Stock Levels'
                    }
                },
                'scales': {
                    'x': {
                        'beginAtZero': True,
                    }
                }
            }
        }

    def get_reagent_expiry_chart(self, days: int = 90) -> Dict[str, Any]:
        """
        Generate chart showing reagents expiring soon.

        Args:
            days: Look-ahead period for expiration

        Returns:
            Chart.js compatible data structure
        """
        expiry_date = timezone.now().date() + timedelta(days=days)

        expiring_reagents = self.Reagent.objects.filter(
            expiration_date__lte=expiry_date,
            expiration_date__gte=timezone.now().date(),
            quantity_in_stock__gt=0
        ).order_by('expiration_date')[:10]

        labels = []
        data = []
        colors = []

        today = timezone.now().date()

        for reagent in expiring_reagents:
            labels.append(reagent.name[:20])
            days_until_expiry = (reagent.expiration_date - today).days
            data.append(days_until_expiry)

            # Color based on urgency
            if days_until_expiry <= 7:
                colors.append('#e74c3c')  # Red - critical
            elif days_until_expiry <= 30:
                colors.append('#f39c12')  # Orange - warning
            else:
                colors.append('#f1c40f')  # Yellow - attention

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Days Until Expiry',
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Reagents Expiring Within {days} Days'
                    }
                },
                'scales': {
                    'x': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Days Until Expiry'
                        }
                    }
                }
            }
        }

    def get_reagent_category_chart(self) -> Dict[str, Any]:
        """
        Generate pie chart for reagent distribution by category.

        Returns:
            Chart.js compatible data structure
        """
        category_counts = self.Reagent.objects.values('category').annotate(
            count=Count('id')
        )

        category_colors = {
            'BIOASSAY_SNIBE': '#3498db',
            'MAGLUMI_SNIBE': '#2ecc71',
            'BIG': '#9b59b6',
        }

        labels = []
        data = []
        colors = []

        for item in category_counts:
            category = item['category']
            labels.append(category.replace('_', ' ').title())
            data.append(item['count'])
            colors.append(category_colors.get(category, '#bdc3c7'))

        return {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 1,
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': 'Reagents by Category'
                    }
                }
            }
        }

    def get_all_dashboard_charts(self, days: int = 30) -> Dict[str, Any]:
        """
        Get all dashboard charts in a single call.

        Args:
            days: Default time range for trend charts

        Returns:
            Dictionary containing all chart configurations
        """
        return {
            'sample_status': self.get_sample_status_pie_chart(),
            'sample_trend': self.get_sample_trend_line_chart(days=days),
            'sample_priority': self.get_sample_priority_bar_chart(),
            'qc_results': self.get_qc_results_doughnut_chart(),
            'qc_trend': self.get_qc_trend_chart(weeks=8),
            'equipment_status': self.get_equipment_status_chart(),
            'equipment_utilization': self.get_equipment_utilization_chart(days=days),
            'reagent_stock': self.get_reagent_stock_chart(),
            'reagent_expiry': self.get_reagent_expiry_chart(days=90),
        }

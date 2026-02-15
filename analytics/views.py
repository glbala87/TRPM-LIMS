# analytics/views.py

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from typing import Optional
import json

from .services import SampleStatisticsService, ChartDataService, MetricsService


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main analytics dashboard view displaying KPIs, charts, and alerts.
    """
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize services
        stats_service = SampleStatisticsService()
        chart_service = ChartDataService()
        metrics_service = MetricsService()

        # Get date range from request or default to last 30 days
        days = int(self.request.GET.get('days', 30))
        date_to = timezone.now()
        date_from = date_to - timedelta(days=days)

        # Get KPIs
        try:
            context['sample_kpis'] = metrics_service.get_sample_kpis(date_from, date_to)
        except Exception:
            context['sample_kpis'] = {}

        try:
            context['qc_kpis'] = metrics_service.get_qc_kpis(date_from, date_to)
        except Exception:
            context['qc_kpis'] = {}

        try:
            context['equipment_kpis'] = metrics_service.get_equipment_kpis()
        except Exception:
            context['equipment_kpis'] = {}

        try:
            context['reagent_kpis'] = metrics_service.get_reagent_kpis()
        except Exception:
            context['reagent_kpis'] = {}

        try:
            context['storage_kpis'] = metrics_service.get_storage_kpis()
        except Exception:
            context['storage_kpis'] = {}

        # Get alerts
        try:
            context['alerts'] = metrics_service.get_critical_alerts()
        except Exception:
            context['alerts'] = []

        # Get today's summary
        try:
            context['today_summary'] = metrics_service.get_today_summary()
        except Exception:
            context['today_summary'] = {}

        # Chart data (as JSON for JavaScript)
        try:
            context['sample_status_chart'] = json.dumps(
                chart_service.get_sample_status_pie_chart(date_from, date_to)
            )
        except Exception:
            context['sample_status_chart'] = '{}'

        try:
            context['sample_trend_chart'] = json.dumps(
                chart_service.get_sample_trend_line_chart(days=days)
            )
        except Exception:
            context['sample_trend_chart'] = '{}'

        try:
            context['qc_results_chart'] = json.dumps(
                chart_service.get_qc_results_doughnut_chart(date_from, date_to)
            )
        except Exception:
            context['qc_results_chart'] = '{}'

        try:
            context['equipment_status_chart'] = json.dumps(
                chart_service.get_equipment_status_chart()
            )
        except Exception:
            context['equipment_status_chart'] = '{}'

        # Additional context
        context['selected_days'] = days
        context['date_from'] = date_from
        context['date_to'] = date_to

        return context


class DashboardSummaryAPIView(LoginRequiredMixin, View):
    """
    API endpoint returning complete dashboard summary as JSON.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            summary = metrics_service.get_dashboard_summary()
            return JsonResponse({
                'status': 'success',
                'data': summary,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class SampleStatisticsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for sample statistics.
    """

    def get(self, request, *args, **kwargs):
        stats_service = SampleStatisticsService()

        # Parse date parameters
        date_from = self._parse_date(request.GET.get('date_from'))
        date_to = self._parse_date(request.GET.get('date_to'))

        try:
            data = {
                'samples_by_status': stats_service.get_samples_by_status(date_from, date_to),
                'samples_by_priority': stats_service.get_samples_by_priority(date_from, date_to),
                'tat_statistics': stats_service.calculate_tat_statistics(date_from, date_to),
            }
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)

    def _parse_date(self, date_str: Optional[str]) -> Optional[timezone.datetime]:
        if not date_str:
            return None
        try:
            return timezone.datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None


class SamplesByStatusAPIView(LoginRequiredMixin, View):
    """
    API endpoint for samples grouped by status.
    """

    def get(self, request, *args, **kwargs):
        stats_service = SampleStatisticsService()

        try:
            data = stats_service.get_samples_by_status()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class TATDistributionAPIView(LoginRequiredMixin, View):
    """
    API endpoint for turnaround time distribution.
    """

    def get(self, request, *args, **kwargs):
        stats_service = SampleStatisticsService()
        bucket_hours = int(request.GET.get('bucket_hours', 4))

        try:
            data = stats_service.get_tat_distribution(bucket_hours=bucket_hours)
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class QCStatisticsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for QC pass/fail statistics.
    """

    def get(self, request, *args, **kwargs):
        stats_service = SampleStatisticsService()

        try:
            data = stats_service.get_qc_pass_fail_rates()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class EquipmentMetricsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for equipment KPIs.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            data = metrics_service.get_equipment_kpis()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class ReagentMetricsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for reagent inventory KPIs.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            data = metrics_service.get_reagent_kpis()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class StorageMetricsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for storage utilization KPIs.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            data = metrics_service.get_storage_kpis()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class AlertsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for critical alerts.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            alerts = metrics_service.get_critical_alerts()
            return JsonResponse({
                'status': 'success',
                'data': alerts,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class ChartDataAPIView(LoginRequiredMixin, View):
    """
    API endpoint for chart data.
    """

    def get(self, request, *args, **kwargs):
        chart_service = ChartDataService()
        chart_type = kwargs.get('chart_type', 'sample_status')
        days = int(request.GET.get('days', 30))

        chart_methods = {
            'sample_status': lambda: chart_service.get_sample_status_pie_chart(),
            'sample_trend': lambda: chart_service.get_sample_trend_line_chart(days=days),
            'sample_priority': lambda: chart_service.get_sample_priority_bar_chart(),
            'qc_results': lambda: chart_service.get_qc_results_doughnut_chart(),
            'qc_trend': lambda: chart_service.get_qc_trend_chart(weeks=8),
            'equipment_status': lambda: chart_service.get_equipment_status_chart(),
            'equipment_utilization': lambda: chart_service.get_equipment_utilization_chart(days=days),
            'maintenance_type': lambda: chart_service.get_maintenance_type_chart(months=6),
            'reagent_stock': lambda: chart_service.get_reagent_stock_chart(),
            'reagent_expiry': lambda: chart_service.get_reagent_expiry_chart(days=90),
            'reagent_category': lambda: chart_service.get_reagent_category_chart(),
        }

        if chart_type not in chart_methods:
            return JsonResponse({
                'status': 'error',
                'message': f'Unknown chart type: {chart_type}',
            }, status=400)

        try:
            data = chart_methods[chart_type]()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class TodaySummaryAPIView(LoginRequiredMixin, View):
    """
    API endpoint for today's activity summary.
    """

    def get(self, request, *args, **kwargs):
        metrics_service = MetricsService()

        try:
            data = metrics_service.get_today_summary()
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


class MonthlyTrendsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for monthly sample trends.
    """

    def get(self, request, *args, **kwargs):
        stats_service = SampleStatisticsService()
        months = int(request.GET.get('months', 12))

        try:
            data = stats_service.get_monthly_trends(months=months)
            return JsonResponse({
                'status': 'success',
                'data': data,
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)


# Widget views for AJAX loading

class SampleStatusWidgetView(LoginRequiredMixin, TemplateView):
    """
    Widget view for sample status distribution.
    """
    template_name = 'analytics/widgets/sample_status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats_service = SampleStatisticsService()
        context['status_data'] = stats_service.get_samples_by_status()
        return context


class QCStatusWidgetView(LoginRequiredMixin, TemplateView):
    """
    Widget view for QC status summary.
    """
    template_name = 'analytics/widgets/qc_status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats_service = SampleStatisticsService()
        context['qc_data'] = stats_service.get_qc_pass_fail_rates()
        return context


class AlertsWidgetView(LoginRequiredMixin, TemplateView):
    """
    Widget view for critical alerts.
    """
    template_name = 'analytics/widgets/alerts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metrics_service = MetricsService()
        context['alerts'] = metrics_service.get_critical_alerts()
        return context

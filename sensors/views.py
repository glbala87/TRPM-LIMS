# sensors/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from .models import SensorType, MonitoringDevice, SensorReading, SensorAlert


class SensorTypeListView(LoginRequiredMixin, ListView):
    model = SensorType
    template_name = 'sensors/type_list.html'
    context_object_name = 'sensor_types'

    def get_queryset(self):
        return SensorType.objects.filter(is_active=True)


class MonitoringDeviceListView(LoginRequiredMixin, ListView):
    model = MonitoringDevice
    template_name = 'sensors/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        queryset = MonitoringDevice.objects.select_related('sensor_type', 'storage_unit')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        sensor_type = self.request.GET.get('type')
        if sensor_type:
            queryset = queryset.filter(sensor_type_id=sensor_type)

        return queryset.order_by('name')


class MonitoringDeviceDetailView(LoginRequiredMixin, DetailView):
    model = MonitoringDevice
    template_name = 'sensors/device_detail.html'
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_readings'] = self.object.readings.order_by('-timestamp')[:50]
        context['active_alerts'] = self.object.alerts.filter(status='ACTIVE')
        return context


class DeviceReadingsView(LoginRequiredMixin, ListView):
    model = SensorReading
    template_name = 'sensors/device_readings.html'
    context_object_name = 'readings'
    paginate_by = 100

    def get_queryset(self):
        device_id = self.kwargs.get('pk')
        return SensorReading.objects.filter(device_id=device_id).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['device'] = get_object_or_404(MonitoringDevice, pk=self.kwargs.get('pk'))
        return context


class SensorReadingListView(LoginRequiredMixin, ListView):
    model = SensorReading
    template_name = 'sensors/reading_list.html'
    context_object_name = 'readings'
    paginate_by = 100

    def get_queryset(self):
        queryset = SensorReading.objects.select_related('device')

        device = self.request.GET.get('device')
        if device:
            queryset = queryset.filter(device_id=device)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-timestamp')


class SensorAlertListView(LoginRequiredMixin, ListView):
    model = SensorAlert
    template_name = 'sensors/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 50

    def get_queryset(self):
        queryset = SensorAlert.objects.select_related('device', 'acknowledged_by', 'resolved_by')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        else:
            # By default show active alerts first
            queryset = queryset.exclude(status='RESOLVED')

        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset.order_by('-triggered_at')


class SensorAlertDetailView(LoginRequiredMixin, DetailView):
    model = SensorAlert
    template_name = 'sensors/alert_detail.html'
    context_object_name = 'alert'


@login_required
def acknowledge_alert(request, pk):
    alert = get_object_or_404(SensorAlert, pk=pk)

    if alert.status != 'ACTIVE':
        messages.error(request, "This alert cannot be acknowledged.")
        return redirect('sensors:alert_detail', pk=pk)

    alert.acknowledge(request.user)
    messages.success(request, "Alert acknowledged.")
    return redirect('sensors:alert_detail', pk=pk)


@login_required
def resolve_alert(request, pk):
    alert = get_object_or_404(SensorAlert, pk=pk)

    if alert.status == 'RESOLVED':
        messages.error(request, "This alert is already resolved.")
        return redirect('sensors:alert_detail', pk=pk)

    notes = request.POST.get('notes', '')
    alert.resolve(request.user, notes)
    messages.success(request, "Alert resolved.")
    return redirect('sensors:alert_list')


class SensorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'sensors/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Active devices with issues
        context['devices_in_alarm'] = MonitoringDevice.objects.filter(
            status='ACTIVE'
        ).select_related('sensor_type')

        context['active_alerts'] = SensorAlert.objects.filter(
            status='ACTIVE'
        ).select_related('device').order_by('-triggered_at')[:10]

        context['critical_alerts'] = SensorAlert.objects.filter(
            status='ACTIVE', severity='CRITICAL'
        ).count()

        context['warning_alerts'] = SensorAlert.objects.filter(
            status='ACTIVE', severity='WARNING'
        ).count()

        return context


@csrf_exempt
@require_POST
def submit_reading(request):
    """API endpoint for sensors to submit readings."""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        value = data.get('value')

        device = MonitoringDevice.objects.get(device_id=device_id)

        reading = SensorReading.objects.create(
            device=device,
            value=value,
            raw_data=data.get('raw_data', {})
        )

        # Check if alert should be created
        if reading.status in ['WARNING', 'CRITICAL']:
            SensorAlert.objects.create(
                device=device,
                reading=reading,
                severity=reading.status,
                message=f"{device.name} reading {value} {device.sensor_type.unit} is {reading.status.lower()}"
            )

        return JsonResponse({
            'status': 'success',
            'reading_id': reading.id,
            'reading_status': reading.status
        })

    except MonitoringDevice.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

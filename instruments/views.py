# instruments/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
import json

from .models import InstrumentConnection, MessageLog, WorklistExport
from .services.connection_manager import ConnectionManager
from .services.worklist_exporter import WorklistExporter


class ConnectionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all instrument connections."""
    model = InstrumentConnection
    template_name = 'instruments/connection_list.html'
    context_object_name = 'connections'
    permission_required = 'instruments.view_instrumentconnection'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('instrument')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(connection_status=status)

        # Filter by protocol
        protocol = self.request.GET.get('protocol')
        if protocol:
            queryset = queryset.filter(protocol=protocol)

        # Filter by active
        active = self.request.GET.get('active')
        if active == 'true':
            queryset = queryset.filter(is_active=True)
        elif active == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocols'] = InstrumentConnection.PROTOCOL_CHOICES
        context['statuses'] = [
            ('CONNECTED', 'Connected'),
            ('DISCONNECTED', 'Disconnected'),
            ('ERROR', 'Error'),
        ]
        return context


class ConnectionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """View connection details and recent messages."""
    model = InstrumentConnection
    template_name = 'instruments/connection_detail.html'
    context_object_name = 'connection'
    permission_required = 'instruments.view_instrumentconnection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recent messages
        context['recent_messages'] = self.object.message_logs.all()[:50]

        # Message statistics
        today = timezone.now().date()
        context['today_stats'] = {
            'inbound': self.object.message_logs.filter(
                direction='INBOUND',
                timestamp__date=today
            ).count(),
            'outbound': self.object.message_logs.filter(
                direction='OUTBOUND',
                timestamp__date=today
            ).count(),
            'errors': self.object.message_logs.filter(
                status='ERROR',
                timestamp__date=today
            ).count(),
        }

        return context


@login_required
@permission_required('instruments.change_instrumentconnection')
@require_POST
def start_connection(request, pk):
    """Start an instrument connection."""
    connection = get_object_or_404(InstrumentConnection, pk=pk)

    try:
        manager = ConnectionManager()
        manager.start_connection(connection)
        messages.success(request, f'Connection to {connection.name} started.')
    except Exception as e:
        messages.error(request, f'Failed to start connection: {str(e)}')

    return redirect('instruments:connection_detail', pk=pk)


@login_required
@permission_required('instruments.change_instrumentconnection')
@require_POST
def stop_connection(request, pk):
    """Stop an instrument connection."""
    connection = get_object_or_404(InstrumentConnection, pk=pk)

    try:
        manager = ConnectionManager()
        manager.stop_connection(connection)
        messages.success(request, f'Connection to {connection.name} stopped.')
    except Exception as e:
        messages.error(request, f'Failed to stop connection: {str(e)}')

    return redirect('instruments:connection_detail', pk=pk)


@login_required
@permission_required('instruments.view_instrumentconnection')
@require_POST
def test_connection(request, pk):
    """Test an instrument connection."""
    connection = get_object_or_404(InstrumentConnection, pk=pk)

    try:
        manager = ConnectionManager()
        result = manager.test_connection(connection)

        if result['success']:
            messages.success(request, f'Connection test successful! Response time: {result.get("response_time", "N/A")}ms')
        else:
            messages.warning(request, f'Connection test failed: {result.get("error", "Unknown error")}')
    except Exception as e:
        messages.error(request, f'Connection test error: {str(e)}')

    return redirect('instruments:connection_detail', pk=pk)


class MessageLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List message logs."""
    model = MessageLog
    template_name = 'instruments/message_list.html'
    context_object_name = 'messages'
    paginate_by = 50
    permission_required = 'instruments.view_messagelog'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('connection', 'connection__instrument')

        # Filter by connection
        connection_id = self.request.GET.get('connection')
        if connection_id:
            queryset = queryset.filter(connection_id=connection_id)

        # Filter by direction
        direction = self.request.GET.get('direction')
        if direction:
            queryset = queryset.filter(direction=direction)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by message type
        message_type = self.request.GET.get('type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(raw_message__icontains=search) |
                Q(related_sample_id__icontains=search) |
                Q(related_patient_id__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['connections'] = InstrumentConnection.objects.filter(is_active=True)
        context['directions'] = MessageLog.DIRECTION_CHOICES
        context['statuses'] = MessageLog.STATUS_CHOICES
        context['message_types'] = MessageLog.MESSAGE_TYPE_CHOICES
        return context


class MessageLogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """View message details."""
    model = MessageLog
    template_name = 'instruments/message_detail.html'
    context_object_name = 'message'
    permission_required = 'instruments.view_messagelog'


@login_required
@permission_required('instruments.change_messagelog')
@require_POST
def reprocess_message(request, pk):
    """Reprocess a message."""
    message = get_object_or_404(MessageLog, pk=pk)

    try:
        from .services.result_importer import ResultImporter
        importer = ResultImporter()
        result = importer.process_message(message)

        if result['success']:
            messages.success(request, 'Message reprocessed successfully.')
        else:
            messages.warning(request, f'Reprocessing failed: {result.get("error", "Unknown error")}')
    except Exception as e:
        messages.error(request, f'Error reprocessing message: {str(e)}')

    return redirect('instruments:message_detail', pk=pk)


class WorklistListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List worklist exports."""
    model = WorklistExport
    template_name = 'instruments/worklist_list.html'
    context_object_name = 'worklists'
    paginate_by = 25
    permission_required = 'instruments.view_worklistexport'

    def get_queryset(self):
        return super().get_queryset().select_related('connection', 'connection__instrument', 'created_by')


class WorklistDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """View worklist details."""
    model = WorklistExport
    template_name = 'instruments/worklist_detail.html'
    context_object_name = 'worklist'
    permission_required = 'instruments.view_worklistexport'


@login_required
@permission_required('instruments.add_worklistexport')
def create_worklist(request):
    """Create a new worklist for export."""
    if request.method == 'POST':
        connection_id = request.POST.get('connection')
        sample_ids = request.POST.getlist('samples')

        connection = get_object_or_404(InstrumentConnection, pk=connection_id)

        try:
            exporter = WorklistExporter()
            worklist = exporter.create_worklist(connection, sample_ids, request.user)
            messages.success(request, f'Worklist created with {len(sample_ids)} samples.')
            return redirect('instruments:worklist_detail', pk=worklist.pk)
        except Exception as e:
            messages.error(request, f'Error creating worklist: {str(e)}')

    context = {
        'connections': InstrumentConnection.objects.filter(is_active=True),
    }
    return render(request, 'instruments/worklist_create.html', context)


@login_required
@permission_required('instruments.change_worklistexport')
@require_POST
def send_worklist(request, pk):
    """Send a worklist to the instrument."""
    worklist = get_object_or_404(WorklistExport, pk=pk)

    try:
        exporter = WorklistExporter()
        result = exporter.send_worklist(worklist)

        if result['success']:
            messages.success(request, 'Worklist sent to instrument.')
        else:
            messages.warning(request, f'Failed to send worklist: {result.get("error", "Unknown error")}')
    except Exception as e:
        messages.error(request, f'Error sending worklist: {str(e)}')

    return redirect('instruments:worklist_detail', pk=pk)


class InstrumentDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Dashboard showing instrument status overview."""
    template_name = 'instruments/dashboard.html'
    permission_required = 'instruments.view_instrumentconnection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Connection status summary
        connections = InstrumentConnection.objects.filter(is_active=True)
        context['connections'] = connections
        context['connection_stats'] = {
            'total': connections.count(),
            'connected': connections.filter(connection_status='CONNECTED').count(),
            'disconnected': connections.filter(connection_status='DISCONNECTED').count(),
            'error': connections.filter(connection_status='ERROR').count(),
        }

        # Today's message stats
        today = timezone.now().date()
        today_messages = MessageLog.objects.filter(timestamp__date=today)
        context['today_stats'] = {
            'total': today_messages.count(),
            'inbound': today_messages.filter(direction='INBOUND').count(),
            'outbound': today_messages.filter(direction='OUTBOUND').count(),
            'errors': today_messages.filter(status='ERROR').count(),
        }

        # Recent errors
        context['recent_errors'] = MessageLog.objects.filter(
            status='ERROR'
        ).select_related('connection', 'connection__instrument')[:10]

        # Pending worklists
        context['pending_worklists'] = WorklistExport.objects.filter(
            status__in=['PENDING', 'SENT']
        ).select_related('connection', 'connection__instrument')[:10]

        return context


# API Views

@login_required
@require_GET
def api_connection_status(request):
    """API endpoint for connection status."""
    connections = InstrumentConnection.objects.filter(is_active=True)

    data = []
    for conn in connections:
        data.append({
            'id': conn.pk,
            'name': conn.name,
            'instrument': conn.instrument.name,
            'status': conn.connection_status,
            'last_connection': conn.last_connection.isoformat() if conn.last_connection else None,
            'last_message': conn.last_message.isoformat() if conn.last_message else None,
        })

    return JsonResponse({'connections': data})


@login_required
@permission_required('instruments.change_instrumentconnection')
@require_POST
def api_send_message(request):
    """API endpoint to send a message to an instrument."""
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        message = data.get('message')

        connection = get_object_or_404(InstrumentConnection, pk=connection_id)

        manager = ConnectionManager()
        result = manager.send_message(connection, message)

        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

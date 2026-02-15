# audit/views.py

"""
Views for the Audit app.

Provides views for viewing audit logs and activity history.
"""

from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog


class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List view for audit logs with filtering."""

    model = AuditLog
    template_name = 'audit/audit_log_list.html'
    context_object_name = 'audit_logs'
    paginate_by = 50
    permission_required = 'audit.view_auditlog'

    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = AuditLog.objects.select_related('user', 'content_type').order_by('-timestamp')

        # Filter by action
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action=action)

        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by content type
        content_type_id = self.request.GET.get('content_type')
        if content_type_id:
            queryset = queryset.filter(content_type_id=content_type_id)

        # Filter by date range
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(object_repr__icontains=search)

        return queryset

    def get_context_data(self, **kwargs):
        """Add filter options to context."""
        context = super().get_context_data(**kwargs)
        context['action_choices'] = AuditLog.ACTION_CHOICES
        context['content_types'] = ContentType.objects.filter(
            id__in=AuditLog.objects.values_list('content_type', flat=True).distinct()
        )
        context['users'] = AuditLog.objects.values_list(
            'user__id', 'user__username'
        ).distinct().exclude(user__isnull=True)
        return context


class AuditLogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Detail view for a single audit log entry."""

    model = AuditLog
    template_name = 'audit/audit_log_detail.html'
    context_object_name = 'audit_log'
    permission_required = 'audit.view_auditlog'

    def get_queryset(self):
        return AuditLog.objects.select_related('user', 'content_type')


def audit_trail_view(request, content_type, object_id):
    """View audit trail for a specific object."""
    from django.shortcuts import render

    ct = get_object_or_404(ContentType, model=content_type)
    logs = AuditLog.objects.filter(
        content_type=ct,
        object_id=object_id
    ).select_related('user').order_by('-timestamp')

    # Try to get the actual object
    try:
        obj = ct.get_object_for_this_type(pk=object_id)
    except ct.model_class().DoesNotExist:
        obj = None

    context = {
        'audit_logs': logs,
        'content_type': ct,
        'object_id': object_id,
        'object': obj,
    }
    return render(request, 'audit/audit_trail.html', context)


class AuditDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Dashboard view showing audit statistics."""

    template_name = 'audit/audit_dashboard.html'
    permission_required = 'audit.view_auditlog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Recent activity
        context['recent_logs'] = AuditLog.objects.select_related(
            'user', 'content_type'
        ).order_by('-timestamp')[:20]

        # Activity by action
        context['activity_by_action'] = AuditLog.objects.values('action').annotate(
            count=Count('id')
        ).order_by('-count')

        # Activity by user (top 10)
        context['activity_by_user'] = AuditLog.objects.exclude(
            user__isnull=True
        ).values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Activity by day (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['daily_activity'] = AuditLog.objects.filter(
            timestamp__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Most modified models
        context['most_modified'] = AuditLog.objects.values(
            'content_type__model'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return context


def api_recent_activity(request):
    """API endpoint for recent audit activity."""
    limit = int(request.GET.get('limit', 10))
    logs = AuditLog.objects.select_related('user', 'content_type').order_by('-timestamp')[:limit]

    data = [{
        'id': log.id,
        'action': log.action,
        'action_display': log.get_action_display(),
        'user': log.user.username if log.user else 'System',
        'content_type': str(log.content_type),
        'object_repr': log.object_repr,
        'timestamp': log.timestamp.isoformat(),
    } for log in logs]

    return JsonResponse({'logs': data})


def api_audit_stats(request):
    """API endpoint for audit statistics."""
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    stats = {
        'total': AuditLog.objects.filter(timestamp__gte=since).count(),
        'by_action': list(
            AuditLog.objects.filter(timestamp__gte=since).values('action').annotate(
                count=Count('id')
            )
        ),
        'by_user': list(
            AuditLog.objects.filter(timestamp__gte=since).exclude(
                user__isnull=True
            ).values('user__username').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        ),
    }

    return JsonResponse(stats)

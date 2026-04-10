"""
API Views for equipment app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from equipment.models import Instrument, InstrumentType, MaintenanceRecord
from api.serializers import (
    InstrumentTypeSerializer,
    InstrumentSerializer, InstrumentListSerializer, InstrumentCreateSerializer,
    MaintenanceRecordSerializer, MaintenanceRecordListSerializer, MaintenanceRecordCreateSerializer,
    InstrumentMaintenanceHistorySerializer,
)
from api.filters import InstrumentFilter, MaintenanceRecordFilter
from api.pagination import StandardResultsSetPagination


class InstrumentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for InstrumentType model."""
    queryset = InstrumentType.objects.all().order_by('name')
    serializer_class = InstrumentTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'manufacturer']
    ordering_fields = ['name', 'manufacturer']


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Instrument model.

    Additional endpoints:
    - maintenance_history: GET /api/instruments/{id}/maintenance-history/
    - set_status: POST /api/instruments/{id}/set-status/
    - schedule_maintenance: POST /api/instruments/{id}/schedule-maintenance/
    """
    queryset = Instrument.objects.all().select_related('instrument_type').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InstrumentFilter
    search_fields = ['name', 'serial_number', 'asset_number', 'location']
    ordering_fields = ['name', 'status', 'next_maintenance', 'next_calibration']

    def get_serializer_class(self):
        if self.action == 'list':
            return InstrumentListSerializer
        if self.action == 'create':
            return InstrumentCreateSerializer
        if self.action == 'maintenance_history':
            return InstrumentMaintenanceHistorySerializer
        return InstrumentSerializer

    @action(detail=True, methods=['get'], url_path='maintenance-history')
    def maintenance_history(self, request, pk=None):
        """Get maintenance history for an instrument."""
        instrument = self.get_object()
        serializer = InstrumentMaintenanceHistorySerializer(instrument, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='set-status')
    def set_status(self, request, pk=None):
        """Set instrument status."""
        instrument = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Instrument.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instrument.status = new_status
        instrument.save()
        return Response(InstrumentSerializer(instrument, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='schedule-maintenance')
    def schedule_maintenance(self, request, pk=None):
        """Schedule a maintenance for an instrument."""
        instrument = self.get_object()

        maintenance_type = request.data.get('maintenance_type', 'PREVENTIVE')
        scheduled_date = request.data.get('scheduled_date')
        description = request.data.get('description', '')

        if not scheduled_date:
            return Response(
                {'error': 'scheduled_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record = MaintenanceRecord.objects.create(
            instrument=instrument,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            description=description,
            status='SCHEDULED'
        )

        return Response(
            MaintenanceRecordSerializer(record, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='maintenance-due')
    def maintenance_due(self, request):
        """Get instruments with maintenance due."""
        instruments = self.get_queryset().filter(
            next_maintenance__lte=timezone.now().date()
        )
        serializer = InstrumentListSerializer(instruments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='calibration-due')
    def calibration_due(self, request):
        """Get instruments with calibration due."""
        instruments = self.get_queryset().filter(
            next_calibration__lte=timezone.now().date()
        )
        serializer = InstrumentListSerializer(instruments, many=True, context={'request': request})
        return Response(serializer.data)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MaintenanceRecord model.

    Additional endpoints:
    - complete: POST /api/maintenance-records/{id}/complete/
    - cancel: POST /api/maintenance-records/{id}/cancel/
    """
    queryset = MaintenanceRecord.objects.all().select_related('instrument').order_by('-scheduled_date')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MaintenanceRecordFilter
    search_fields = ['instrument__name', 'description', 'service_provider']
    ordering_fields = ['scheduled_date', 'completed_at', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return MaintenanceRecordListSerializer
        if self.action == 'create':
            return MaintenanceRecordCreateSerializer
        return MaintenanceRecordSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a maintenance record."""
        record = self.get_object()

        if record.status == 'COMPLETED':
            return Response(
                {'error': 'Maintenance already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.status = 'COMPLETED'
        record.completed_at = timezone.now()
        record.performed_by_user = request.user
        if not record.performed_by:
            record.performed_by = request.user.get_full_name() or request.user.username

        # Update optional fields from request
        if 'parts_replaced' in request.data:
            record.parts_replaced = request.data['parts_replaced']
        if 'cost' in request.data:
            record.cost = request.data['cost']
        if 'notes' in request.data:
            record.notes = request.data['notes']

        record.save()
        return Response(MaintenanceRecordSerializer(record, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a maintenance record."""
        record = self.get_object()

        if record.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {'error': f'Cannot cancel maintenance with status {record.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.status = 'CANCELLED'
        record.notes = request.data.get('notes', record.notes)
        record.save()
        return Response(MaintenanceRecordSerializer(record, context={'request': request}).data)

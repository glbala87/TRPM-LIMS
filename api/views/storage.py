"""
API Views for storage app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

from storage.models import StorageUnit, StorageRack, StoragePosition, StorageLog
from molecular_diagnostics.models import MolecularSample
from api.serializers import (
    StorageUnitSerializer, StorageUnitListSerializer, StorageUnitCreateSerializer,
    StorageRackSerializer, StorageRackListSerializer, StorageRackCreateSerializer,
    StoragePositionSerializer, StoragePositionListSerializer,
    StorageLogSerializer, StorageLogListSerializer,
    StoreSampleSerializer, MoveSampleSerializer, RetrieveSampleSerializer,
)
from api.filters import StorageUnitFilter, StoragePositionFilter, StorageLogFilter
from api.pagination import StandardResultsSetPagination


class StorageUnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StorageUnit model.

    Additional endpoints:
    - available_positions: GET /api/storage-units/{id}/available-positions/
    - temperature_log: GET /api/storage-units/{id}/temperature-log/
    """
    queryset = StorageUnit.objects.all().prefetch_related('racks').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StorageUnitFilter
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'unit_type', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return StorageUnitListSerializer
        if self.action == 'create':
            return StorageUnitCreateSerializer
        return StorageUnitSerializer

    @action(detail=True, methods=['get'], url_path='available-positions')
    def available_positions(self, request, pk=None):
        """Get all available positions in a storage unit."""
        unit = self.get_object()
        positions = StoragePosition.objects.filter(
            rack__storage_unit=unit,
            is_occupied=False,
            is_reserved=False
        ).select_related('rack')
        serializer = StoragePositionSerializer(positions, many=True, context={'request': request})
        return Response(serializer.data)


class StorageRackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StorageRack model.

    Additional endpoints:
    - positions: GET /api/storage-racks/{id}/positions/
    - next_available: GET /api/storage-racks/{id}/next-available/
    """
    queryset = StorageRack.objects.all().select_related('storage_unit').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'storage_unit__name']
    ordering_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return StorageRackListSerializer
        if self.action == 'create':
            return StorageRackCreateSerializer
        return StorageRackSerializer

    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """Get all positions in a rack."""
        rack = self.get_object()
        positions = rack.positions.all().order_by('row', 'column')
        serializer = StoragePositionSerializer(positions, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='next-available')
    def next_available(self, request, pk=None):
        """Get the next available position in a rack."""
        rack = self.get_object()
        position = rack.get_available_position()
        if position:
            return Response(StoragePositionSerializer(position, context={'request': request}).data)
        return Response({'message': 'No available positions'}, status=status.HTTP_404_NOT_FOUND)


class StoragePositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StoragePosition model.

    Additional endpoints:
    - store: POST /api/storage-positions/{id}/store/
    - retrieve_sample: POST /api/storage-positions/{id}/retrieve/
    - move: POST /api/storage-positions/{id}/move/
    - reserve: POST /api/storage-positions/{id}/reserve/
    - release: POST /api/storage-positions/{id}/release/
    """
    queryset = StoragePosition.objects.all().select_related('rack', 'rack__storage_unit').order_by('id')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StoragePositionFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return StoragePositionListSerializer
        if self.action == 'store':
            return StoreSampleSerializer
        if self.action == 'move':
            return MoveSampleSerializer
        if self.action == 'retrieve_sample':
            return RetrieveSampleSerializer
        return StoragePositionSerializer

    @action(detail=True, methods=['post'])
    def store(self, request, pk=None):
        """Store a sample in this position."""
        position = self.get_object()
        serializer = StoreSampleSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sample = get_object_or_404(MolecularSample, pk=serializer.validated_data['sample_id'])
        reason = serializer.validated_data.get('reason', '')

        try:
            position.store_sample(sample, request.user, reason)
            return Response({
                'success': True,
                'message': f'Sample {sample.sample_id} stored at {position.full_location}',
                'position': StoragePositionSerializer(position, context={'request': request}).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='retrieve')
    def retrieve_sample(self, request, pk=None):
        """Retrieve sample from this position."""
        position = self.get_object()
        serializer = RetrieveSampleSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reason = serializer.validated_data.get('reason', '')

        try:
            sample = position.remove_sample(request.user, reason)
            return Response({
                'success': True,
                'message': f'Sample {sample.sample_id} retrieved from {position.full_location}',
                'sample_id': sample.sample_id
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move sample from this position to another."""
        from_position = self.get_object()
        serializer = MoveSampleSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        to_position = get_object_or_404(StoragePosition, pk=serializer.validated_data['to_position_id'])
        reason = serializer.validated_data.get('reason', '')

        if not from_position.is_occupied:
            return Response({'error': 'No sample in this position'}, status=status.HTTP_400_BAD_REQUEST)

        if to_position.is_occupied:
            return Response({'error': 'Destination position is occupied'}, status=status.HTTP_400_BAD_REQUEST)

        sample = from_position.sample

        # Remove from current position
        from_position.remove_sample(request.user, f'Moving to {to_position.full_location}. {reason}')

        # Store in new position
        to_position.store_sample(sample, request.user, f'Moved from {from_position.full_location}. {reason}')

        # Log the move
        StorageLog.objects.create(
            sample=sample,
            action='MOVE',
            from_position=from_position,
            to_position=to_position,
            user=request.user,
            reason=reason
        )

        return Response({
            'success': True,
            'message': f'Sample {sample.sample_id} moved to {to_position.full_location}',
            'new_position': StoragePositionSerializer(to_position, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve this position."""
        position = self.get_object()

        try:
            position.reserve(request.user)
            return Response({
                'success': True,
                'message': f'Position {position.full_location} reserved',
                'position': StoragePositionSerializer(position, context={'request': request}).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release reservation on this position."""
        position = self.get_object()

        if not position.is_reserved:
            return Response({'error': 'Position is not reserved'}, status=status.HTTP_400_BAD_REQUEST)

        position.is_reserved = False
        position.save()

        return Response({
            'success': True,
            'message': f'Position {position.full_location} released',
            'position': StoragePositionSerializer(position, context={'request': request}).data
        })


class StorageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for StorageLog model (read-only)."""
    queryset = StorageLog.objects.all().select_related(
        'sample', 'from_position', 'to_position', 'user'
    ).order_by('-timestamp')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StorageLogFilter
    ordering_fields = ['timestamp', 'action']

    def get_serializer_class(self):
        if self.action == 'list':
            return StorageLogListSerializer
        return StorageLogSerializer

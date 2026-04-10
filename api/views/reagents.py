"""
API Views for reagents app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from reagents.models import Reagent, ReagentCategory, ReagentUsage, MolecularReagent
from api.serializers import (
    ReagentCategorySerializer,
    ReagentSerializer, ReagentListSerializer, ReagentCreateSerializer,
    ReagentUsageSerializer,
    MolecularReagentSerializer, MolecularReagentListSerializer, MolecularReagentCreateSerializer,
    ReagentInventorySerializer,
)
from api.filters import ReagentFilter, MolecularReagentFilter
from api.pagination import StandardResultsSetPagination


class ReagentCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for ReagentCategory model."""
    queryset = ReagentCategory.objects.all().order_by('name')
    serializer_class = ReagentCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class ReagentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reagent model.

    Additional endpoints:
    - inventory_summary: GET /api/reagents/inventory-summary/
    - low_stock: GET /api/reagents/low-stock/
    - expiring_soon: GET /api/reagents/expiring-soon/
    - use: POST /api/reagents/{id}/use/
    - restock: POST /api/reagents/{id}/restock/
    """
    queryset = Reagent.objects.all().order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReagentFilter
    search_fields = ['name', 'vendor', 'lot_number']
    ordering_fields = ['name', 'expiration_date', 'quantity_in_stock']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReagentListSerializer
        if self.action == 'create':
            return ReagentCreateSerializer
        return ReagentSerializer

    @action(detail=False, methods=['get'], url_path='inventory-summary')
    def inventory_summary(self, request):
        """Get reagent inventory summary."""
        today = timezone.now().date()
        expiring_threshold = today + timedelta(days=30)

        summary = {
            'total_reagents': Reagent.objects.count(),
            'low_stock_count': Reagent.objects.filter(quantity_in_stock__lt=10).count(),
            'expired_count': Reagent.objects.filter(expiration_date__lt=today).count(),
            'expiring_soon_count': Reagent.objects.filter(
                expiration_date__gte=today,
                expiration_date__lte=expiring_threshold
            ).count(),
            'on_order_count': Reagent.objects.filter(on_order=True).count(),
        }

        serializer = ReagentInventorySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Get reagents with low stock."""
        reagents = self.get_queryset().filter(quantity_in_stock__lt=10)
        serializer = ReagentListSerializer(reagents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='expiring-soon')
    def expiring_soon(self, request):
        """Get reagents expiring within 30 days."""
        today = timezone.now().date()
        expiring_threshold = today + timedelta(days=30)

        reagents = self.get_queryset().filter(
            expiration_date__gte=today,
            expiration_date__lte=expiring_threshold
        ).order_by('expiration_date')

        serializer = ReagentListSerializer(reagents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Record reagent usage."""
        reagent = self.get_object()
        quantity = request.data.get('quantity', 1)
        lab_order_id = request.data.get('lab_order_id')

        if reagent.quantity_in_stock < quantity:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reagent.quantity_in_stock -= quantity
        reagent.save()

        # Record usage
        if lab_order_id:
            from lab_management.models import LabOrder
            lab_order = LabOrder.objects.filter(pk=lab_order_id).first()
            if lab_order:
                ReagentUsage.objects.create(
                    reagent=reagent,
                    used_in_lab_order=lab_order,
                    quantity_used=quantity
                )

        return Response(ReagentSerializer(reagent, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        """Restock a reagent."""
        reagent = self.get_object()
        quantity = request.data.get('quantity', 0)
        new_lot_number = request.data.get('lot_number')
        new_expiration = request.data.get('expiration_date')

        reagent.quantity_in_stock += quantity

        if new_lot_number:
            reagent.lot_number = new_lot_number
        if new_expiration:
            reagent.expiration_date = new_expiration

        reagent.on_order = False
        reagent.save()

        return Response(ReagentSerializer(reagent, context={'request': request}).data)


class ReagentUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ReagentUsage model (read-only)."""
    queryset = ReagentUsage.objects.all().select_related('reagent', 'lab_order').order_by('-usage_date')
    serializer_class = ReagentUsageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['usage_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        reagent_id = self.request.query_params.get('reagent', None)
        if reagent_id:
            queryset = queryset.filter(reagent_id=reagent_id)
        return queryset


class MolecularReagentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MolecularReagent model.

    Additional endpoints:
    - expired: GET /api/molecular-reagents/expired/
    - low_stock: GET /api/molecular-reagents/low-stock/
    - validate: POST /api/molecular-reagents/{id}/validate/
    - use_volume: POST /api/molecular-reagents/{id}/use-volume/
    """
    queryset = MolecularReagent.objects.all().prefetch_related(
        'linked_test_panels', 'linked_gene_targets'
    ).order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MolecularReagentFilter
    search_fields = ['name', 'catalog_number', 'lot_number', 'manufacturer', 'supplier']
    ordering_fields = ['name', 'expiration_date', 'current_volume_ul']

    def get_serializer_class(self):
        if self.action == 'list':
            return MolecularReagentListSerializer
        if self.action == 'create':
            return MolecularReagentCreateSerializer
        return MolecularReagentSerializer

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired molecular reagents."""
        today = timezone.now().date()
        reagents = self.get_queryset().filter(expiration_date__lt=today)
        serializer = MolecularReagentListSerializer(reagents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Get molecular reagents with low stock (less than 10% of initial volume)."""
        from django.db.models import F
        reagents = self.get_queryset().filter(
            current_volume_ul__lt=F('initial_volume_ul') * 0.1
        )
        serializer = MolecularReagentListSerializer(reagents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Mark reagent as validated."""
        reagent = self.get_object()
        reagent.is_validated = True
        reagent.validation_date = timezone.now().date()
        # MolecularReagent has no `validated_by` field; record the validator in
        # validation_notes instead to keep the audit trail.
        existing = reagent.validation_notes or ''
        stamp = f"Validated by {request.user.get_username()} on {reagent.validation_date}"
        reagent.validation_notes = (existing + '\n' + stamp).strip() if existing else stamp
        reagent.save()
        return Response(MolecularReagentSerializer(reagent, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='use-volume')
    def use_volume(self, request, pk=None):
        """Record volume usage for a molecular reagent."""
        reagent = self.get_object()
        volume_used = request.data.get('volume_ul', 0)

        if reagent.current_volume_ul < volume_used:
            return Response(
                {'error': 'Insufficient volume'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reagent.current_volume_ul -= volume_used

        # Mark as opened if not already
        if not reagent.opened_date:
            reagent.opened_date = timezone.now().date()

        reagent.save()
        return Response(MolecularReagentSerializer(reagent, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def open(self, request, pk=None):
        """Mark reagent as opened (starts stability countdown)."""
        reagent = self.get_object()

        if reagent.opened_date:
            return Response(
                {'error': 'Reagent already opened'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reagent.opened_date = timezone.now().date()
        reagent.save()
        return Response(MolecularReagentSerializer(reagent, context={'request': request}).data)

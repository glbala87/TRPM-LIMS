"""
API Views for lab_management app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from lab_management.models import Patient, LabOrder, TestResult
from api.serializers import (
    PatientSerializer, PatientListSerializer, PatientCreateSerializer,
    LabOrderSerializer, LabOrderListSerializer, LabOrderCreateSerializer,
    TestResultSerializer,
)
from api.filters import PatientFilter, LabOrderFilter
from api.pagination import StandardResultsSetPagination


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient model.

    Provides CRUD operations and additional endpoints:
    - list: GET /api/patients/
    - create: POST /api/patients/
    - retrieve: GET /api/patients/{id}/
    - update: PUT /api/patients/{id}/
    - partial_update: PATCH /api/patients/{id}/
    - destroy: DELETE /api/patients/{id}/
    - orders: GET /api/patients/{id}/orders/
    """
    queryset = Patient.objects.all().order_by('-date_added')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'OP_NO', 'passport_no']
    ordering_fields = ['date_added', 'first_name', 'last_name', 'OP_NO']
    ordering = ['-date_added']

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        if self.action == 'create':
            return PatientCreateSerializer
        return PatientSerializer

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get all lab orders for a patient."""
        patient = self.get_object()
        orders = LabOrder.objects.filter(patient=patient).order_by('-date')
        serializer = LabOrderListSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)


class LabOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LabOrder model.

    Provides CRUD operations and additional endpoints:
    - list: GET /api/lab-orders/
    - create: POST /api/lab-orders/
    - retrieve: GET /api/lab-orders/{id}/
    - update: PUT /api/lab-orders/{id}/
    - partial_update: PATCH /api/lab-orders/{id}/
    - destroy: DELETE /api/lab-orders/{id}/
    - mark_collected: POST /api/lab-orders/{id}/mark-collected/
    - mark_insufficient: POST /api/lab-orders/{id}/mark-insufficient/
    """
    queryset = LabOrder.objects.all().select_related('patient').order_by('-date')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LabOrderFilter
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__OP_NO', 'test_name']
    ordering_fields = ['date', 'test_type']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return LabOrderListSerializer
        if self.action == 'create':
            return LabOrderCreateSerializer
        return LabOrderSerializer

    @action(detail=True, methods=['post'], url_path='mark-collected')
    def mark_collected(self, request, pk=None):
        """Mark sample as collected for a lab order."""
        order = self.get_object()
        order.sample_collected = True
        order.sample_insufficient = False
        order.save()
        serializer = LabOrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-insufficient')
    def mark_insufficient(self, request, pk=None):
        """Mark sample as insufficient for a lab order."""
        order = self.get_object()
        order.sample_insufficient = True
        order.save()
        serializer = LabOrderSerializer(order, context={'request': request})
        return Response(serializer.data)


class TestResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TestResult model.

    Provides CRUD operations for test results.
    """
    queryset = TestResult.objects.all().select_related('lab_order').order_by('-id')
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'lab_order__date']
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_order_id = self.request.query_params.get('lab_order', None)
        if lab_order_id:
            queryset = queryset.filter(lab_order_id=lab_order_id)
        return queryset

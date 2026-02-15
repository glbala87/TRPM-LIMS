"""
API Views for molecular_diagnostics app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from molecular_diagnostics.models import (
    MolecularSample, MolecularSampleType, MolecularTestPanel, GeneTarget,
    MolecularResult, PCRResult, SequencingResult, VariantCall,
    PCRPlate, PlateWell, InstrumentRun, NGSLibrary, NGSPool,
    QCMetricDefinition, ControlSample, QCRecord,
    WorkflowDefinition, WorkflowStep, SampleHistory
)
from molecular_diagnostics.services.workflow_engine import WorkflowEngine
from api.serializers import (
    MolecularSampleTypeSerializer,
    GeneTargetSerializer, GeneTargetListSerializer,
    MolecularTestPanelSerializer, MolecularTestPanelListSerializer,
    MolecularSampleSerializer, MolecularSampleListSerializer, MolecularSampleCreateSerializer,
    SampleTransitionSerializer,
    WorkflowStepSerializer, WorkflowDefinitionSerializer, SampleHistorySerializer,
    InstrumentRunSerializer, InstrumentRunListSerializer,
    PCRPlateSerializer, PCRPlateListSerializer, PlateWellSerializer,
    NGSLibrarySerializer, NGSPoolSerializer,
    MolecularResultSerializer, MolecularResultListSerializer,
    PCRResultSerializer, SequencingResultSerializer, VariantCallSerializer,
    QCMetricDefinitionSerializer, ControlSampleSerializer, QCRecordSerializer,
)
from api.filters import (
    MolecularSampleFilter, MolecularTestPanelFilter, GeneTargetFilter,
    MolecularResultFilter, VariantCallFilter, PCRPlateFilter,
    InstrumentRunFilter, QCRecordFilter
)
from api.pagination import StandardResultsSetPagination, SampleListPagination


class MolecularSampleTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for MolecularSampleType model."""
    queryset = MolecularSampleType.objects.all().order_by('name')
    serializer_class = MolecularSampleTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


class GeneTargetViewSet(viewsets.ModelViewSet):
    """ViewSet for GeneTarget model."""
    queryset = GeneTarget.objects.all().order_by('symbol')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GeneTargetFilter
    search_fields = ['symbol', 'name', 'chromosome']
    ordering_fields = ['symbol', 'chromosome']

    def get_serializer_class(self):
        if self.action == 'list':
            return GeneTargetListSerializer
        return GeneTargetSerializer


class MolecularTestPanelViewSet(viewsets.ModelViewSet):
    """ViewSet for MolecularTestPanel model."""
    queryset = MolecularTestPanel.objects.all().prefetch_related('gene_targets').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MolecularTestPanelFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'test_type']

    def get_serializer_class(self):
        if self.action == 'list':
            return MolecularTestPanelListSerializer
        return MolecularTestPanelSerializer


class MolecularSampleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MolecularSample model.

    Additional endpoints:
    - transition: POST /api/molecular-samples/{id}/transition/
    - history: GET /api/molecular-samples/{id}/history/
    - available_transitions: GET /api/molecular-samples/{id}/available-transitions/
    """
    queryset = MolecularSample.objects.all().select_related(
        'sample_type', 'lab_order', 'storage_location'
    ).order_by('-received_datetime')
    permission_classes = [IsAuthenticated]
    pagination_class = SampleListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MolecularSampleFilter
    search_fields = ['sample_id', 'lab_order__patient__first_name', 'lab_order__patient__last_name']
    ordering_fields = ['sample_id', 'received_datetime', 'workflow_status', 'priority']

    def get_serializer_class(self):
        if self.action == 'list':
            return MolecularSampleListSerializer
        if self.action == 'create':
            return MolecularSampleCreateSerializer
        if self.action == 'transition':
            return SampleTransitionSerializer
        return MolecularSampleSerializer

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition sample to a new workflow status."""
        sample = self.get_object()
        serializer = SampleTransitionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        engine = WorkflowEngine()
        new_status = serializer.validated_data['new_status']
        notes = serializer.validated_data.get('notes', '')
        qc_passed = serializer.validated_data.get('qc_passed')
        qc_notes = serializer.validated_data.get('qc_notes', '')

        success, message = engine.transition(
            sample=sample,
            new_status=new_status,
            user=request.user,
            notes=notes,
            qc_passed=qc_passed,
            qc_notes=qc_notes
        )

        if success:
            sample.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'sample': MolecularSampleSerializer(sample, context={'request': request}).data
            })
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get workflow history for a sample."""
        sample = self.get_object()
        history = SampleHistory.objects.filter(sample=sample).order_by('-timestamp')
        serializer = SampleHistorySerializer(history, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='available-transitions')
    def available_transitions(self, request, pk=None):
        """Get available workflow transitions for a sample."""
        sample = self.get_object()
        engine = WorkflowEngine()
        transitions = engine.get_available_transitions(sample)
        return Response({
            'current_status': sample.status,
            'current_status_display': sample.get_status_display(),
            'available_transitions': [
                {'value': t, 'display': dict(MolecularSample.WORKFLOW_STATUS_CHOICES).get(t, t)}
                for t in transitions
            ]
        })


class WorkflowDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkflowDefinition model."""
    queryset = WorkflowDefinition.objects.all().prefetch_related('steps').order_by('name')
    serializer_class = WorkflowDefinitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class InstrumentRunViewSet(viewsets.ModelViewSet):
    """ViewSet for InstrumentRun model."""
    queryset = InstrumentRun.objects.all().select_related('instrument').order_by('-start_time')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InstrumentRunFilter
    search_fields = ['run_id', 'protocol_name']
    ordering_fields = ['run_id', 'start_time', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return InstrumentRunListSerializer
        return InstrumentRunSerializer

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an instrument run."""
        run = self.get_object()
        if run.status != 'PLANNED':
            return Response(
                {'error': 'Run must be in PLANNED status to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.utils import timezone
        run.status = 'IN_PROGRESS'
        run.start_time = timezone.now()
        run.operator = request.user
        run.save()
        return Response(InstrumentRunSerializer(run, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete an instrument run."""
        run = self.get_object()
        if run.status != 'IN_PROGRESS':
            return Response(
                {'error': 'Run must be in IN_PROGRESS status to complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.utils import timezone
        run.status = 'COMPLETED'
        run.end_time = timezone.now()
        run.save()
        return Response(InstrumentRunSerializer(run, context={'request': request}).data)


class PCRPlateViewSet(viewsets.ModelViewSet):
    """ViewSet for PCRPlate model."""
    queryset = PCRPlate.objects.all().select_related('instrument_run').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PCRPlateFilter
    search_fields = ['barcode']
    ordering_fields = ['barcode', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PCRPlateListSerializer
        return PCRPlateSerializer

    @action(detail=True, methods=['get'])
    def layout(self, request, pk=None):
        """Get plate layout visualization data."""
        plate = self.get_object()
        return Response(plate.get_layout())


class NGSLibraryViewSet(viewsets.ModelViewSet):
    """ViewSet for NGSLibrary model."""
    queryset = NGSLibrary.objects.all().select_related('sample', 'prep_kit').order_by('-prep_date')
    serializer_class = NGSLibrarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['library_id', 'sample__sample_id']
    ordering_fields = ['library_id', 'prep_date']


class NGSPoolViewSet(viewsets.ModelViewSet):
    """ViewSet for NGSPool model."""
    queryset = NGSPool.objects.all().prefetch_related('libraries').order_by('-pool_date')
    serializer_class = NGSPoolSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['pool_id']
    ordering_fields = ['pool_id', 'pool_date']


class MolecularResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MolecularResult model.

    Additional endpoints:
    - approve: POST /api/molecular-results/{id}/approve/
    - review: POST /api/molecular-results/{id}/review/
    """
    queryset = MolecularResult.objects.all().select_related(
        'sample', 'test_panel'
    ).order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MolecularResultFilter
    search_fields = ['sample__sample_id', 'test_panel__name']
    ordering_fields = ['created_at', 'performed_at', 'approved_at', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return MolecularResultListSerializer
        return MolecularResultSerializer

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Mark result as reviewed."""
        result = self.get_object()
        from django.utils import timezone
        result.reviewed_by = request.user
        result.reviewed_at = timezone.now()
        if result.status == 'PENDING':
            result.status = 'PRELIMINARY'
        result.save()
        return Response(MolecularResultSerializer(result, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve and finalize result."""
        result = self.get_object()
        from django.utils import timezone
        result.approved_by = request.user
        result.approved_at = timezone.now()
        result.status = 'FINAL'
        result.save()
        return Response(MolecularResultSerializer(result, context={'request': request}).data)


class VariantCallViewSet(viewsets.ModelViewSet):
    """ViewSet for VariantCall model."""
    queryset = VariantCall.objects.all().select_related('result', 'gene_target').order_by('-id')
    serializer_class = VariantCallSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VariantCallFilter
    search_fields = ['hgvs_cdna', 'hgvs_protein', 'gene_target__symbol', 'dbsnp_id']
    ordering_fields = ['chromosome', 'position', 'classification']


class QCMetricDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for QCMetricDefinition model."""
    queryset = QCMetricDefinition.objects.all().order_by('name')
    serializer_class = QCMetricDefinitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code']


class ControlSampleViewSet(viewsets.ModelViewSet):
    """ViewSet for ControlSample model."""
    queryset = ControlSample.objects.all().select_related('gene_target', 'test_panel').order_by('name')
    serializer_class = ControlSampleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'lot_number']
    ordering_fields = ['name', 'expiration_date']


class QCRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for QCRecord model."""
    queryset = QCRecord.objects.all().select_related(
        'instrument_run', 'plate', 'metric', 'control_sample'
    ).order_by('-recorded_at')
    serializer_class = QCRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = QCRecordFilter
    ordering_fields = ['recorded_at', 'status']

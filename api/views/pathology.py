# api/views/pathology.py
"""
API Views for pathology module.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from pathology.models import (
    PathologyType, InflammationType, TumorSite, TumorMorphology,
    SpecimenType, StainingProtocol,
    Histology, HistologyBlock, HistologySlide,
    Pathology, PathologyAddendum,
)
from pathology.services import TNMStagingService, PathologyReportService
from api.serializers import (
    PathologyTypeSerializer, InflammationTypeSerializer, TumorSiteSerializer, TumorMorphologySerializer,
    SpecimenTypeSerializer, StainingProtocolSerializer,
    HistologySerializer, HistologyListSerializer, HistologyCreateSerializer,
    HistologyBlockSerializer, HistologySlideSerializer,
    PathologySerializer, PathologyListSerializer, PathologyCreateSerializer, PathologyUpdateSerializer,
    PathologyAddendumSerializer,
    SignReportSerializer, AmendReportSerializer, AddAddendumSerializer, CalculateStageSerializer, StagingSummarySerializer,
)
from api.pagination import StandardResultsSetPagination


# Reference ViewSets
class PathologyTypeViewSet(viewsets.ModelViewSet):
    queryset = PathologyType.objects.all().order_by('name')
    serializer_class = PathologyTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class InflammationTypeViewSet(viewsets.ModelViewSet):
    queryset = InflammationType.objects.all().order_by('name')
    serializer_class = InflammationTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class TumorSiteViewSet(viewsets.ModelViewSet):
    queryset = TumorSite.objects.all().select_related('parent').order_by('code')
    serializer_class = TumorSiteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['body_system', 'parent', 'is_active']
    search_fields = ['code', 'name']


class TumorMorphologyViewSet(viewsets.ModelViewSet):
    queryset = TumorMorphology.objects.all().order_by('code')
    serializer_class = TumorMorphologySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['behavior', 'is_active']
    search_fields = ['code', 'name']


class SpecimenTypeViewSet(viewsets.ModelViewSet):
    queryset = SpecimenType.objects.all().order_by('name')
    serializer_class = SpecimenTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class StainingProtocolViewSet(viewsets.ModelViewSet):
    queryset = StainingProtocol.objects.all().order_by('name')
    serializer_class = StainingProtocolSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['stain_type', 'is_active']
    search_fields = ['code', 'name', 'antibody']


# Histology ViewSets
class HistologyViewSet(viewsets.ModelViewSet):
    queryset = Histology.objects.all().select_related(
        'laboratory', 'lab_order', 'specimen_type', 'specimen_site'
    ).prefetch_related('blocks').order_by('-received_datetime')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['laboratory', 'status', 'specimen_type', 'fixation_type', 'is_stat', 'is_active']
    search_fields = ['histology_id', 'surgical_number', 'accession_number']
    ordering_fields = ['histology_id', 'received_datetime', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return HistologyListSerializer
        if self.action == 'create':
            return HistologyCreateSerializer
        return HistologySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition histology to a new status."""
        histology = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Histology.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        histology.status = new_status
        histology.save()

        return Response({
            'success': True,
            'histology': HistologySerializer(histology, context={'request': request}).data,
        })

    @action(detail=True, methods=['post'])
    def add_block(self, request, pk=None):
        """Add a block to histology specimen."""
        histology = self.get_object()
        serializer = HistologyBlockSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        block = serializer.save(histology=histology)
        histology.block_count = histology.blocks.count()
        histology.save()

        return Response(HistologyBlockSerializer(block).data, status=status.HTTP_201_CREATED)


class HistologyBlockViewSet(viewsets.ModelViewSet):
    queryset = HistologyBlock.objects.all().select_related('histology').prefetch_related('slides').order_by('histology', 'block_id')
    serializer_class = HistologyBlockSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['histology', 'is_decalcified']
    search_fields = ['block_id', 'barcode', 'histology__histology_id']


class HistologySlideViewSet(viewsets.ModelViewSet):
    queryset = HistologySlide.objects.all().select_related('block', 'stain').order_by('block', 'slide_number')
    serializer_class = HistologySlideSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['block', 'stain', 'quality', 'is_scanned', 'requires_recut']
    search_fields = ['barcode', 'block__histology__histology_id']

    def perform_create(self, serializer):
        slide = serializer.save(stained_by=self.request.user)
        # Update slide count on histology
        histology = slide.block.histology
        histology.slide_count = sum(block.slides.count() for block in histology.blocks.all())
        histology.save()


# Pathology ViewSets
class PathologyViewSet(viewsets.ModelViewSet):
    queryset = Pathology.objects.all().select_related(
        'laboratory', 'patient', 'histology', 'pathology_type',
        'tumor_site', 'tumor_morphology', 'pathologist'
    ).prefetch_related('addenda').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['laboratory', 'status', 'pathology_type', 'stage_group', 'grade', 'pathologist']
    search_fields = ['pathology_id', 'patient__first_name', 'patient__last_name', 'diagnosis']
    ordering_fields = ['pathology_id', 'created_at', 'signed_date', 'stage_group']

    def get_serializer_class(self):
        if self.action == 'list':
            return PathologyListSerializer
        if self.action == 'create':
            return PathologyCreateSerializer
        if self.action in ('update', 'partial_update'):
            return PathologyUpdateSerializer
        return PathologySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign and finalize pathology report."""
        pathology = self.get_object()
        serializer = SignReportSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = PathologyReportService(pathology)
        success, message = service.sign_report(
            pathologist=request.user,
            is_preliminary=serializer.validated_data.get('is_preliminary', False),
        )

        if success:
            pathology.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'pathology': PathologySerializer(pathology, context={'request': request}).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def amend(self, request, pk=None):
        """Amend a finalized report."""
        pathology = self.get_object()
        serializer = AmendReportSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = PathologyReportService(pathology)
        success, message = service.amend_report(
            user=request.user,
            new_diagnosis=serializer.validated_data['new_diagnosis'],
            amendment_reason=serializer.validated_data['amendment_reason'],
        )

        if success:
            pathology.refresh_from_db()
            return Response({
                'success': True,
                'message': message,
                'pathology': PathologySerializer(pathology, context={'request': request}).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_addendum(self, request, pk=None):
        """Add an addendum to the report."""
        pathology = self.get_object()
        serializer = AddAddendumSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = PathologyReportService(pathology)
        success, message, addendum = service.add_addendum(
            author=request.user,
            content=serializer.validated_data['content'],
            reason=serializer.validated_data.get('reason', ''),
        )

        if success:
            return Response({
                'success': True,
                'message': message,
                'addendum': PathologyAddendumSerializer(addendum).data,
            })
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def staging_summary(self, request, pk=None):
        """Get staging summary for a pathology report."""
        pathology = self.get_object()
        summary = TNMStagingService.get_staging_summary(pathology)
        return Response(summary)

    @action(detail=True, methods=['get'])
    def report_content(self, request, pk=None):
        """Get full report content for rendering."""
        pathology = self.get_object()
        service = PathologyReportService(pathology)
        content = service.get_report_content()
        return Response(content)

    @action(detail=False, methods=['post'])
    def calculate_stage(self, request):
        """Calculate stage group from TNM values."""
        serializer = CalculateStageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        tumor_site = None
        if data.get('tumor_site_id'):
            tumor_site = TumorSite.objects.get(pk=data['tumor_site_id'])

        stage_group, notes = TNMStagingService.calculate_stage_group(
            t_stage=data['t_stage'],
            n_stage=data['n_stage'],
            m_stage=data['m_stage'],
            tumor_site=tumor_site,
        )

        return Response({
            'stage_group': stage_group,
            'notes': notes,
            'tnm': f"p{data['t_stage']}{data['n_stage']}{data['m_stage']}",
        })


class PathologyAddendumViewSet(viewsets.ModelViewSet):
    queryset = PathologyAddendum.objects.all().select_related('pathology', 'author').order_by('pathology', 'addendum_number')
    serializer_class = PathologyAddendumSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pathology']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

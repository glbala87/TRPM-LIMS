# api/views/microbiology.py
"""
API Views for microbiology module.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from microbiology.models import (
    TestMethod, BreakpointType, Host, SiteOfInfection, ASTGuideline,
    Kingdom, Phylum, OrganismClass, Order, Family, Genus, Organism,
    AntibioticClass, Antibiotic,
    Breakpoint,
    ASTPanel,
    MicrobiologySample, OrganismResult, ASTResult,
)
from microbiology.services import ASTInterpretationEngine
from api.serializers import (
    TestMethodSerializer, BreakpointTypeSerializer, HostSerializer, SiteOfInfectionSerializer, ASTGuidelineSerializer,
    KingdomSerializer, PhylumSerializer, OrganismClassSerializer, OrderSerializer, FamilySerializer, GenusSerializer,
    OrganismSerializer, OrganismListSerializer,
    AntibioticClassSerializer, AntibioticSerializer, AntibioticListSerializer,
    BreakpointSerializer,
    ASTPanelSerializer, ASTPanelListSerializer,
    MicrobiologySampleSerializer, MicrobiologySampleListSerializer, MicrobiologySampleCreateSerializer,
    OrganismResultSerializer, OrganismResultListSerializer, ASTResultSerializer,
    ASTInterpretationRequestSerializer,
)
from api.pagination import StandardResultsSetPagination


# Reference ViewSets
class TestMethodViewSet(viewsets.ModelViewSet):
    queryset = TestMethod.objects.all().order_by('name')
    serializer_class = TestMethodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class BreakpointTypeViewSet(viewsets.ModelViewSet):
    queryset = BreakpointType.objects.all().order_by('name')
    serializer_class = BreakpointTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all().order_by('name')
    serializer_class = HostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name', 'species']


class SiteOfInfectionViewSet(viewsets.ModelViewSet):
    queryset = SiteOfInfection.objects.all().order_by('name')
    serializer_class = SiteOfInfectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class ASTGuidelineViewSet(viewsets.ModelViewSet):
    queryset = ASTGuideline.objects.all().order_by('-year', 'name')
    serializer_class = ASTGuidelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'year', 'is_current']
    search_fields = ['name', 'version']


# Taxonomy ViewSets
class KingdomViewSet(viewsets.ModelViewSet):
    queryset = Kingdom.objects.all().order_by('name')
    serializer_class = KingdomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class GenusViewSet(viewsets.ModelViewSet):
    queryset = Genus.objects.all().select_related('family').order_by('name')
    serializer_class = GenusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code']


class OrganismViewSet(viewsets.ModelViewSet):
    queryset = Organism.objects.all().select_related('genus', 'family', 'kingdom').order_by('genus__name', 'species')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['organism_type', 'gram_stain', 'kingdom', 'is_pathogen', 'is_active']
    search_fields = ['species', 'genus__name', 'whonet_org_code', 'sct_code']
    ordering_fields = ['species', 'organism_type']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganismListSerializer
        return OrganismSerializer


# Antibiotic ViewSets
class AntibioticClassViewSet(viewsets.ModelViewSet):
    queryset = AntibioticClass.objects.all().order_by('name')
    serializer_class = AntibioticClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['code', 'name']


class AntibioticViewSet(viewsets.ModelViewSet):
    queryset = Antibiotic.objects.all().select_related('antibiotic_class').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['antibiotic_class', 'human_use', 'veterinary_use', 'is_active']
    search_fields = ['name', 'abbreviation', 'whonet_abx_code', 'atc_code']
    ordering_fields = ['name', 'abbreviation']

    def get_serializer_class(self):
        if self.action == 'list':
            return AntibioticListSerializer
        return AntibioticSerializer


# Breakpoint ViewSet
class BreakpointViewSet(viewsets.ModelViewSet):
    queryset = Breakpoint.objects.all().select_related(
        'guideline', 'test_method', 'organism', 'antibiotic'
    ).order_by('guideline', 'antibiotic')
    serializer_class = BreakpointSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['guideline', 'test_method', 'organism', 'antibiotic', 'is_active']
    search_fields = ['organism__species', 'organism_group', 'antibiotic__name']


# Panel ViewSet
class ASTPanelViewSet(viewsets.ModelViewSet):
    queryset = ASTPanel.objects.all().prefetch_related('organisms', 'panel_antibiotics').order_by('name')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['laboratory', 'panel_type', 'guideline', 'is_active']
    search_fields = ['code', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ASTPanelListSerializer
        return ASTPanelSerializer


# Sample ViewSets
class MicrobiologySampleViewSet(viewsets.ModelViewSet):
    queryset = MicrobiologySample.objects.all().select_related(
        'laboratory', 'lab_order'
    ).prefetch_related('organism_results').order_by('-received_datetime')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['laboratory', 'status', 'specimen_type', 'growth_observed']
    search_fields = ['sample_id', 'lab_order__patient__first_name', 'lab_order__patient__last_name']
    ordering_fields = ['sample_id', 'received_datetime', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return MicrobiologySampleListSerializer
        if self.action == 'create':
            return MicrobiologySampleCreateSerializer
        return MicrobiologySampleSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OrganismResultViewSet(viewsets.ModelViewSet):
    queryset = OrganismResult.objects.all().select_related(
        'sample', 'organism', 'ast_panel'
    ).prefetch_related('ast_results').order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['sample', 'organism', 'is_significant', 'is_contaminant', 'identification_method']
    search_fields = ['result_id', 'organism__species']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganismResultListSerializer
        return OrganismResultSerializer

    def perform_create(self, serializer):
        serializer.save(identified_by=self.request.user)

    @action(detail=True, methods=['post'])
    def interpret_all(self, request, pk=None):
        """Interpret all AST results for this organism."""
        organism_result = self.get_object()
        engine = ASTInterpretationEngine()
        results = engine.interpret_organism_result(organism_result)
        return Response({
            'success': True,
            'interpreted_count': len(results),
            'results': results,
        })

    @action(detail=True, methods=['get'])
    def resistance_patterns(self, request, pk=None):
        """Check for known resistance patterns."""
        organism_result = self.get_object()
        engine = ASTInterpretationEngine()
        patterns = engine.check_resistance_patterns(organism_result)
        return Response({
            'patterns': patterns,
        })


class ASTResultViewSet(viewsets.ModelViewSet):
    queryset = ASTResult.objects.all().select_related(
        'organism_result', 'antibiotic', 'breakpoint_used'
    ).order_by('-created_at')
    serializer_class = ASTResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['organism_result', 'antibiotic', 'interpretation', 'test_method', 'is_reported']
    search_fields = ['organism_result__result_id', 'antibiotic__name']

    def perform_create(self, serializer):
        serializer.save(tested_by=self.request.user)

    @action(detail=False, methods=['post'])
    def interpret(self, request):
        """Interpret a single AST value."""
        serializer = ASTInterpretationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        organism = Organism.objects.get(pk=data['organism_id'])
        antibiotic = Antibiotic.objects.get(pk=data['antibiotic_id'])

        guideline = None
        if data.get('guideline_id'):
            guideline = ASTGuideline.objects.get(pk=data['guideline_id'])

        engine = ASTInterpretationEngine(guideline=guideline)
        interpretation, breakpoint = engine.interpret_result(
            organism=organism,
            antibiotic=antibiotic,
            raw_value=data['raw_value'],
            test_method=data['test_method'],
        )

        return Response({
            'interpretation': interpretation,
            'breakpoint_id': breakpoint.id if breakpoint else None,
            'breakpoint_display': str(breakpoint) if breakpoint else None,
        })


class AntibiogramViewSet(viewsets.ViewSet):
    """ViewSet for generating antibiograms."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def generate(self, request):
        """Generate cumulative antibiogram for a laboratory."""
        laboratory_id = request.query_params.get('laboratory_id')
        if not laboratory_id:
            return Response({'error': 'laboratory_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        engine = ASTInterpretationEngine()
        antibiogram = engine.generate_antibiogram(laboratory_id=int(laboratory_id))

        return Response(antibiogram)

"""
URL configuration for the TRPM-LIMS REST API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import (
    # Lab Management
    PatientViewSet, LabOrderViewSet, TestResultViewSet,
    # Molecular Diagnostics
    MolecularSampleTypeViewSet, GeneTargetViewSet, MolecularTestPanelViewSet,
    MolecularSampleViewSet, WorkflowDefinitionViewSet,
    InstrumentRunViewSet, PCRPlateViewSet, NGSLibraryViewSet, NGSPoolViewSet,
    MolecularResultViewSet, VariantCallViewSet,
    QCMetricDefinitionViewSet, ControlSampleViewSet, QCRecordViewSet,
    # Equipment
    InstrumentTypeViewSet, InstrumentViewSet, MaintenanceRecordViewSet,
    # Storage
    StorageUnitViewSet, StorageRackViewSet, StoragePositionViewSet, StorageLogViewSet,
    # Reagents
    ReagentCategoryViewSet, ReagentViewSet, ReagentUsageViewSet, MolecularReagentViewSet,
    # Microbiology
    TestMethodViewSet, BreakpointTypeViewSet, HostViewSet, SiteOfInfectionViewSet, ASTGuidelineViewSet,
    KingdomViewSet, GenusViewSet, OrganismViewSet,
    AntibioticClassViewSet, AntibioticViewSet,
    BreakpointViewSet,
    ASTPanelViewSet,
    MicrobiologySampleViewSet, OrganismResultViewSet, ASTResultViewSet,
    AntibiogramViewSet,
    # QMS
    DocumentCategoryViewSet, DocumentTagViewSet, DocumentTemplateViewSet,
    DocumentFolderViewSet,
    DocumentViewSet, DocumentReviewCycleViewSet, DocumentReviewStepViewSet,
    DocumentSubscriptionViewSet, DocumentCommentViewSet,
    # Messaging
    MessageThreadViewSet, MessageViewSet,
    ActivityFeedViewSet, ActivityStreamViewSet,
    NotificationViewSet, NoticeViewSet,
    # Pathology
    PathologyTypeViewSet, InflammationTypeViewSet, TumorSiteViewSet, TumorMorphologyViewSet,
    SpecimenTypeViewSet, StainingProtocolViewSet,
    HistologyViewSet, HistologyBlockViewSet, HistologySlideViewSet,
    PathologyViewSet, PathologyAddendumViewSet,
)

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()

# Lab Management
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'lab-orders', LabOrderViewSet, basename='lab-order')
router.register(r'test-results', TestResultViewSet, basename='test-result')

# Molecular Diagnostics
router.register(r'sample-types', MolecularSampleTypeViewSet, basename='sample-type')
router.register(r'gene-targets', GeneTargetViewSet, basename='gene-target')
router.register(r'test-panels', MolecularTestPanelViewSet, basename='test-panel')
router.register(r'molecular-samples', MolecularSampleViewSet, basename='molecular-sample')
router.register(r'workflows', WorkflowDefinitionViewSet, basename='workflow')
router.register(r'instrument-runs', InstrumentRunViewSet, basename='instrument-run')
router.register(r'pcr-plates', PCRPlateViewSet, basename='pcr-plate')
router.register(r'ngs-libraries', NGSLibraryViewSet, basename='ngs-library')
router.register(r'ngs-pools', NGSPoolViewSet, basename='ngs-pool')
router.register(r'molecular-results', MolecularResultViewSet, basename='molecular-result')
router.register(r'variant-calls', VariantCallViewSet, basename='variant-call')
router.register(r'qc-metrics', QCMetricDefinitionViewSet, basename='qc-metric')
router.register(r'control-samples', ControlSampleViewSet, basename='control-sample')
router.register(r'qc-records', QCRecordViewSet, basename='qc-record')

# Equipment
router.register(r'instrument-types', InstrumentTypeViewSet, basename='instrument-type')
router.register(r'instruments', InstrumentViewSet, basename='instrument')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance-record')

# Storage
router.register(r'storage-units', StorageUnitViewSet, basename='storage-unit')
router.register(r'storage-racks', StorageRackViewSet, basename='storage-rack')
router.register(r'storage-positions', StoragePositionViewSet, basename='storage-position')
router.register(r'storage-logs', StorageLogViewSet, basename='storage-log')

# Reagents
router.register(r'reagent-categories', ReagentCategoryViewSet, basename='reagent-category')
router.register(r'reagents', ReagentViewSet, basename='reagent')
router.register(r'reagent-usage', ReagentUsageViewSet, basename='reagent-usage')
router.register(r'molecular-reagents', MolecularReagentViewSet, basename='molecular-reagent')

# Microbiology
router.register(r'micro/test-methods', TestMethodViewSet, basename='micro-test-method')
router.register(r'micro/breakpoint-types', BreakpointTypeViewSet, basename='micro-breakpoint-type')
router.register(r'micro/hosts', HostViewSet, basename='micro-host')
router.register(r'micro/sites-of-infection', SiteOfInfectionViewSet, basename='micro-site-of-infection')
router.register(r'micro/guidelines', ASTGuidelineViewSet, basename='micro-guideline')
router.register(r'micro/kingdoms', KingdomViewSet, basename='micro-kingdom')
router.register(r'micro/genera', GenusViewSet, basename='micro-genus')
router.register(r'micro/organisms', OrganismViewSet, basename='micro-organism')
router.register(r'micro/antibiotic-classes', AntibioticClassViewSet, basename='micro-antibiotic-class')
router.register(r'micro/antibiotics', AntibioticViewSet, basename='micro-antibiotic')
router.register(r'micro/breakpoints', BreakpointViewSet, basename='micro-breakpoint')
router.register(r'micro/ast-panels', ASTPanelViewSet, basename='micro-ast-panel')
router.register(r'micro/samples', MicrobiologySampleViewSet, basename='micro-sample')
router.register(r'micro/organism-results', OrganismResultViewSet, basename='micro-organism-result')
router.register(r'micro/ast-results', ASTResultViewSet, basename='micro-ast-result')
router.register(r'micro/antibiogram', AntibiogramViewSet, basename='micro-antibiogram')

# QMS (Quality Management System)
router.register(r'qms/categories', DocumentCategoryViewSet, basename='qms-category')
router.register(r'qms/tags', DocumentTagViewSet, basename='qms-tag')
router.register(r'qms/templates', DocumentTemplateViewSet, basename='qms-template')
router.register(r'qms/folders', DocumentFolderViewSet, basename='qms-folder')
router.register(r'qms/documents', DocumentViewSet, basename='qms-document')
router.register(r'qms/review-cycles', DocumentReviewCycleViewSet, basename='qms-review-cycle')
router.register(r'qms/review-steps', DocumentReviewStepViewSet, basename='qms-review-step')
router.register(r'qms/subscriptions', DocumentSubscriptionViewSet, basename='qms-subscription')
router.register(r'qms/comments', DocumentCommentViewSet, basename='qms-comment')

# Messaging
router.register(r'messaging/threads', MessageThreadViewSet, basename='message-thread')
router.register(r'messaging/messages', MessageViewSet, basename='message')
router.register(r'messaging/activity-feeds', ActivityFeedViewSet, basename='activity-feed')
router.register(r'messaging/activities', ActivityStreamViewSet, basename='activity')
router.register(r'messaging/notifications', NotificationViewSet, basename='notification')
router.register(r'messaging/notices', NoticeViewSet, basename='notice')

# Pathology
router.register(r'pathology/types', PathologyTypeViewSet, basename='pathology-type')
router.register(r'pathology/inflammation-types', InflammationTypeViewSet, basename='inflammation-type')
router.register(r'pathology/tumor-sites', TumorSiteViewSet, basename='tumor-site')
router.register(r'pathology/tumor-morphologies', TumorMorphologyViewSet, basename='tumor-morphology')
router.register(r'pathology/specimen-types', SpecimenTypeViewSet, basename='pathology-specimen-type')
router.register(r'pathology/staining-protocols', StainingProtocolViewSet, basename='staining-protocol')
router.register(r'pathology/histology', HistologyViewSet, basename='histology')
router.register(r'pathology/blocks', HistologyBlockViewSet, basename='histology-block')
router.register(r'pathology/slides', HistologySlideViewSet, basename='histology-slide')
router.register(r'pathology/reports', PathologyViewSet, basename='pathology-report')
router.register(r'pathology/addenda', PathologyAddendumViewSet, basename='pathology-addendum')

urlpatterns = [
    # API routes
    path('', include(router.urls)),

    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

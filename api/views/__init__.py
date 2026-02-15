"""
API Views for TRPM-LIMS.
"""
from .lab_management import PatientViewSet, LabOrderViewSet, TestResultViewSet
from .molecular_diagnostics import (
    MolecularSampleTypeViewSet, GeneTargetViewSet, MolecularTestPanelViewSet,
    MolecularSampleViewSet, WorkflowDefinitionViewSet,
    InstrumentRunViewSet, PCRPlateViewSet, NGSLibraryViewSet, NGSPoolViewSet,
    MolecularResultViewSet, VariantCallViewSet,
    QCMetricDefinitionViewSet, ControlSampleViewSet, QCRecordViewSet,
)
from .equipment import InstrumentTypeViewSet, InstrumentViewSet, MaintenanceRecordViewSet
from .storage import StorageUnitViewSet, StorageRackViewSet, StoragePositionViewSet, StorageLogViewSet
from .reagents import (
    ReagentCategoryViewSet, ReagentViewSet, ReagentUsageViewSet, MolecularReagentViewSet
)
from .microbiology import (
    TestMethodViewSet, BreakpointTypeViewSet, HostViewSet, SiteOfInfectionViewSet, ASTGuidelineViewSet,
    KingdomViewSet, GenusViewSet, OrganismViewSet,
    AntibioticClassViewSet, AntibioticViewSet,
    BreakpointViewSet,
    ASTPanelViewSet,
    MicrobiologySampleViewSet, OrganismResultViewSet, ASTResultViewSet,
    AntibiogramViewSet,
)
from .qms import (
    DocumentCategoryViewSet, DocumentTagViewSet, DocumentTemplateViewSet,
    DocumentFolderViewSet,
    DocumentViewSet, DocumentReviewCycleViewSet, DocumentReviewStepViewSet,
    DocumentSubscriptionViewSet, DocumentCommentViewSet,
)
from .messaging import (
    MessageThreadViewSet, MessageViewSet,
    ActivityFeedViewSet, ActivityStreamViewSet,
    NotificationViewSet, NoticeViewSet,
)
from .pathology import (
    PathologyTypeViewSet, InflammationTypeViewSet, TumorSiteViewSet, TumorMorphologyViewSet,
    SpecimenTypeViewSet, StainingProtocolViewSet,
    HistologyViewSet, HistologyBlockViewSet, HistologySlideViewSet,
    PathologyViewSet, PathologyAddendumViewSet,
)

__all__ = [
    # Lab Management
    'PatientViewSet', 'LabOrderViewSet', 'TestResultViewSet',
    # Molecular Diagnostics
    'MolecularSampleTypeViewSet', 'GeneTargetViewSet', 'MolecularTestPanelViewSet',
    'MolecularSampleViewSet', 'WorkflowDefinitionViewSet',
    'InstrumentRunViewSet', 'PCRPlateViewSet', 'NGSLibraryViewSet', 'NGSPoolViewSet',
    'MolecularResultViewSet', 'VariantCallViewSet',
    'QCMetricDefinitionViewSet', 'ControlSampleViewSet', 'QCRecordViewSet',
    # Equipment
    'InstrumentTypeViewSet', 'InstrumentViewSet', 'MaintenanceRecordViewSet',
    # Storage
    'StorageUnitViewSet', 'StorageRackViewSet', 'StoragePositionViewSet', 'StorageLogViewSet',
    # Reagents
    'ReagentCategoryViewSet', 'ReagentViewSet', 'ReagentUsageViewSet', 'MolecularReagentViewSet',
    # Microbiology
    'TestMethodViewSet', 'BreakpointTypeViewSet', 'HostViewSet', 'SiteOfInfectionViewSet', 'ASTGuidelineViewSet',
    'KingdomViewSet', 'GenusViewSet', 'OrganismViewSet',
    'AntibioticClassViewSet', 'AntibioticViewSet',
    'BreakpointViewSet',
    'ASTPanelViewSet',
    'MicrobiologySampleViewSet', 'OrganismResultViewSet', 'ASTResultViewSet',
    'AntibiogramViewSet',
    # QMS
    'DocumentCategoryViewSet', 'DocumentTagViewSet', 'DocumentTemplateViewSet',
    'DocumentFolderViewSet',
    'DocumentViewSet', 'DocumentReviewCycleViewSet', 'DocumentReviewStepViewSet',
    'DocumentSubscriptionViewSet', 'DocumentCommentViewSet',
    # Messaging
    'MessageThreadViewSet', 'MessageViewSet',
    'ActivityFeedViewSet', 'ActivityStreamViewSet',
    'NotificationViewSet', 'NoticeViewSet',
    # Pathology
    'PathologyTypeViewSet', 'InflammationTypeViewSet', 'TumorSiteViewSet', 'TumorMorphologyViewSet',
    'SpecimenTypeViewSet', 'StainingProtocolViewSet',
    'HistologyViewSet', 'HistologyBlockViewSet', 'HistologySlideViewSet',
    'PathologyViewSet', 'PathologyAddendumViewSet',
]

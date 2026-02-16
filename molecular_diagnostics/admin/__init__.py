# molecular_diagnostics/admin/__init__.py

from .samples import MolecularSampleTypeAdmin, MolecularSampleAdmin
from .tests import GeneTargetAdmin, MolecularTestPanelAdmin
from .workflows import WorkflowDefinitionAdmin, WorkflowStepAdmin, SampleHistoryAdmin
from .batches import InstrumentRunAdmin, PCRPlateAdmin, NGSLibraryAdmin, NGSPoolAdmin
from .qc import QCMetricDefinitionAdmin, ControlSampleAdmin, QCRecordAdmin
from .results import MolecularResultAdmin, PCRResultAdmin, SequencingResultAdmin, VariantCallAdmin
from .annotations import VariantAnnotationAdmin, AnnotationCacheAdmin

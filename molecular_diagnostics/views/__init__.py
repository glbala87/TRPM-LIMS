# molecular_diagnostics/views/__init__.py

from .dashboard_views import dashboard, tat_dashboard, at_risk_samples
from .sample_views import sample_list, sample_detail, sample_transition
from .report_views import generate_report, download_report
from .plate_views import plate_list, plate_detail, plate_layout

__all__ = [
    'dashboard',
    'tat_dashboard',
    'at_risk_samples',
    'sample_list',
    'sample_detail',
    'sample_transition',
    'generate_report',
    'download_report',
    'plate_list',
    'plate_detail',
    'plate_layout',
]

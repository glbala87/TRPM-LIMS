# molecular_diagnostics/views/report_views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
import mimetypes

from ..models import MolecularResult
from ..services.report_generator import ReportGenerator


@login_required
def generate_report(request, pk):
    """Generate PDF report for a molecular result"""
    result = get_object_or_404(
        MolecularResult.objects.select_related(
            'sample__lab_order__patient',
            'test_panel'
        ),
        pk=pk
    )

    if request.method == 'POST':
        if not result.is_reportable:
            messages.error(request, 'Result must be finalized before generating report')
            return redirect('admin:molecular_diagnostics_molecularresult_change', pk)

        generator = ReportGenerator()

        try:
            report_path = generator.generate_report(result, request.user)
            messages.success(request, 'Report generated successfully')
        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')

        return redirect('admin:molecular_diagnostics_molecularresult_change', pk)

    return redirect('admin:molecular_diagnostics_molecularresult_change', pk)


@login_required
def download_report(request, pk):
    """Download a generated PDF report"""
    result = get_object_or_404(MolecularResult, pk=pk)

    if not result.report_file:
        messages.error(request, 'No report has been generated for this result')
        return redirect('admin:molecular_diagnostics_molecularresult_change', pk)

    file_path = result.report_file.path
    content_type, _ = mimetypes.guess_type(file_path)

    response = FileResponse(
        open(file_path, 'rb'),
        content_type=content_type or 'application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="{result.sample.sample_id}_report.pdf"'

    return response

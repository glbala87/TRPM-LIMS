# molecular_diagnostics/services/report_generator.py

from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
import os

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    # OSError occurs when WeasyPrint is installed but system dependencies are missing
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None


class ReportGenerator:
    """
    PDF report generator for molecular diagnostics results.

    Uses WeasyPrint for HTML to PDF conversion.
    """

    REPORT_TEMPLATES = {
        'PCR': 'molecular_diagnostics/reports/pcr_report.html',
        'RT_PCR': 'molecular_diagnostics/reports/pcr_report.html',
        'NGS': 'molecular_diagnostics/reports/ngs_report.html',
        'SANGER': 'molecular_diagnostics/reports/sanger_report.html',
        'DEFAULT': 'molecular_diagnostics/reports/base_report.html',
    }

    def __init__(self):
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint is required for PDF generation. "
                "Install it with: pip install weasyprint"
            )

    def generate_report(self, result, generated_by=None):
        """
        Generate a PDF report for a molecular result.

        Args:
            result: MolecularResult instance
            generated_by: User generating the report

        Returns:
            Path to generated PDF file

        Raises:
            ValueError: If result is not reportable
        """
        if not result.is_reportable:
            raise ValueError("Result must be finalized before generating report")

        # Determine template based on test type
        test_type = result.test_panel.test_type
        template_name = self.REPORT_TEMPLATES.get(
            test_type,
            self.REPORT_TEMPLATES['DEFAULT']
        )

        # Prepare context
        context = self._build_context(result)

        # Render HTML
        html_content = render_to_string(template_name, context)

        # Generate PDF
        pdf_content = self._render_pdf(html_content)

        # Save to result
        filename = f"{result.sample.sample_id}_{result.test_panel.code}_report.pdf"
        result.report_file.save(filename, ContentFile(pdf_content))
        result.report_generated = True
        result.report_generated_at = timezone.now()
        result.save()

        return result.report_file.path

    def _build_context(self, result):
        """Build the template context for report generation."""
        sample = result.sample
        patient = sample.lab_order.patient
        test_panel = result.test_panel

        context = {
            'result': result,
            'sample': sample,
            'patient': patient,
            'test_panel': test_panel,
            'lab_order': sample.lab_order,
            'report_date': timezone.now(),

            # Patient info
            'patient_name': f"{patient.first_name} {patient.last_name}",
            'patient_id': patient.OP_NO,
            'patient_age': patient.age,
            'patient_gender': patient.gender,

            # Sample info
            'sample_id': sample.sample_id,
            'sample_type': sample.sample_type.name if sample.sample_type else '',
            'collection_date': sample.collection_datetime,
            'received_date': sample.received_datetime,

            # Test info
            'test_name': test_panel.name,
            'test_code': test_panel.code,
            'test_type': test_panel.get_test_type_display(),
            'methodology': test_panel.methodology,

            # Results
            'interpretation': result.get_interpretation_display(),
            'clinical_significance': result.clinical_significance,
            'recommendations': result.recommendations,
            'limitations': result.limitations,

            # Approval info
            'performed_by': result.performed_by,
            'performed_at': result.performed_at,
            'approved_by': result.approved_by,
            'approved_at': result.approved_at,

            # Lab info (could be from settings)
            'lab_name': getattr(settings, 'LAB_NAME', 'Molecular Diagnostics Laboratory'),
            'lab_address': getattr(settings, 'LAB_ADDRESS', ''),
            'lab_phone': getattr(settings, 'LAB_PHONE', ''),
            'lab_accreditation': getattr(settings, 'LAB_ACCREDITATION', ''),
        }

        # Add test-type specific data
        if test_panel.test_type in ['PCR', 'RT_PCR']:
            context.update(self._get_pcr_context(result))
        elif test_panel.test_type == 'NGS':
            context.update(self._get_ngs_context(result))

        return context

    def _get_pcr_context(self, result):
        """Get PCR-specific context data."""
        pcr_results = result.pcr_results.select_related('target_gene').all()

        return {
            'pcr_results': pcr_results,
            'targets_tested': [r.target_gene for r in pcr_results],
            'detected_targets': [r.target_gene for r in pcr_results if r.is_detected == 'DETECTED'],
        }

    def _get_ngs_context(self, result):
        """Get NGS-specific context data."""
        context = {
            'variant_calls': result.variant_calls.select_related('gene').all(),
        }

        # Add sequencing metrics if available
        try:
            seq_result = result.sequencing_result
            context.update({
                'sequencing_metrics': {
                    'total_reads': seq_result.total_reads,
                    'mean_coverage': seq_result.mean_coverage,
                    'q30_percentage': seq_result.q30_percentage,
                    'on_target_percentage': seq_result.on_target_percentage,
                }
            })
        except result.sequencing_result.RelatedObjectDoesNotExist:
            context['sequencing_metrics'] = None

        # Categorize variants
        pathogenic = []
        vus = []
        benign = []

        for variant in context['variant_calls']:
            if variant.is_clinically_significant:
                pathogenic.append(variant)
            elif variant.classification == 'VUS':
                vus.append(variant)
            else:
                benign.append(variant)

        context.update({
            'pathogenic_variants': pathogenic,
            'vus_variants': vus,
            'benign_variants': benign,
        })

        return context

    def _render_pdf(self, html_content):
        """Render HTML content to PDF bytes."""
        # Get CSS for styling
        css_content = self._get_report_css()

        html = HTML(string=html_content)
        css = CSS(string=css_content)

        return html.write_pdf(stylesheets=[css])

    def _get_report_css(self):
        """Get CSS styling for reports."""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Molecular Diagnostics Report";
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
            }
        }

        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }

        .header {
            text-align: center;
            border-bottom: 2px solid #2c5282;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .header h1 {
            color: #2c5282;
            margin: 0;
            font-size: 18pt;
        }

        .lab-info {
            font-size: 9pt;
            color: #666;
        }

        .section {
            margin-bottom: 15px;
        }

        .section-title {
            background-color: #2c5282;
            color: white;
            padding: 5px 10px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }

        .info-table td {
            padding: 3px 5px;
            border: 1px solid #ddd;
        }

        .info-table .label {
            background-color: #f7fafc;
            font-weight: bold;
            width: 30%;
        }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }

        .results-table th {
            background-color: #2c5282;
            color: white;
            padding: 8px;
            text-align: left;
        }

        .results-table td {
            padding: 6px 8px;
            border: 1px solid #ddd;
        }

        .results-table tr:nth-child(even) {
            background-color: #f7fafc;
        }

        .positive {
            color: #c53030;
            font-weight: bold;
        }

        .negative {
            color: #2f855a;
            font-weight: bold;
        }

        .pathogenic {
            color: #c53030;
            font-weight: bold;
        }

        .vus {
            color: #d69e2e;
        }

        .benign {
            color: #2f855a;
        }

        .interpretation-box {
            border: 2px solid #2c5282;
            padding: 10px;
            margin: 15px 0;
            background-color: #f7fafc;
        }

        .signature-section {
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
        }

        .signature-block {
            width: 45%;
            text-align: center;
        }

        .signature-line {
            border-top: 1px solid #333;
            margin-top: 40px;
            padding-top: 5px;
        }

        .disclaimer {
            font-size: 8pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            margin-top: 20px;
        }

        .qc-metrics {
            font-size: 9pt;
            color: #666;
        }
        """

    def generate_batch_report(self, results, output_path=None):
        """
        Generate a combined report for multiple results.

        Args:
            results: List of MolecularResult instances
            output_path: Optional path for output file

        Returns:
            Path to generated PDF file
        """
        # For batch reports, generate individual PDFs and combine
        # This is a simplified implementation
        pdf_contents = []

        for result in results:
            if result.is_reportable:
                context = self._build_context(result)
                test_type = result.test_panel.test_type
                template_name = self.REPORT_TEMPLATES.get(
                    test_type,
                    self.REPORT_TEMPLATES['DEFAULT']
                )
                html_content = render_to_string(template_name, context)
                pdf_contents.append(self._render_pdf(html_content))

        # For now, return the first report
        # A full implementation would merge PDFs
        if pdf_contents and output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_contents[0])
            return output_path

        return None

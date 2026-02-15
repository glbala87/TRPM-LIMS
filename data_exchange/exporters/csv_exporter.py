"""
CSV export functionality.
"""
import csv
import io
from typing import List, Dict, Any, Callable
from datetime import datetime, date
from django.db.models import QuerySet


class CSVExporter:
    """
    Generic CSV exporter for Django models.
    """

    def __init__(self, queryset: QuerySet, fields: List[str] = None,
                 field_labels: Dict[str, str] = None,
                 field_formatters: Dict[str, Callable] = None,
                 date_format: str = '%Y-%m-%d',
                 datetime_format: str = '%Y-%m-%d %H:%M:%S'):
        """
        Initialize CSV exporter.

        Args:
            queryset: Django QuerySet to export
            fields: List of field names to include (default: all fields)
            field_labels: Dict mapping field names to column headers
            field_formatters: Dict mapping field names to formatter functions
            date_format: Format string for date fields
            datetime_format: Format string for datetime fields
        """
        self.queryset = queryset
        self.model = queryset.model
        self.fields = fields or self._get_default_fields()
        self.field_labels = field_labels or {}
        self.field_formatters = field_formatters or {}
        self.date_format = date_format
        self.datetime_format = datetime_format

    def _get_default_fields(self) -> List[str]:
        """Get list of all model field names."""
        return [f.name for f in self.model._meta.fields]

    def _get_header(self) -> List[str]:
        """Get column headers."""
        headers = []
        for field in self.fields:
            label = self.field_labels.get(field, field.replace('_', ' ').title())
            headers.append(label)
        return headers

    def _format_value(self, obj: Any, field_name: str) -> str:
        """Format a field value for CSV output."""
        # Get value using attribute access or related lookup
        value = obj
        for part in field_name.split('__'):
            if value is None:
                break
            value = getattr(value, part, None)

        # Apply custom formatter if provided
        if field_name in self.field_formatters:
            return self.field_formatters[field_name](value)

        # Handle None
        if value is None:
            return ''

        # Format dates
        if isinstance(value, datetime):
            return value.strftime(self.datetime_format)
        if isinstance(value, date):
            return value.strftime(self.date_format)

        # Handle related objects
        if hasattr(value, 'pk'):
            return str(value)

        # Handle callables (like get_status_display)
        if callable(value):
            return str(value())

        return str(value)

    def _get_row(self, obj: Any) -> List[str]:
        """Get a row of values for an object."""
        return [self._format_value(obj, field) for field in self.fields]

    def export_to_string(self) -> str:
        """Export to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(self._get_header())

        # Write data rows
        for obj in self.queryset:
            writer.writerow(self._get_row(obj))

        return output.getvalue()

    def export_to_file(self, file_path: str):
        """Export to CSV file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self._get_header())
            for obj in self.queryset:
                writer.writerow(self._get_row(obj))

    def export_to_response(self, filename: str = 'export.csv'):
        """Export to Django HttpResponse for download."""
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(self._get_header())

        for obj in self.queryset:
            writer.writerow(self._get_row(obj))

        return response


# Pre-configured exporters for common models

class PatientCSVExporter(CSVExporter):
    """CSV exporter for Patient records."""

    def __init__(self, queryset, **kwargs):
        from lab_management.models import Patient

        fields = kwargs.pop('fields', [
            'OP_NO', 'first_name', 'middle_name', 'last_name',
            'gender', 'age', 'nationality', 'client_name',
            'registered_date'
        ])

        field_labels = kwargs.pop('field_labels', {
            'OP_NO': 'Patient ID',
            'first_name': 'First Name',
            'middle_name': 'Middle Name',
            'last_name': 'Last Name',
            'gender': 'Gender',
            'age': 'Age',
            'nationality': 'Nationality',
            'client_name': 'Hospital/Clinic',
            'registered_date': 'Registration Date',
        })

        super().__init__(queryset, fields=fields, field_labels=field_labels, **kwargs)


class SampleCSVExporter(CSVExporter):
    """CSV exporter for MolecularSample records."""

    def __init__(self, queryset, **kwargs):
        fields = kwargs.pop('fields', [
            'sample_id', 'lab_order__patient__OP_NO', 'sample_type__name',
            'status', 'priority', 'collection_date', 'received_date',
            'volume_ul', 'concentration_ng_ul', 'a260_280_ratio'
        ])

        field_labels = kwargs.pop('field_labels', {
            'sample_id': 'Sample ID',
            'lab_order__patient__OP_NO': 'Patient ID',
            'sample_type__name': 'Sample Type',
            'status': 'Status',
            'priority': 'Priority',
            'collection_date': 'Collection Date',
            'received_date': 'Received Date',
            'volume_ul': 'Volume (uL)',
            'concentration_ng_ul': 'Concentration (ng/uL)',
            'a260_280_ratio': 'A260/280 Ratio',
        })

        super().__init__(queryset, fields=fields, field_labels=field_labels, **kwargs)


class ResultsCSVExporter(CSVExporter):
    """CSV exporter for MolecularResult records."""

    def __init__(self, queryset, **kwargs):
        fields = kwargs.pop('fields', [
            'sample__sample_id', 'test_panel__name', 'status',
            'interpretation', 'performed_date', 'approved_date',
            'summary', 'clinical_significance'
        ])

        field_labels = kwargs.pop('field_labels', {
            'sample__sample_id': 'Sample ID',
            'test_panel__name': 'Test Panel',
            'status': 'Status',
            'interpretation': 'Interpretation',
            'performed_date': 'Performed Date',
            'approved_date': 'Approved Date',
            'summary': 'Summary',
            'clinical_significance': 'Clinical Significance',
        })

        super().__init__(queryset, fields=fields, field_labels=field_labels, **kwargs)

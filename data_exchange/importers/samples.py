"""
Sample data importer.
"""
from typing import Dict, List, Any
from datetime import datetime
from .base import BaseImporter, ValidationError
from molecular_diagnostics.models import MolecularSample, MolecularSampleType
from lab_management.models import Patient, LabOrder


class MolecularSampleImporter(BaseImporter):
    """
    Importer for MolecularSample records.

    Expected CSV columns:
    - patient_id OR patient_op_no (required)
    - sample_type (required)
    - collection_date (required)
    - collection_time
    - volume_ul
    - priority
    - notes
    """

    model = MolecularSample
    duplicate_field = 'sample_id'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cache sample types
        self._sample_types = {st.name.lower(): st for st in MolecularSampleType.objects.all()}
        self._sample_types.update({st.code.lower(): st for st in MolecularSampleType.objects.all() if st.code})

    def get_required_fields(self) -> List[str]:
        return ['sample_type', 'collection_date']

    def get_field_mapping(self) -> Dict[str, str]:
        return {
            'patient_id': 'patient_id',
            'Patient ID': 'patient_id',
            'patient_op_no': 'patient_op_no',
            'Patient OP No': 'patient_op_no',
            'OP_NO': 'patient_op_no',
            'sample_type': 'sample_type',
            'Sample Type': 'sample_type',
            'Type': 'sample_type',
            'collection_date': 'collection_date',
            'Collection Date': 'collection_date',
            'Date': 'collection_date',
            'collection_time': 'collection_time',
            'Collection Time': 'collection_time',
            'Time': 'collection_time',
            'volume_ul': 'volume_ul',
            'Volume': 'volume_ul',
            'Volume (uL)': 'volume_ul',
            'priority': 'priority',
            'Priority': 'priority',
            'notes': 'notes',
            'Notes': 'notes',
            'quality_notes': 'quality_notes',
            'Quality Notes': 'quality_notes',
            'concentration_ng_ul': 'concentration_ng_ul',
            'Concentration': 'concentration_ng_ul',
            'a260_280_ratio': 'a260_280_ratio',
            'A260/280': 'a260_280_ratio',
        }

    def validate_row(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        errors = []

        # Must have either patient_id or patient_op_no
        if not row_data.get('patient_id') and not row_data.get('patient_op_no'):
            errors.append(ValidationError(
                row_number,
                'patient',
                "Either patient_id or patient_op_no is required"
            ))

        # Validate sample type exists
        sample_type = row_data.get('sample_type', '').lower()
        if sample_type and sample_type not in self._sample_types:
            errors.append(ValidationError(
                row_number,
                'sample_type',
                f"Unknown sample type '{sample_type}'"
            ))

        # Validate collection date format
        collection_date = row_data.get('collection_date')
        if collection_date:
            if not self._parse_date(collection_date):
                errors.append(ValidationError(
                    row_number,
                    'collection_date',
                    f"Invalid date format '{collection_date}'. Use YYYY-MM-DD."
                ))

        # Validate priority
        priority = row_data.get('priority', '').upper()
        if priority and priority not in ['ROUTINE', 'URGENT', 'STAT']:
            errors.append(ValidationError(
                row_number,
                'priority',
                f"Invalid priority '{priority}'. Must be ROUTINE, URGENT, or STAT."
            ))

        # Validate numeric fields
        for field in ['volume_ul', 'concentration_ng_ul', 'a260_280_ratio']:
            value = row_data.get(field)
            if value:
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        row_number,
                        field,
                        f"Invalid numeric value '{value}'"
                    ))

        return errors

    def _parse_date(self, date_str):
        """Parse date string in various formats."""
        if not date_str:
            return None

        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']

        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue

        return None

    def _parse_time(self, time_str):
        """Parse time string."""
        if not time_str:
            return None

        formats = ['%H:%M:%S', '%H:%M', '%I:%M %p', '%I:%M:%S %p']

        for fmt in formats:
            try:
                return datetime.strptime(str(time_str), fmt).time()
            except ValueError:
                continue

        return None

    def create_object(self, row_data: Dict) -> MolecularSample:
        # Find patient
        patient = None
        if row_data.get('patient_id'):
            patient = Patient.objects.get(pk=row_data['patient_id'])
        elif row_data.get('patient_op_no'):
            patient = Patient.objects.get(OP_NO=row_data['patient_op_no'])

        # Find or create lab order
        lab_order, _ = LabOrder.objects.get_or_create(
            patient=patient,
            test_category='MOLECULAR',
            defaults={'test_name': 'Imported Sample'}
        )

        # Get sample type
        sample_type_name = row_data.get('sample_type', '').lower()
        sample_type = self._sample_types.get(sample_type_name)

        # Parse dates
        collection_date = self._parse_date(row_data.get('collection_date'))
        collection_time = self._parse_time(row_data.get('collection_time'))

        # Build sample data
        sample_data = {
            'lab_order': lab_order,
            'sample_type': sample_type,
            'collection_date': collection_date,
            'collection_time': collection_time,
            'priority': row_data.get('priority', 'ROUTINE').upper(),
            'quality_notes': row_data.get('quality_notes') or row_data.get('notes', ''),
        }

        # Add numeric fields
        for field in ['volume_ul', 'concentration_ng_ul', 'a260_280_ratio']:
            value = row_data.get(field)
            if value:
                sample_data[field] = float(value)

        # Set received date and user if available
        from django.utils import timezone
        sample_data['received_date'] = timezone.now().date()
        if self.user:
            sample_data['received_by'] = self.user

        sample = MolecularSample.objects.create(**sample_data)
        return sample

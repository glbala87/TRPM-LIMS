"""
Patient data importer.
"""
from typing import Dict, List, Any
from .base import BaseImporter, ValidationError
from lab_management.models import Patient


class PatientImporter(BaseImporter):
    """
    Importer for Patient records.

    Expected CSV columns:
    - first_name (required)
    - last_name (required)
    - middle_name
    - gender (required: M/F)
    - age
    - nationality
    - passport_no
    - resident_card
    - client_name
    - tribe
    - marital_status
    """

    model = Patient
    duplicate_field = 'OP_NO'  # Check by OP_NO if provided

    def get_required_fields(self) -> List[str]:
        return ['first_name', 'last_name', 'gender']

    def get_field_mapping(self) -> Dict[str, str]:
        return {
            'first_name': 'first_name',
            'First Name': 'first_name',
            'FirstName': 'first_name',
            'last_name': 'last_name',
            'Last Name': 'last_name',
            'LastName': 'last_name',
            'middle_name': 'middle_name',
            'Middle Name': 'middle_name',
            'gender': 'gender',
            'Gender': 'gender',
            'sex': 'gender',
            'Sex': 'gender',
            'age': 'age',
            'Age': 'age',
            'nationality': 'nationality',
            'Nationality': 'nationality',
            'passport_no': 'passport_no',
            'Passport': 'passport_no',
            'Passport No': 'passport_no',
            'resident_card': 'resident_card',
            'Resident Card': 'resident_card',
            'client_name': 'client_name',
            'Client': 'client_name',
            'Hospital': 'client_name',
            'Clinic': 'client_name',
            'tribe': 'tribe',
            'Tribe': 'tribe',
            'marital_status': 'marital_status',
            'Marital Status': 'marital_status',
            'OP_NO': 'OP_NO',
            'op_no': 'OP_NO',
            'Patient ID': 'OP_NO',
        }

    def validate_row(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        errors = []

        # Validate gender
        gender = row_data.get('gender', '').upper()
        if gender and gender not in ['M', 'F', 'MALE', 'FEMALE']:
            errors.append(ValidationError(
                row_number,
                'gender',
                f"Invalid gender '{gender}'. Must be M or F."
            ))

        # Validate age if provided
        age = row_data.get('age')
        if age:
            try:
                age_int = int(age)
                if age_int < 0 or age_int > 150:
                    errors.append(ValidationError(
                        row_number,
                        'age',
                        f"Invalid age '{age}'. Must be between 0 and 150."
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    row_number,
                    'age',
                    f"Invalid age '{age}'. Must be a number."
                ))

        return errors

    def create_object(self, row_data: Dict) -> Patient:
        # Normalize gender
        gender = row_data.get('gender', '').upper()
        if gender in ['MALE', 'M']:
            row_data['gender'] = 'M'
        elif gender in ['FEMALE', 'F']:
            row_data['gender'] = 'F'

        # Convert age to integer
        if row_data.get('age'):
            row_data['age'] = int(row_data['age'])

        # Create patient
        patient = Patient.objects.create(**row_data)
        return patient

    def check_duplicate(self, row_data: Dict):
        """Check for duplicate by passport or name combination."""
        # Check by passport if provided
        passport = row_data.get('passport_no')
        if passport:
            existing = Patient.objects.filter(passport_no=passport).first()
            if existing:
                return existing

        # Check by name combination
        first_name = row_data.get('first_name', '')
        last_name = row_data.get('last_name', '')

        if first_name and last_name:
            existing = Patient.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            ).first()
            if existing:
                return existing

        return None

"""
Base importer class for data import operations.
"""
import csv
import io
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple, Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import openpyxl


class ValidationError:
    """Represents a validation error for a row."""
    def __init__(self, row_number: int, field: str, message: str):
        self.row_number = row_number
        self.field = field
        self.message = message

    def to_dict(self):
        return {
            'row': self.row_number,
            'field': self.field,
            'message': self.message
        }


class ImportResult:
    """Result of importing a single row."""
    def __init__(self, row_number: int, status: str, obj=None, error: str = ''):
        self.row_number = row_number
        self.status = status  # SUCCESS, FAILED, SKIPPED, DUPLICATE
        self.obj = obj
        self.error = error


class BaseImporter(ABC):
    """
    Base class for data importers.

    Subclasses should implement:
    - get_required_fields(): Return list of required field names
    - get_field_mapping(): Return dict mapping CSV columns to model fields
    - validate_row(row_data): Validate a single row
    - create_object(row_data): Create/update model instance
    """

    # Model class to import into
    model = None

    # Field that determines duplicates
    duplicate_field = None

    def __init__(self, import_job=None, user=None):
        self.import_job = import_job
        self.user = user
        self.errors: List[ValidationError] = []
        self.warnings: List[Dict] = []
        self.results: List[ImportResult] = []

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required field names."""
        pass

    @abstractmethod
    def get_field_mapping(self) -> Dict[str, str]:
        """Return mapping of source columns to model fields."""
        pass

    @abstractmethod
    def validate_row(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        """Validate a single row. Return list of errors."""
        pass

    @abstractmethod
    def create_object(self, row_data: Dict) -> Any:
        """Create or update model instance from row data."""
        pass

    def read_csv(self, file_obj) -> List[Dict]:
        """Read CSV file and return list of row dictionaries."""
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8-sig')

        reader = csv.DictReader(io.StringIO(content))
        return list(reader)

    def read_excel(self, file_obj) -> List[Dict]:
        """Read Excel file and return list of row dictionaries."""
        wb = openpyxl.load_workbook(file_obj, read_only=True)
        ws = wb.active

        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        headers = [str(h).strip() if h else f'column_{i}' for i, h in enumerate(rows[0])]
        data = []

        for row in rows[1:]:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = value
            data.append(row_dict)

        return data

    def read_file(self, file_obj, file_format: str = 'CSV') -> List[Dict]:
        """Read file based on format."""
        if file_format.upper() == 'XLSX':
            return self.read_excel(file_obj)
        return self.read_csv(file_obj)

    def map_row(self, row_data: Dict) -> Dict:
        """Apply field mapping to row data."""
        mapping = self.get_field_mapping()
        mapped = {}

        for source_col, target_field in mapping.items():
            if source_col in row_data:
                value = row_data[source_col]
                # Clean string values
                if isinstance(value, str):
                    value = value.strip()
                mapped[target_field] = value

        return mapped

    def validate_required_fields(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        """Check that all required fields are present."""
        errors = []
        required = self.get_required_fields()
        mapping = self.get_field_mapping()

        for field in required:
            # Find the source column for this field
            source_col = None
            for src, tgt in mapping.items():
                if tgt == field:
                    source_col = src
                    break

            if source_col and (source_col not in row_data or not row_data.get(source_col)):
                errors.append(ValidationError(
                    row_number,
                    field,
                    f"Required field '{source_col}' is missing or empty"
                ))

        return errors

    def check_duplicate(self, row_data: Dict) -> Optional[Any]:
        """Check if record already exists. Returns existing object or None."""
        if not self.duplicate_field or not self.model:
            return None

        value = row_data.get(self.duplicate_field)
        if not value:
            return None

        try:
            return self.model.objects.get(**{self.duplicate_field: value})
        except self.model.DoesNotExist:
            return None

    def validate(self, data: List[Dict]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate all rows.
        Returns (is_valid, errors)
        """
        self.errors = []

        for i, row in enumerate(data, start=2):  # Start at 2 assuming header is row 1
            # Check required fields
            req_errors = self.validate_required_fields(row, i)
            self.errors.extend(req_errors)

            # Map and validate row
            mapped_row = self.map_row(row)
            row_errors = self.validate_row(mapped_row, i)
            self.errors.extend(row_errors)

        return len(self.errors) == 0, self.errors

    def import_data(self, data: List[Dict], skip_duplicates=True, update_existing=False) -> List[ImportResult]:
        """
        Import all rows.

        Args:
            data: List of row dictionaries
            skip_duplicates: Skip rows that already exist
            update_existing: Update existing records instead of skipping

        Returns:
            List of ImportResult objects
        """
        self.results = []

        for i, row in enumerate(data, start=2):
            mapped_row = self.map_row(row)

            try:
                # Check for duplicates
                existing = self.check_duplicate(mapped_row)

                if existing:
                    if skip_duplicates and not update_existing:
                        self.results.append(ImportResult(i, 'DUPLICATE', existing))
                        continue
                    elif update_existing:
                        # Update existing record
                        obj = self.update_object(existing, mapped_row)
                        self.results.append(ImportResult(i, 'SUCCESS', obj))
                        continue

                # Create new record
                with transaction.atomic():
                    obj = self.create_object(mapped_row)
                    self.results.append(ImportResult(i, 'SUCCESS', obj))

            except Exception as e:
                self.results.append(ImportResult(i, 'FAILED', error=str(e)))

        return self.results

    def update_object(self, obj: Any, row_data: Dict) -> Any:
        """Update existing object with new data. Override in subclasses."""
        for field, value in row_data.items():
            if hasattr(obj, field) and value is not None:
                setattr(obj, field, value)
        obj.save()
        return obj

    def get_summary(self) -> Dict:
        """Get import summary statistics."""
        success_count = sum(1 for r in self.results if r.status == 'SUCCESS')
        failed_count = sum(1 for r in self.results if r.status == 'FAILED')
        skipped_count = sum(1 for r in self.results if r.status == 'SKIPPED')
        duplicate_count = sum(1 for r in self.results if r.status == 'DUPLICATE')

        return {
            'total': len(self.results),
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'duplicates': duplicate_count,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': self.warnings,
        }

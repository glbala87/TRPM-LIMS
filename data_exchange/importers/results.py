"""
Results data importer.
"""
from typing import Dict, List
from .base import BaseImporter, ValidationError
from molecular_diagnostics.models import MolecularSample, MolecularResult, MolecularTestPanel, PCRResult, GeneTarget


class ResultsImporter(BaseImporter):
    """
    Importer for test results.

    Expected CSV columns:
    - sample_id (required)
    - test_panel (required)
    - interpretation
    - summary
    - clinical_significance
    - recommendations
    """

    model = MolecularResult

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cache test panels
        self._test_panels = {tp.code.lower(): tp for tp in MolecularTestPanel.objects.all() if tp.code}
        self._test_panels.update({tp.name.lower(): tp for tp in MolecularTestPanel.objects.all()})

    def get_required_fields(self) -> List[str]:
        return ['sample_id', 'test_panel']

    def get_field_mapping(self) -> Dict[str, str]:
        return {
            'sample_id': 'sample_id',
            'Sample ID': 'sample_id',
            'SampleID': 'sample_id',
            'test_panel': 'test_panel',
            'Test Panel': 'test_panel',
            'Test': 'test_panel',
            'Panel': 'test_panel',
            'interpretation': 'interpretation',
            'Interpretation': 'interpretation',
            'Result': 'interpretation',
            'summary': 'summary',
            'Summary': 'summary',
            'clinical_significance': 'clinical_significance',
            'Clinical Significance': 'clinical_significance',
            'Significance': 'clinical_significance',
            'recommendations': 'recommendations',
            'Recommendations': 'recommendations',
            'limitations': 'limitations',
            'Limitations': 'limitations',
            'notes': 'notes',
            'Notes': 'notes',
        }

    def validate_row(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        errors = []

        # Validate sample exists
        sample_id = row_data.get('sample_id')
        if sample_id:
            if not MolecularSample.objects.filter(sample_id=sample_id).exists():
                errors.append(ValidationError(
                    row_number,
                    'sample_id',
                    f"Sample '{sample_id}' not found"
                ))

        # Validate test panel exists
        test_panel = row_data.get('test_panel', '').lower()
        if test_panel and test_panel not in self._test_panels:
            errors.append(ValidationError(
                row_number,
                'test_panel',
                f"Test panel '{test_panel}' not found"
            ))

        # Validate interpretation
        interpretation = row_data.get('interpretation', '').upper()
        valid_interpretations = ['POSITIVE', 'NEGATIVE', 'INDETERMINATE', 'NOT_TESTED', 'INCONCLUSIVE']
        if interpretation and interpretation not in valid_interpretations:
            errors.append(ValidationError(
                row_number,
                'interpretation',
                f"Invalid interpretation '{interpretation}'. Must be one of: {', '.join(valid_interpretations)}"
            ))

        return errors

    def create_object(self, row_data: Dict) -> MolecularResult:
        # Get sample
        sample = MolecularSample.objects.get(sample_id=row_data['sample_id'])

        # Get test panel
        test_panel_name = row_data.get('test_panel', '').lower()
        test_panel = self._test_panels.get(test_panel_name)

        # Build result data
        result_data = {
            'sample': sample,
            'test_panel': test_panel,
            'interpretation': row_data.get('interpretation', 'NOT_TESTED').upper(),
            'summary': row_data.get('summary', ''),
            'clinical_significance': row_data.get('clinical_significance', ''),
            'recommendations': row_data.get('recommendations', ''),
            'limitations': row_data.get('limitations', ''),
            'status': 'PENDING',
        }

        # Set performed by if user available
        if self.user:
            result_data['performed_by'] = self.user
            from django.utils import timezone
            result_data['performed_date'] = timezone.now()

        result = MolecularResult.objects.create(**result_data)
        return result

    def check_duplicate(self, row_data: Dict):
        """Check if result already exists for sample and test."""
        sample_id = row_data.get('sample_id')
        test_panel_name = row_data.get('test_panel', '').lower()

        if not sample_id or not test_panel_name:
            return None

        test_panel = self._test_panels.get(test_panel_name)
        if not test_panel:
            return None

        try:
            sample = MolecularSample.objects.get(sample_id=sample_id)
            return MolecularResult.objects.filter(
                sample=sample,
                test_panel=test_panel
            ).first()
        except MolecularSample.DoesNotExist:
            return None


class PCRResultsImporter(BaseImporter):
    """
    Importer for PCR results with Ct values.

    Expected CSV columns:
    - sample_id (required)
    - gene_target (required)
    - ct_value
    - detection (DETECTED/NOT_DETECTED)
    - quantity
    - quantity_unit
    """

    model = PCRResult

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gene_targets = {gt.symbol.upper(): gt for gt in GeneTarget.objects.all()}

    def get_required_fields(self) -> List[str]:
        return ['sample_id', 'gene_target']

    def get_field_mapping(self) -> Dict[str, str]:
        return {
            'sample_id': 'sample_id',
            'Sample ID': 'sample_id',
            'gene_target': 'gene_target',
            'Gene': 'gene_target',
            'Target': 'gene_target',
            'Gene Target': 'gene_target',
            'ct_value': 'ct_value',
            'Ct': 'ct_value',
            'CT Value': 'ct_value',
            'Ct Value': 'ct_value',
            'detection': 'detection',
            'Detection': 'detection',
            'Result': 'detection',
            'quantity': 'quantity',
            'Quantity': 'quantity',
            'Copies': 'quantity',
            'quantity_unit': 'quantity_unit',
            'Unit': 'quantity_unit',
            'notes': 'notes',
            'Notes': 'notes',
        }

    def validate_row(self, row_data: Dict, row_number: int) -> List[ValidationError]:
        errors = []

        # Validate gene target exists
        gene = row_data.get('gene_target', '').upper()
        if gene and gene not in self._gene_targets:
            errors.append(ValidationError(
                row_number,
                'gene_target',
                f"Gene target '{gene}' not found"
            ))

        # Validate Ct value
        ct_value = row_data.get('ct_value')
        if ct_value:
            try:
                ct = float(ct_value)
                if ct < 0 or ct > 50:
                    errors.append(ValidationError(
                        row_number,
                        'ct_value',
                        f"Ct value {ct} out of range (0-50)"
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    row_number,
                    'ct_value',
                    f"Invalid Ct value '{ct_value}'"
                ))

        # Validate detection
        detection = row_data.get('detection', '').upper()
        if detection and detection not in ['DETECTED', 'NOT_DETECTED', 'INDETERMINATE']:
            errors.append(ValidationError(
                row_number,
                'detection',
                f"Invalid detection status '{detection}'"
            ))

        return errors

    def create_object(self, row_data: Dict) -> PCRResult:
        # Get sample and find/create result
        sample = MolecularSample.objects.get(sample_id=row_data['sample_id'])

        # Get or create molecular result
        result, _ = MolecularResult.objects.get_or_create(
            sample=sample,
            defaults={'status': 'PENDING'}
        )

        # Get gene target
        gene_symbol = row_data.get('gene_target', '').upper()
        gene_target = self._gene_targets.get(gene_symbol)

        # Build PCR result data
        pcr_data = {
            'result': result,
            'gene_target': gene_target,
            'notes': row_data.get('notes', ''),
        }

        # Add Ct value
        ct_value = row_data.get('ct_value')
        if ct_value:
            pcr_data['ct_value'] = float(ct_value)

        # Add detection
        detection = row_data.get('detection', '').upper()
        if detection:
            pcr_data['detection'] = detection

        # Add quantity
        quantity = row_data.get('quantity')
        if quantity:
            pcr_data['quantity'] = float(quantity)
            pcr_data['quantity_unit'] = row_data.get('quantity_unit', 'copies/mL')

        pcr_result = PCRResult.objects.create(**pcr_data)
        return pcr_result

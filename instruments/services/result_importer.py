# instruments/services/result_importer.py

"""
Result Importer Service

Imports test results from instrument messages into the LIMS database.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class ResultImporter:
    """
    Imports test results from instrument messages.

    This service:
    - Parses results from ASTM and HL7 messages
    - Matches results to existing orders/samples
    - Validates result values
    - Creates result records in the database
    - Updates order status
    """

    def __init__(self):
        self.stats = {
            'processed': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
        }

    def import_from_message(self, connection, message) -> Dict[str, Any]:
        """
        Import results from a parsed protocol message.

        Args:
            connection: InstrumentConnection model instance
            message: Parsed message object (ASTMMessage or HL7Message)

        Returns:
            dict: Import results with statistics
        """
        from ..models import MessageLog

        protocol = connection.protocol
        results = []

        try:
            if protocol == 'ASTM':
                results = self._extract_astm_results(message)
            elif protocol == 'HL7':
                results = self._extract_hl7_results(message)
            else:
                logger.warning(f"Unknown protocol: {protocol}")
                return {'success': False, 'error': f'Unknown protocol: {protocol}'}

            # Import each result
            import_results = []
            for result_data in results:
                import_result = self._import_single_result(connection, result_data)
                import_results.append(import_result)
                self.stats['processed'] += 1

                if import_result['success']:
                    self.stats['imported'] += 1
                elif import_result.get('skipped'):
                    self.stats['skipped'] += 1
                else:
                    self.stats['errors'] += 1

            return {
                'success': True,
                'results': import_results,
                'stats': self.stats.copy()
            }

        except Exception as e:
            logger.exception(f"Error importing results: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_message(self, message_log) -> Dict[str, Any]:
        """
        Process a MessageLog record.

        Args:
            message_log: MessageLog model instance

        Returns:
            dict: Processing results
        """
        from ..protocols.astm.parser import ASTMParser
        from ..protocols.hl7.parser import HL7Parser

        try:
            connection = message_log.connection
            raw_message = message_log.raw_message

            # Parse the raw message
            if connection.protocol == 'ASTM':
                parser = ASTMParser()
                parsed = parser.parse_string(raw_message)
            elif connection.protocol == 'HL7':
                parser = HL7Parser()
                parsed = parser.parse_string(raw_message)
            else:
                return {'success': False, 'error': 'Unknown protocol'}

            # Import results
            result = self.import_from_message(connection, parsed)

            # Update message log
            if result['success']:
                message_log.mark_processed(
                    parsed_data=parsed.to_dict() if hasattr(parsed, 'to_dict') else {}
                )
            else:
                message_log.mark_processed(error=result.get('error'))

            return result

        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            message_log.mark_processed(error=str(e))
            return {'success': False, 'error': str(e)}

    def _extract_astm_results(self, message) -> List[Dict[str, Any]]:
        """Extract results from an ASTM message."""
        from ..protocols.astm.parser import ASTMParser

        results = []
        parser = ASTMParser()

        # Get patient info (if available)
        patient_info = {}
        if message.patients:
            patient_record = message.patients[0]
            patient_info = parser.parse_patient_record(patient_record)

        # Get order info and results
        current_order = None
        for order_record in message.orders:
            current_order = parser.parse_order_record(order_record)

        for result_record in message.results:
            result_data = parser.parse_result_record(result_record)

            # Combine with patient and order info
            result_data['patient'] = patient_info
            result_data['order'] = current_order or {}
            result_data['sample_id'] = current_order.get('specimen_id', '') if current_order else ''

            results.append(result_data)

        return results

    def _extract_hl7_results(self, message) -> List[Dict[str, Any]]:
        """Extract results from an HL7 message."""
        from ..protocols.hl7.parser import HL7Parser

        parser = HL7Parser()
        return parser.extract_results(message)

    def _import_single_result(self, connection, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import a single result into the database.

        Args:
            connection: InstrumentConnection model instance
            result_data: Parsed result data

        Returns:
            dict: Import result with success/error info
        """
        try:
            # Extract key identifiers
            sample_id = self._get_sample_id(result_data)
            test_code = self._get_test_code(result_data)
            value = self._get_result_value(result_data)
            units = self._get_units(result_data)

            if not sample_id:
                return {
                    'success': False,
                    'skipped': True,
                    'reason': 'No sample ID found'
                }

            if not test_code:
                return {
                    'success': False,
                    'skipped': True,
                    'reason': 'No test code found'
                }

            # Find the corresponding sample and test order
            sample = self._find_sample(sample_id)
            if not sample:
                logger.warning(f"Sample not found: {sample_id}")
                return {
                    'success': False,
                    'skipped': True,
                    'reason': f'Sample not found: {sample_id}'
                }

            # Find or create result record
            with transaction.atomic():
                result_record = self._create_or_update_result(
                    sample=sample,
                    test_code=test_code,
                    value=value,
                    units=units,
                    result_data=result_data,
                    connection=connection
                )

                if result_record:
                    return {
                        'success': True,
                        'sample_id': sample_id,
                        'test_code': test_code,
                        'value': value,
                        'result_id': result_record.pk if hasattr(result_record, 'pk') else None
                    }

            return {
                'success': False,
                'error': 'Failed to create result record'
            }

        except Exception as e:
            logger.exception(f"Error importing single result: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_sample_id(self, result_data: Dict[str, Any]) -> Optional[str]:
        """Extract sample ID from result data."""
        # Try different locations where sample ID might be
        sample_id = result_data.get('sample_id', '')

        if not sample_id and 'order' in result_data:
            sample_id = result_data['order'].get('specimen_id', '')
            if not sample_id:
                sample_id = result_data['order'].get('placer_order_number', '')
            if not sample_id:
                sample_id = result_data['order'].get('filler_order_number', '')

        if not sample_id and 'result' in result_data:
            # HL7 format
            pass

        return sample_id.strip() if sample_id else None

    def _get_test_code(self, result_data: Dict[str, Any]) -> Optional[str]:
        """Extract test code from result data."""
        # ASTM format
        test_id = result_data.get('test_id', '')
        if test_id:
            # Test ID might be in format "^^^code^text"
            parts = test_id.split('^')
            for part in parts:
                if part.strip():
                    return part.strip()

        # HL7 format
        if 'result' in result_data:
            obs_id = result_data['result'].get('observation_identifier', '')
            if obs_id:
                return obs_id.split('^')[0].strip()

        return None

    def _get_result_value(self, result_data: Dict[str, Any]) -> str:
        """Extract result value from result data."""
        # ASTM format
        value = result_data.get('value', '')

        # HL7 format
        if not value and 'result' in result_data:
            value = result_data['result'].get('observation_value', '')

        return str(value).strip() if value else ''

    def _get_units(self, result_data: Dict[str, Any]) -> str:
        """Extract units from result data."""
        # ASTM format
        units = result_data.get('units', '')

        # HL7 format
        if not units and 'result' in result_data:
            units = result_data['result'].get('units', '')

        return str(units).strip() if units else ''

    def _find_sample(self, sample_id: str):
        """
        Find a sample by ID.

        This method should be customized based on the actual sample model structure.
        """
        # Try to import the Sample model
        try:
            from samples.models import Sample

            # Try different search strategies
            sample = Sample.objects.filter(sample_id=sample_id).first()
            if sample:
                return sample

            # Try barcode
            sample = Sample.objects.filter(barcode=sample_id).first()
            if sample:
                return sample

            # Try accession number
            sample = Sample.objects.filter(accession_number=sample_id).first()
            if sample:
                return sample

        except ImportError:
            logger.warning("Sample model not available")

        return None

    def _create_or_update_result(
        self,
        sample,
        test_code: str,
        value: str,
        units: str,
        result_data: Dict[str, Any],
        connection
    ):
        """
        Create or update a test result record.

        This method should be customized based on the actual result model structure.
        """
        try:
            from results.models import TestResult

            # Parse numeric value if possible
            numeric_value = None
            try:
                numeric_value = Decimal(value)
            except (InvalidOperation, ValueError):
                pass

            # Get abnormal flag
            abnormal_flag = result_data.get('abnormal_flag', '')
            if 'result' in result_data:
                abnormal_flag = result_data['result'].get('abnormal_flags', '')

            # Get result status
            result_status = result_data.get('result_status', 'F')
            if 'result' in result_data:
                result_status = result_data['result'].get('observation_result_status', 'F')

            # Find existing result or create new
            result, created = TestResult.objects.get_or_create(
                sample=sample,
                test_code=test_code,
                defaults={
                    'value': value,
                    'numeric_value': numeric_value,
                    'units': units,
                    'abnormal_flag': abnormal_flag,
                    'status': 'FINAL' if result_status == 'F' else 'PRELIMINARY',
                    'instrument': connection.instrument,
                    'received_at': timezone.now(),
                }
            )

            if not created:
                # Update existing result
                result.value = value
                result.numeric_value = numeric_value
                result.units = units
                result.abnormal_flag = abnormal_flag
                result.status = 'FINAL' if result_status == 'F' else 'PRELIMINARY'
                result.received_at = timezone.now()
                result.save()

            logger.info(
                f"{'Created' if created else 'Updated'} result for "
                f"sample {sample.sample_id}, test {test_code}: {value} {units}"
            )

            return result

        except ImportError:
            logger.warning("TestResult model not available")
            # Log the result data for manual processing
            logger.info(
                f"Result received - Sample: {sample}, Test: {test_code}, "
                f"Value: {value} {units}"
            )
            return None

    def validate_result_value(self, value: str, test_code: str) -> Dict[str, Any]:
        """
        Validate a result value.

        Args:
            value: Result value string
            test_code: Test code for context

        Returns:
            dict: Validation result with 'valid' and 'errors' keys
        """
        errors = []

        if not value:
            errors.append("Empty value")

        # Check for common error indicators
        error_indicators = ['ERROR', 'ERR', 'INVALID', '???', '***']
        for indicator in error_indicators:
            if indicator in value.upper():
                errors.append(f"Error indicator found: {indicator}")

        # Try to parse as numeric if expected
        # This could be enhanced with test-specific validation rules

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def get_import_stats(self) -> Dict[str, int]:
        """Get import statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset import statistics."""
        self.stats = {
            'processed': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
        }

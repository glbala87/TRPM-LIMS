# instruments/services/worklist_exporter.py

"""
Worklist Exporter Service

Exports worklists (sample lists with test orders) to laboratory instruments.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class WorklistExporter:
    """
    Exports worklists to laboratory instruments.

    This service:
    - Builds worklist messages in ASTM or HL7 format
    - Sends worklists to instruments via connection manager
    - Tracks worklist status and acknowledgments
    """

    def __init__(self):
        pass

    def create_worklist(
        self,
        connection,
        sample_ids: List[str],
        created_by=None
    ):
        """
        Create a new worklist export record.

        Args:
            connection: InstrumentConnection model instance
            sample_ids: List of sample IDs to include
            created_by: User creating the worklist

        Returns:
            WorklistExport model instance
        """
        from ..models import WorklistExport

        # Build export data
        samples_data = self._build_samples_data(sample_ids)

        worklist = WorklistExport.objects.create(
            connection=connection,
            samples=sample_ids,
            export_data={'samples': samples_data},
            status='PENDING',
            created_by=created_by
        )

        logger.info(f"Created worklist {worklist.pk} with {len(sample_ids)} samples")
        return worklist

    def send_worklist(self, worklist) -> Dict[str, Any]:
        """
        Send a worklist to the instrument.

        Args:
            worklist: WorklistExport model instance

        Returns:
            dict: Result with success/error info
        """
        from .connection_manager import ConnectionManager

        connection = worklist.connection

        try:
            # Build the message
            message = self._build_worklist_message(worklist)

            if not message:
                return {
                    'success': False,
                    'error': 'Failed to build worklist message'
                }

            # Send via connection manager
            manager = ConnectionManager()
            result = manager.send_message(connection, message)

            if result['success']:
                worklist.status = 'SENT'
                worklist.sent_at = timezone.now()
                worklist.save()

                logger.info(f"Worklist {worklist.pk} sent successfully")
                return {
                    'success': True,
                    'bytes_sent': result.get('bytes_sent', 0)
                }
            else:
                worklist.status = 'ERROR'
                worklist.error_message = result.get('error', 'Unknown error')
                worklist.save()

                return result

        except Exception as e:
            logger.exception(f"Error sending worklist: {e}")
            worklist.status = 'ERROR'
            worklist.error_message = str(e)
            worklist.save()

            return {
                'success': False,
                'error': str(e)
            }

    def _build_samples_data(self, sample_ids: List[str]) -> List[Dict[str, Any]]:
        """Build sample data for the worklist."""
        samples_data = []

        for sample_id in sample_ids:
            sample_info = self._get_sample_info(sample_id)
            if sample_info:
                samples_data.append(sample_info)
            else:
                # Include minimal info for unknown samples
                samples_data.append({
                    'specimen_id': sample_id,
                    'patient_id': '',
                    'patient_name': '',
                    'test_ids': [],
                })

        return samples_data

    def _get_sample_info(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """
        Get sample information for worklist export.

        This method should be customized based on the actual sample model structure.
        """
        try:
            from samples.models import Sample

            sample = Sample.objects.filter(sample_id=sample_id).first()
            if not sample:
                sample = Sample.objects.filter(barcode=sample_id).first()

            if sample:
                # Get patient info
                patient_info = {}
                if hasattr(sample, 'patient') and sample.patient:
                    patient = sample.patient
                    patient_info = {
                        'patient_id': getattr(patient, 'patient_id', ''),
                        'patient_name': getattr(patient, 'name', ''),
                        'family_name': getattr(patient, 'last_name', ''),
                        'given_name': getattr(patient, 'first_name', ''),
                        'date_of_birth': str(getattr(patient, 'date_of_birth', '')),
                        'sex': getattr(patient, 'sex', ''),
                    }

                # Get test orders
                test_ids = []
                if hasattr(sample, 'test_orders'):
                    for order in sample.test_orders.filter(status='PENDING'):
                        if hasattr(order, 'test') and order.test:
                            test_ids.append(order.test.code)

                return {
                    'specimen_id': sample.sample_id,
                    'instrument_specimen_id': getattr(sample, 'barcode', sample.sample_id),
                    'priority': 'R',  # Routine by default
                    'test_ids': test_ids,
                    **patient_info
                }

        except ImportError:
            logger.warning("Sample model not available")

        return None

    def _build_worklist_message(self, worklist) -> Optional[bytes]:
        """Build the worklist message in the appropriate protocol format."""
        connection = worklist.connection
        samples_data = worklist.export_data.get('samples', [])

        if not samples_data:
            logger.warning(f"No samples data for worklist {worklist.pk}")
            return None

        if connection.protocol == 'ASTM':
            return self._build_astm_worklist(samples_data, connection)
        elif connection.protocol == 'HL7':
            return self._build_hl7_worklist(samples_data, connection)
        else:
            logger.error(f"Unknown protocol: {connection.protocol}")
            return None

    def _build_astm_worklist(
        self,
        samples_data: List[Dict[str, Any]],
        connection
    ) -> bytes:
        """Build an ASTM worklist message."""
        from ..protocols.astm.encoder import ASTMEncoder

        encoder = ASTMEncoder()
        records = []

        # Header record
        receiver_id = connection.protocol_config.get('receiver_id', '')
        records.append(encoder.encode_header(
            sender_name='LIMS',
            receiver_id=receiver_id
        ))

        # Patient and Order records for each sample
        for i, sample in enumerate(samples_data, start=1):
            # Patient record
            records.append(encoder.encode_patient(
                sequence_number=i,
                patient_id=sample.get('patient_id', ''),
                laboratory_patient_id=sample.get('patient_id', ''),
                patient_name=sample.get('patient_name', ''),
                birthdate=sample.get('date_of_birth', ''),
                sex=sample.get('sex', ''),
            ))

            # Order record
            records.append(encoder.encode_order(
                sequence_number=1,
                specimen_id=sample.get('specimen_id', ''),
                instrument_specimen_id=sample.get('instrument_specimen_id', ''),
                test_ids=sample.get('test_ids', []),
                priority=sample.get('priority', 'R'),
                action_code='A',  # Add order
            ))

        # Terminator record
        records.append(encoder.encode_terminator())

        return encoder.encode_message(records)

    def _build_hl7_worklist(
        self,
        samples_data: List[Dict[str, Any]],
        connection
    ) -> bytes:
        """Build an HL7 worklist message (ORM^O01)."""
        from ..protocols.hl7.encoder import HL7Encoder

        encoder = HL7Encoder()
        all_messages = []

        receiving_app = connection.protocol_config.get('receiving_application', '')

        for sample in samples_data:
            # Build patient info
            patient_info = {
                'patient_id': sample.get('patient_id', ''),
                'family_name': sample.get('family_name', ''),
                'given_name': sample.get('given_name', ''),
                'date_of_birth': sample.get('date_of_birth', ''),
                'sex': sample.get('sex', ''),
            }

            # Build order info
            order_info = {
                'placer_order_number': sample.get('specimen_id', ''),
                'ordering_provider': '',
            }

            # Build tests
            tests = []
            for test_id in sample.get('test_ids', []):
                tests.append({
                    'test_code': test_id,
                    'test_name': '',
                    'priority': sample.get('priority', 'R'),
                })

            # Build ORM message
            message = encoder.build_orm_message(
                patient_info=patient_info,
                order_info=order_info,
                tests=tests,
                sending_application='LIMS',
                receiving_application=receiving_app
            )

            all_messages.append(message)

        # Combine all messages
        return b''.join(all_messages)

    def acknowledge_worklist(self, worklist, success: bool = True) -> bool:
        """
        Mark a worklist as acknowledged by the instrument.

        Args:
            worklist: WorklistExport model instance
            success: Whether the acknowledgment was positive

        Returns:
            bool: True if update successful
        """
        try:
            worklist.acknowledged_at = timezone.now()

            if success:
                worklist.status = 'ACKNOWLEDGED'
            else:
                worklist.status = 'ERROR'

            worklist.save()
            logger.info(f"Worklist {worklist.pk} acknowledged (success={success})")
            return True

        except Exception as e:
            logger.error(f"Error acknowledging worklist: {e}")
            return False

    def complete_worklist(self, worklist) -> bool:
        """
        Mark a worklist as completed (all results received).

        Args:
            worklist: WorklistExport model instance

        Returns:
            bool: True if update successful
        """
        try:
            worklist.completed_at = timezone.now()
            worklist.status = 'COMPLETED'
            worklist.save()

            logger.info(f"Worklist {worklist.pk} completed")
            return True

        except Exception as e:
            logger.error(f"Error completing worklist: {e}")
            return False

    def get_pending_worklists(self, connection=None) -> List:
        """
        Get all pending worklists.

        Args:
            connection: Optional connection to filter by

        Returns:
            QuerySet of WorklistExport records
        """
        from ..models import WorklistExport

        queryset = WorklistExport.objects.filter(
            status__in=['PENDING', 'SENT', 'ACKNOWLEDGED']
        )

        if connection:
            queryset = queryset.filter(connection=connection)

        return queryset.select_related('connection', 'connection__instrument')

    def retry_failed_worklist(self, worklist) -> Dict[str, Any]:
        """
        Retry sending a failed worklist.

        Args:
            worklist: WorklistExport model instance

        Returns:
            dict: Result of send attempt
        """
        if worklist.status != 'ERROR':
            return {
                'success': False,
                'error': f'Worklist status is {worklist.status}, not ERROR'
            }

        # Reset status and clear error
        worklist.status = 'PENDING'
        worklist.error_message = ''
        worklist.save()

        return self.send_worklist(worklist)

    def cancel_worklist(self, worklist, reason: str = '') -> bool:
        """
        Cancel a pending worklist.

        Args:
            worklist: WorklistExport model instance
            reason: Cancellation reason

        Returns:
            bool: True if cancelled successfully
        """
        if worklist.status not in ['PENDING', 'ERROR']:
            logger.warning(f"Cannot cancel worklist in status {worklist.status}")
            return False

        try:
            # If worklist was sent, we might need to send a cancel message
            if worklist.status == 'SENT':
                # Build and send cancel message
                # This depends on instrument capabilities
                pass

            worklist.status = 'ERROR'
            worklist.error_message = f'Cancelled: {reason}' if reason else 'Cancelled'
            worklist.save()

            logger.info(f"Worklist {worklist.pk} cancelled")
            return True

        except Exception as e:
            logger.error(f"Error cancelling worklist: {e}")
            return False

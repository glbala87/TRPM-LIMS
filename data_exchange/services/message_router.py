# data_exchange/services/message_router.py
"""
Message routing service for HL7/FHIR message dispatch.

Handles message creation, logging, transmission, and retry logic.
"""

import logging
import socket
import requests
from typing import Optional
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from data_exchange.models import ExternalSystem, MessageLog
from .hl7_service import HL7Service, HL7ServiceError
from .fhir_service import FHIRService, FHIRServiceError

logger = logging.getLogger(__name__)


class MessageRouterError(Exception):
    """Exception raised for message routing errors."""
    pass


class MessageRouter:
    """
    Central service for routing messages to external systems.

    Supports:
    - HL7 v2.x via MLLP
    - FHIR R4 via HTTP
    - Message logging and retry
    """

    # MLLP framing characters
    MLLP_START = b'\x0b'  # VT (Vertical Tab)
    MLLP_END = b'\x1c\x0d'  # FS + CR

    def __init__(self, external_system: ExternalSystem):
        """
        Initialize message router.

        Args:
            external_system: ExternalSystem configuration
        """
        self.system = external_system
        self.hl7_service = HL7Service(external_system)
        self.fhir_service = FHIRService(external_system.fhir_base_url or None)

    def send_result(self, molecular_result, linked_object=None) -> MessageLog:
        """
        Send a molecular result to the external system.

        Automatically determines the appropriate message format
        based on the external system configuration.

        Args:
            molecular_result: MolecularResult instance
            linked_object: Optional object to link in message log

        Returns:
            MessageLog instance
        """
        if self.system.protocol == 'HL7V2':
            return self.send_hl7_result(molecular_result, linked_object)
        elif self.system.protocol in ['FHIR_R4', 'FHIR_STU3']:
            return self.send_fhir_result(molecular_result, linked_object)
        else:
            raise MessageRouterError(f"Unsupported protocol: {self.system.protocol}")

    def send_hl7_result(
        self,
        molecular_result,
        linked_object=None
    ) -> MessageLog:
        """
        Send an HL7 ORU^R01 message for a molecular result.

        Args:
            molecular_result: MolecularResult instance
            linked_object: Optional object to link in message log

        Returns:
            MessageLog instance
        """
        # Generate HL7 message
        message = self.hl7_service.generate_oru_r01(molecular_result)

        # Extract message control ID from MSH-10
        segments = message.split('\r')
        msh_fields = segments[0].split('|')
        message_id = msh_fields[9] if len(msh_fields) > 9 else str(molecular_result.id)

        # Create message log
        log = self._create_message_log(
            message_id=message_id,
            message_type='ORU_R01',
            direction='OUTBOUND',
            raw_message=message,
            linked_object=linked_object or molecular_result
        )

        # Send message
        try:
            if self.system.transport == 'MLLP':
                response = self._send_mllp(message)
            elif self.system.transport == 'HTTP':
                response = self._send_http_hl7(message)
            else:
                raise MessageRouterError(f"Unsupported transport: {self.system.transport}")

            # Parse acknowledgment
            ack = self.hl7_service.parse_ack(response)

            log.acknowledgment_code = ack['ack_code']
            log.acknowledgment_message = ack['text_message']

            if ack['is_valid']:
                log.status = 'ACKNOWLEDGED'
                log.acknowledged_at = timezone.now()
            else:
                log.status = 'REJECTED'
                log.status_message = ack.get('error_message', 'Message rejected')

            log.save()

            # Update system connection status
            self._update_system_status(success=True)

        except Exception as e:
            self._handle_send_error(log, e)

        return log

    def send_fhir_result(
        self,
        molecular_result,
        linked_object=None
    ) -> MessageLog:
        """
        Send a FHIR DiagnosticReport for a molecular result.

        Args:
            molecular_result: MolecularResult instance
            linked_object: Optional object to link in message log

        Returns:
            MessageLog instance
        """
        # Generate FHIR resource
        resource = self.fhir_service.generate_diagnostic_report(molecular_result)
        message = self.fhir_service.to_json(resource)

        # Create message log
        log = self._create_message_log(
            message_id=resource.get('id', str(molecular_result.id)),
            message_type='FHIR_DIAGNOSTIC_REPORT',
            direction='OUTBOUND',
            raw_message=message,
            parsed_message=resource,
            linked_object=linked_object or molecular_result
        )

        # Send resource
        try:
            response = self._send_fhir_resource(resource)

            if response.status_code in [200, 201]:
                log.status = 'ACKNOWLEDGED'
                log.acknowledged_at = timezone.now()

                # Extract ID from response if created
                try:
                    response_data = response.json()
                    log.acknowledgment_id = response_data.get('id', '')
                except Exception:
                    pass
            else:
                log.status = 'REJECTED'
                log.status_message = f"HTTP {response.status_code}: {response.text[:500]}"

            log.sent_at = timezone.now()
            log.save()

            self._update_system_status(success=response.status_code in [200, 201])

        except Exception as e:
            self._handle_send_error(log, e)

        return log

    def _create_message_log(
        self,
        message_id: str,
        message_type: str,
        direction: str,
        raw_message: str,
        parsed_message: dict = None,
        linked_object=None
    ) -> MessageLog:
        """Create a MessageLog entry."""
        log = MessageLog(
            external_system=self.system,
            direction=direction,
            message_id=message_id,
            message_type=message_type,
            raw_message=raw_message,
            parsed_message=parsed_message or {},
            status='SENDING',
        )

        # Link to LIMS object
        if linked_object:
            log.content_type = ContentType.objects.get_for_model(linked_object)
            log.object_id = linked_object.pk

        log.save()
        return log

    def _send_mllp(self, message: str) -> str:
        """
        Send HL7 message via MLLP protocol.

        Args:
            message: HL7 message string

        Returns:
            Response message string (ACK)
        """
        # Frame message with MLLP characters
        framed = self.MLLP_START + message.encode(self.system.message_encoding) + self.MLLP_END

        # Connect and send
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.system.timeout_seconds)
            sock.connect((self.system.host, self.system.port))
            sock.sendall(framed)

            # Receive response
            response = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                # Check for end of MLLP message
                if self.MLLP_END in response:
                    break

        # Remove MLLP framing
        response = response.strip(self.MLLP_START).strip(self.MLLP_END)
        return response.decode(self.system.message_encoding)

    def _send_http_hl7(self, message: str) -> str:
        """
        Send HL7 message via HTTP.

        Args:
            message: HL7 message string

        Returns:
            Response message string
        """
        url = f"http://{self.system.host}:{self.system.port}{self.system.path}"

        headers = {
            'Content-Type': 'application/hl7-v2',
        }

        # Add authentication if configured
        auth = None
        if self.system.credentials:
            username = self.system.credentials.get('username')
            password = self.system.credentials.get('password')
            if username and password:
                auth = (username, password)

        response = requests.post(
            url,
            data=message.encode(self.system.message_encoding),
            headers=headers,
            auth=auth,
            timeout=self.system.timeout_seconds
        )
        response.raise_for_status()

        return response.text

    def _send_fhir_resource(self, resource: dict) -> requests.Response:
        """
        Send FHIR resource via HTTP.

        Args:
            resource: FHIR resource dictionary

        Returns:
            HTTP Response
        """
        base_url = self.system.fhir_base_url or f"http://{self.system.host}:{self.system.port}"
        resource_type = resource.get('resourceType')
        resource_id = resource.get('id')

        if resource_id:
            url = f"{base_url}/{resource_type}/{resource_id}"
            method = 'PUT'
        else:
            url = f"{base_url}/{resource_type}"
            method = 'POST'

        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
        }

        # Add OAuth2 token if configured
        if self.system.credentials:
            token = self.system.credentials.get('access_token')
            if token:
                headers['Authorization'] = f'Bearer {token}'

        response = requests.request(
            method,
            url,
            json=resource,
            headers=headers,
            timeout=self.system.timeout_seconds
        )

        return response

    def _handle_send_error(self, log: MessageLog, error: Exception):
        """Handle send error and update log."""
        logger.error(f"Message send failed: {error}")

        log.status = 'FAILED'
        log.status_message = str(error)[:1000]
        log.retry_count += 1

        # Schedule retry if under limit
        if log.retry_count < self.system.retry_attempts:
            log.status = 'RETRYING'
            log.next_retry_at = timezone.now() + timedelta(
                seconds=self.system.retry_delay_seconds
            )

        log.save()
        self._update_system_status(success=False, error=str(error))

    def _update_system_status(self, success: bool, error: str = None):
        """Update external system status."""
        self.system.last_connection_at = timezone.now()

        if success:
            self.system.status = 'ACTIVE'
            self.system.last_error = ''
        else:
            self.system.status = 'ERROR'
            self.system.last_error = error or 'Connection failed'

        self.system.save(update_fields=['last_connection_at', 'status', 'last_error'])

    def retry_failed_messages(self) -> int:
        """
        Retry failed messages that are due for retry.

        Returns:
            Number of messages retried
        """
        messages = MessageLog.objects.filter(
            external_system=self.system,
            status='RETRYING',
            next_retry_at__lte=timezone.now()
        )

        count = 0
        for log in messages:
            try:
                self._retry_message(log)
                count += 1
            except Exception as e:
                logger.error(f"Retry failed for message {log.id}: {e}")

        return count

    def _retry_message(self, log: MessageLog):
        """Retry a specific message."""
        log.status = 'SENDING'
        log.save(update_fields=['status'])

        if log.message_type == 'ORU_R01':
            # Resend HL7 message
            try:
                if self.system.transport == 'MLLP':
                    response = self._send_mllp(log.raw_message)
                else:
                    response = self._send_http_hl7(log.raw_message)

                ack = self.hl7_service.parse_ack(response)

                if ack['is_valid']:
                    log.status = 'ACKNOWLEDGED'
                    log.acknowledged_at = timezone.now()
                else:
                    log.status = 'REJECTED'

                log.acknowledgment_code = ack['ack_code']
                log.save()

            except Exception as e:
                self._handle_send_error(log, e)

        elif log.message_type.startswith('FHIR_'):
            # Resend FHIR resource
            try:
                import json
                resource = json.loads(log.raw_message)
                response = self._send_fhir_resource(resource)

                if response.status_code in [200, 201]:
                    log.status = 'ACKNOWLEDGED'
                    log.acknowledged_at = timezone.now()
                else:
                    log.status = 'REJECTED'
                    log.status_message = f"HTTP {response.status_code}"

                log.save()

            except Exception as e:
                self._handle_send_error(log, e)

    def get_pending_messages(self) -> list:
        """Get list of pending messages for this system."""
        return list(MessageLog.objects.filter(
            external_system=self.system,
            status__in=['PENDING', 'SENDING', 'RETRYING']
        ).order_by('created_at'))

    def get_message_stats(self) -> dict:
        """Get message statistics for this system."""
        from django.db.models import Count

        stats = MessageLog.objects.filter(
            external_system=self.system
        ).values('status').annotate(count=Count('id'))

        return {s['status']: s['count'] for s in stats}

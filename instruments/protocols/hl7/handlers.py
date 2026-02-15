# instruments/protocols/hl7/handlers.py

"""
HL7 Protocol Message Handlers

Handles the protocol-level communication for HL7 messages.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .parser import HL7Parser, HL7Message
from .encoder import HL7Encoder, VT, FS, CR

logger = logging.getLogger(__name__)


@dataclass
class HL7Session:
    """Represents an HL7 communication session."""
    messages_received: List[HL7Message] = field(default_factory=list)
    messages_sent: List[bytes] = field(default_factory=list)
    last_activity: datetime = None
    last_received_control_id: str = ''

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()


class HL7MessageHandler:
    """
    Handles HL7 protocol communication.

    This class manages HL7 message parsing, encoding, and acknowledgment
    generation. It supports MLLP framing and provides callbacks for
    processing received messages.
    """

    def __init__(
        self,
        on_message_received: Optional[Callable[[HL7Message], None]] = None,
        on_message_sent: Optional[Callable[[bytes], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        sending_application: str = 'LIMS',
        sending_facility: str = '',
        auto_acknowledge: bool = True,
    ):
        self.parser = HL7Parser()
        self.encoder = HL7Encoder()
        self.session = HL7Session()

        # Configuration
        self.sending_application = sending_application
        self.sending_facility = sending_facility
        self.auto_acknowledge = auto_acknowledge

        # Callbacks
        self.on_message_received = on_message_received
        self.on_message_sent = on_message_sent
        self.on_error = on_error

        # Buffer for partial messages (MLLP framing)
        self.receive_buffer = b''

    def reset(self):
        """Reset the handler state."""
        self.session = HL7Session()
        self.receive_buffer = b''

    def handle_received_data(self, data: bytes) -> Optional[bytes]:
        """
        Handle received data from instrument.

        Returns bytes to send back (acknowledgment), or None if no response needed.
        """
        self.session.last_activity = datetime.now()

        if not data:
            return None

        logger.debug(f"Received data: {data!r}")

        # Add to buffer
        self.receive_buffer += data

        # Try to extract complete messages
        responses = []
        while True:
            message, remaining = self._extract_message()
            if message is None:
                break

            self.receive_buffer = remaining

            try:
                parsed = self.parser.parse(message)
                self.session.messages_received.append(parsed)
                self.session.last_received_control_id = parsed.control_id

                logger.info(
                    f"Received HL7 message: {parsed.message_type}^{parsed.trigger_event} "
                    f"(Control ID: {parsed.control_id})"
                )

                # Call the callback
                if self.on_message_received:
                    self.on_message_received(parsed)

                # Generate acknowledgment if configured
                if self.auto_acknowledge:
                    ack = self._generate_ack(parsed)
                    responses.append(ack)

            except Exception as e:
                logger.error(f"Error parsing HL7 message: {e}")
                if self.on_error:
                    self.on_error(f"Parse error: {e}")

                # Generate negative acknowledgment
                if self.auto_acknowledge:
                    nak = self._generate_nak(str(e))
                    responses.append(nak)

        if responses:
            return b''.join(responses)
        return None

    def _extract_message(self) -> tuple:
        """Extract a complete MLLP-framed message from the buffer."""
        # Look for start of message (VT)
        start = self.receive_buffer.find(VT)
        if start == -1:
            return None, self.receive_buffer

        # Look for end of message (FS CR)
        end = self.receive_buffer.find(FS + CR, start)
        if end == -1:
            # Also check for just FS
            end = self.receive_buffer.find(FS, start)
            if end == -1:
                return None, self.receive_buffer
            end_offset = 1
        else:
            end_offset = 2

        # Extract the message (including framing)
        message = self.receive_buffer[start:end + end_offset]
        remaining = self.receive_buffer[end + end_offset:]

        return message, remaining

    def _generate_ack(
        self,
        original_message: HL7Message,
        ack_code: str = 'AA',
        text_message: str = '',
    ) -> bytes:
        """Generate an acknowledgment message."""
        return self.encoder.build_ack_message(
            original_control_id=original_message.control_id,
            acknowledgment_code=ack_code,
            text_message=text_message,
            sending_application=self.sending_application,
            receiving_application=original_message.msh.get_field(3) if original_message.msh else '',
        )

    def _generate_nak(self, error_message: str) -> bytes:
        """Generate a negative acknowledgment message."""
        return self.encoder.build_ack_message(
            original_control_id=self.session.last_received_control_id,
            acknowledgment_code='AE',
            text_message=error_message,
            sending_application=self.sending_application,
        )

    def send_message(self, message: bytes) -> bytes:
        """
        Send a message to the instrument.

        Returns the bytes to transmit.
        """
        self.session.messages_sent.append(message)
        self.session.last_activity = datetime.now()

        if self.on_message_sent:
            self.on_message_sent(message)

        return message

    def build_order_message(
        self,
        patient_info: Dict[str, Any],
        order_info: Dict[str, Any],
        tests: List[Dict[str, Any]],
        receiving_application: str = '',
    ) -> bytes:
        """Build and prepare an order message for sending."""
        return self.encoder.build_orm_message(
            patient_info=patient_info,
            order_info=order_info,
            tests=tests,
            sending_application=self.sending_application,
            receiving_application=receiving_application,
        )

    def build_result_message(
        self,
        patient_info: Dict[str, Any],
        order_info: Dict[str, Any],
        results: List[Dict[str, Any]],
        receiving_application: str = '',
    ) -> bytes:
        """Build and prepare a result message for sending."""
        return self.encoder.build_oru_message(
            patient_info=patient_info,
            order_info=order_info,
            results=results,
            sending_application=self.sending_application,
            receiving_application=receiving_application,
        )

    def extract_results_from_message(self, message: HL7Message) -> List[Dict[str, Any]]:
        """Extract test results from an ORU message."""
        return self.parser.extract_results(message)

    def is_result_message(self, message: HL7Message) -> bool:
        """Check if the message is a result message (ORU)."""
        return message.message_type == 'ORU'

    def is_order_message(self, message: HL7Message) -> bool:
        """Check if the message is an order message (ORM)."""
        return message.message_type == 'ORM'

    def is_query_message(self, message: HL7Message) -> bool:
        """Check if the message is a query message (QRY)."""
        return message.message_type in ('QRY', 'QBP')

    def get_sample_id_from_message(self, message: HL7Message) -> Optional[str]:
        """Extract the primary sample/specimen ID from a message."""
        # Try OBR segment first (Filler Order Number or Placer Order Number)
        obr = message.get_segment('OBR')
        if obr:
            filler_order = obr.get_field(3)
            if filler_order:
                return filler_order
            placer_order = obr.get_field(2)
            if placer_order:
                return placer_order

        # Try ORC segment
        orc = message.get_segment('ORC')
        if orc:
            filler_order = orc.get_field(3)
            if filler_order:
                return filler_order
            placer_order = orc.get_field(2)
            if placer_order:
                return placer_order

        return None

    def get_patient_id_from_message(self, message: HL7Message) -> Optional[str]:
        """Extract the patient ID from a message."""
        pid = message.pid
        if pid:
            # PID-3: Patient Identifier List
            patient_id = pid.get_field(3)
            if patient_id:
                return patient_id

            # PID-2: Patient ID
            patient_id = pid.get_field(2)
            if patient_id:
                return patient_id

        return None

    def validate_message(self, message: HL7Message) -> Dict[str, Any]:
        """
        Validate an HL7 message.

        Returns a dictionary with validation results.
        """
        errors = []
        warnings = []

        # Check for required MSH segment
        if not message.msh:
            errors.append("Missing MSH segment")
        else:
            # Check required MSH fields
            if not message.control_id:
                errors.append("Missing Message Control ID (MSH-10)")
            if not message.message_type:
                errors.append("Missing Message Type (MSH-9)")
            if not message.version:
                warnings.append("Missing Version ID (MSH-12)")

        # For ORU messages, check for required segments
        if message.message_type == 'ORU':
            if not message.get_segment('OBR'):
                warnings.append("ORU message missing OBR segment")
            if not message.get_all_segments('OBX'):
                warnings.append("ORU message missing OBX segments")

        # For ORM messages, check for required segments
        if message.message_type == 'ORM':
            if not message.get_segment('ORC'):
                warnings.append("ORM message missing ORC segment")
            if not message.get_segment('OBR'):
                warnings.append("ORM message missing OBR segment")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
        }

# instruments/protocols/astm/handlers.py

"""
ASTM Protocol Message Handlers

Handles the protocol-level communication for ASTM messages.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .parser import ASTMParser, ASTMMessage, ASTMRecord
from .encoder import ASTMEncoder, ENQ, EOT, ACK, NAK, STX, ETX

logger = logging.getLogger(__name__)


class ASTMState(Enum):
    """ASTM protocol state machine states."""
    IDLE = 'idle'
    RECEIVING = 'receiving'
    SENDING = 'sending'
    WAIT_ACK = 'wait_ack'
    ERROR = 'error'


@dataclass
class ASTMSession:
    """Represents an ASTM communication session."""
    state: ASTMState = ASTMState.IDLE
    frames_received: List[bytes] = None
    frames_to_send: List[bytes] = None
    current_frame_index: int = 0
    retry_count: int = 0
    max_retries: int = 6
    last_activity: datetime = None

    def __post_init__(self):
        if self.frames_received is None:
            self.frames_received = []
        if self.frames_to_send is None:
            self.frames_to_send = []
        if self.last_activity is None:
            self.last_activity = datetime.now()


class ASTMMessageHandler:
    """
    Handles ASTM protocol communication.

    This class manages the state machine for ASTM bidirectional communication,
    handling ENQ/ACK/NAK sequences, frame-by-frame transmission, and
    message assembly.
    """

    def __init__(
        self,
        on_message_received: Optional[Callable[[ASTMMessage], None]] = None,
        on_message_sent: Optional[Callable[[bytes], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.parser = ASTMParser()
        self.encoder = ASTMEncoder()
        self.session = ASTMSession()

        # Callbacks
        self.on_message_received = on_message_received
        self.on_message_sent = on_message_sent
        self.on_error = on_error

        # Buffer for partial data
        self.receive_buffer = b''

    def reset(self):
        """Reset the handler state."""
        self.session = ASTMSession()
        self.receive_buffer = b''

    def handle_received_data(self, data: bytes) -> Optional[bytes]:
        """
        Handle received data from instrument.

        Returns bytes to send back to the instrument, or None if no response needed.
        """
        self.session.last_activity = datetime.now()

        if not data:
            return None

        logger.debug(f"Received data: {data!r}")

        # Handle ENQ - instrument wants to send
        if data == ENQ:
            return self._handle_enq()

        # Handle EOT - end of transmission
        if data == EOT:
            return self._handle_eot()

        # Handle ACK - our frame was acknowledged
        if data == ACK:
            return self._handle_ack()

        # Handle NAK - our frame was rejected
        if data == NAK:
            return self._handle_nak()

        # Otherwise, it's frame data
        return self._handle_frame_data(data)

    def _handle_enq(self) -> bytes:
        """Handle ENQ from instrument."""
        if self.session.state == ASTMState.IDLE:
            logger.debug("Received ENQ, sending ACK")
            self.session.state = ASTMState.RECEIVING
            self.session.frames_received = []
            return ACK
        else:
            # Busy, send NAK
            logger.debug("Received ENQ while busy, sending NAK")
            return NAK

    def _handle_eot(self) -> Optional[bytes]:
        """Handle EOT from instrument."""
        if self.session.state == ASTMState.RECEIVING:
            logger.debug("Received EOT, processing message")
            self._process_received_message()
            self.session.state = ASTMState.IDLE
        else:
            logger.debug("Received EOT in unexpected state")
            self.session.state = ASTMState.IDLE

        return None

    def _handle_ack(self) -> Optional[bytes]:
        """Handle ACK from instrument."""
        if self.session.state == ASTMState.WAIT_ACK:
            self.session.retry_count = 0
            self.session.current_frame_index += 1

            # Send next frame if available
            if self.session.current_frame_index < len(self.session.frames_to_send):
                frame = self.session.frames_to_send[self.session.current_frame_index]
                self.session.state = ASTMState.WAIT_ACK
                return frame
            else:
                # All frames sent, send EOT
                self.session.state = ASTMState.IDLE
                if self.on_message_sent:
                    self.on_message_sent(b''.join(self.session.frames_to_send))
                return EOT

        return None

    def _handle_nak(self) -> Optional[bytes]:
        """Handle NAK from instrument."""
        if self.session.state == ASTMState.WAIT_ACK:
            self.session.retry_count += 1

            if self.session.retry_count > self.session.max_retries:
                logger.error("Max retries exceeded")
                self.session.state = ASTMState.ERROR
                if self.on_error:
                    self.on_error("Max retries exceeded")
                return EOT

            # Resend current frame
            if self.session.current_frame_index < len(self.session.frames_to_send):
                frame = self.session.frames_to_send[self.session.current_frame_index]
                return frame

        return None

    def _handle_frame_data(self, data: bytes) -> bytes:
        """Handle frame data from instrument."""
        self.receive_buffer += data

        # Check for complete frame(s)
        response = b''
        while self._process_buffer():
            response = ACK

        return response if response else ACK

    def _process_buffer(self) -> bool:
        """Process the receive buffer for complete frames."""
        # Look for STX...ETX/ETB pattern
        stx_pos = self.receive_buffer.find(STX)
        if stx_pos == -1:
            return False

        # Look for ETX or ETB
        etx_pos = self.receive_buffer.find(ETX, stx_pos)
        etb_pos = self.receive_buffer.find(b'\x17', stx_pos)

        end_pos = -1
        if etx_pos != -1 and etb_pos != -1:
            end_pos = min(etx_pos, etb_pos)
        elif etx_pos != -1:
            end_pos = etx_pos
        elif etb_pos != -1:
            end_pos = etb_pos

        if end_pos == -1:
            return False

        # Check for checksum (2 bytes) and CR LF
        frame_end = end_pos + 5  # ETX/ETB + 2 checksum + CR + LF

        if len(self.receive_buffer) < frame_end:
            return False

        # Extract complete frame
        frame = self.receive_buffer[stx_pos:frame_end]
        self.session.frames_received.append(frame)

        # Remove processed data from buffer
        self.receive_buffer = self.receive_buffer[frame_end:]

        return True

    def _process_received_message(self):
        """Process all received frames into a message."""
        if not self.session.frames_received:
            return

        # Combine all frames
        combined = b''.join(self.session.frames_received)

        try:
            message = self.parser.parse(combined)

            if self.on_message_received:
                self.on_message_received(message)

            logger.info(
                f"Processed ASTM message with {len(message.results)} results, "
                f"{len(message.orders)} orders, {len(message.patients)} patients"
            )
        except Exception as e:
            logger.error(f"Error parsing ASTM message: {e}")
            if self.on_error:
                self.on_error(f"Parse error: {e}")

    def send_message(self, records: List[str]) -> bytes:
        """
        Prepare a message for sending.

        Returns the ENQ byte to initiate transmission.
        The actual frames will be sent after receiving ACK.
        """
        # Encode all records into frames
        self.encoder.reset_frame_number()
        frames = []

        for i, record in enumerate(records):
            is_last = (i == len(records) - 1)
            frame = self.encoder.encode_frame(record, is_last)
            frames.append(frame)

        self.session.frames_to_send = frames
        self.session.current_frame_index = 0
        self.session.state = ASTMState.SENDING
        self.session.retry_count = 0

        return ENQ

    def get_first_frame(self) -> Optional[bytes]:
        """Get the first frame to send after ENQ is acknowledged."""
        if self.session.frames_to_send:
            self.session.state = ASTMState.WAIT_ACK
            return self.session.frames_to_send[0]
        return None

    def build_query_request(
        self,
        sample_ids: List[str],
        test_id: str = '',
    ) -> List[str]:
        """Build records for a sample query request."""
        records = []

        # Header
        records.append(self.encoder.encode_header(sender_name='LIMS'))

        # Query record for each sample
        for i, sample_id in enumerate(sample_ids, start=1):
            records.append(self.encoder.encode_query(
                sequence_number=i,
                starting_range_id=sample_id,
                test_id=test_id,
                request_type='S',
            ))

        # Terminator
        records.append(self.encoder.encode_terminator())

        return records

    def build_worklist_download(self, samples: List[Dict[str, Any]]) -> List[str]:
        """Build records for a worklist download to instrument."""
        records = []

        # Header
        records.append(self.encoder.encode_header(sender_name='LIMS'))

        # Patient and Order records for each sample
        for i, sample in enumerate(samples, start=1):
            # Patient record
            records.append(self.encoder.encode_patient(
                sequence_number=i,
                patient_id=sample.get('patient_id', ''),
                patient_name=sample.get('patient_name', ''),
                birthdate=sample.get('birthdate', ''),
                sex=sample.get('sex', ''),
            ))

            # Order record
            records.append(self.encoder.encode_order(
                sequence_number=1,
                specimen_id=sample.get('specimen_id', ''),
                test_ids=sample.get('test_ids', []),
                priority=sample.get('priority', 'R'),
            ))

        # Terminator
        records.append(self.encoder.encode_terminator())

        return records

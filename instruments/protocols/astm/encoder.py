# instruments/protocols/astm/encoder.py

"""
ASTM E1381/E1394 Protocol Encoder

Encodes messages for sending to laboratory instruments.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ASTM Control Characters
STX = b'\x02'  # Start of text
ETX = b'\x03'  # End of text
ETB = b'\x17'  # End of transmission block
EOT = b'\x04'  # End of transmission
ENQ = b'\x05'  # Enquiry
ACK = b'\x06'  # Acknowledge
NAK = b'\x15'  # Negative acknowledge
CR = b'\x0D'   # Carriage return
LF = b'\x0A'   # Line feed

# Field delimiters
FIELD_DELIMITER = '|'
REPEAT_DELIMITER = '\\'
COMPONENT_DELIMITER = '^'
ESCAPE_DELIMITER = '&'


class ASTMEncoder:
    """Encoder for ASTM E1381/E1394 protocol messages."""

    def __init__(self, encoding: str = 'latin-1'):
        self.encoding = encoding
        self.field_delimiter = FIELD_DELIMITER
        self.repeat_delimiter = REPEAT_DELIMITER
        self.component_delimiter = COMPONENT_DELIMITER
        self.escape_delimiter = ESCAPE_DELIMITER
        self.frame_number = 0
        self.max_frame_size = 240  # Maximum data size per frame

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for frame data."""
        checksum = sum(data) % 256
        return f'{checksum:02X}'

    def _next_frame_number(self) -> int:
        """Get the next frame number (1-7 cycling)."""
        self.frame_number = (self.frame_number % 7) + 1
        return self.frame_number

    def reset_frame_number(self):
        """Reset frame number counter."""
        self.frame_number = 0

    def encode_frame(self, record_data: str, is_last: bool = True) -> bytes:
        """Encode a single record into an ASTM frame."""
        frame_num = self._next_frame_number()
        end_char = ETX if is_last else ETB

        # Build frame content
        frame_content = f'{frame_num}{record_data}'.encode(self.encoding)
        frame_with_end = frame_content + end_char

        # Calculate checksum
        checksum = self._calculate_checksum(frame_with_end)

        # Build complete frame
        frame = STX + frame_with_end + checksum.encode('ascii') + CR + LF

        return frame

    def encode_message(self, records: List[str]) -> bytes:
        """Encode multiple records into a complete ASTM message."""
        self.reset_frame_number()
        message = b''

        for i, record in enumerate(records):
            is_last = (i == len(records) - 1)
            message += self.encode_frame(record, is_last)

        return message

    def encode_header(
        self,
        sender_name: str = '',
        sender_address: str = '',
        receiver_id: str = '',
        message_datetime: Optional[datetime] = None,
        message_id: str = '',
        processing_id: str = 'P',
        version: str = 'E1394-97',
    ) -> str:
        """Encode a header record."""
        if message_datetime is None:
            message_datetime = datetime.now()

        datetime_str = message_datetime.strftime('%Y%m%d%H%M%S')

        fields = [
            'H',  # Record type
            f'{self.repeat_delimiter}{self.component_delimiter}{self.escape_delimiter}',
            '',  # Message control ID
            '',  # Access password
            sender_name,  # Sender name/ID
            sender_address,  # Sender address
            '',  # Reserved
            '',  # Sender telephone
            '',  # Characteristics of sender
            receiver_id,  # Receiver ID
            '',  # Comments
            processing_id,  # Processing ID (P=Production, T=Training, D=Debug)
            version,  # Version
            datetime_str,  # Message date/time
        ]

        return self.field_delimiter.join(fields)

    def encode_patient(
        self,
        sequence_number: int = 1,
        patient_id: str = '',
        laboratory_patient_id: str = '',
        patient_name: str = '',
        birthdate: str = '',
        sex: str = '',
        race: str = '',
        address: str = '',
        telephone: str = '',
        physician_id: str = '',
    ) -> str:
        """Encode a patient record."""
        fields = [
            f'P{sequence_number}',
            patient_id,
            laboratory_patient_id,
            '',  # Third patient ID
            patient_name,
            '',  # Mother's maiden name
            birthdate,
            sex,
            race,
            address,
            telephone,
            physician_id,
        ]

        return self.field_delimiter.join(fields)

    def encode_order(
        self,
        sequence_number: int = 1,
        specimen_id: str = '',
        instrument_specimen_id: str = '',
        test_ids: List[str] = None,
        priority: str = 'R',  # R=Routine, S=Stat
        requested_datetime: Optional[datetime] = None,
        specimen_collection_datetime: Optional[datetime] = None,
        action_code: str = 'A',  # A=Add, C=Cancel
        specimen_descriptor: str = '',
        ordering_physician: str = '',
        report_type: str = 'O',  # O=Order, F=Final
    ) -> str:
        """Encode an order record."""
        if test_ids is None:
            test_ids = []

        # Format test IDs
        test_id_str = self.repeat_delimiter.join(test_ids) if test_ids else ''

        # Format datetimes
        requested_str = requested_datetime.strftime('%Y%m%d%H%M%S') if requested_datetime else ''
        collection_str = specimen_collection_datetime.strftime('%Y%m%d%H%M%S') if specimen_collection_datetime else ''

        fields = [
            f'O{sequence_number}',
            specimen_id,
            instrument_specimen_id,
            test_id_str,
            priority,
            requested_str,
            collection_str,
            '',  # Collection end time
            '',  # Collection volume
            '',  # Collector ID
            action_code,
            '',  # Danger code
            '',  # Clinical info
            '',  # Specimen received datetime
            specimen_descriptor,
            ordering_physician,
            '',  # Physician telephone
            '',  # User field 1
            '',  # User field 2
            '',  # Laboratory field 1
            '',  # Laboratory field 2
            '',  # Datetime reported
            '',  # Instrument charge
            '',  # Instrument section ID
            report_type,
        ]

        return self.field_delimiter.join(fields)

    def encode_result(
        self,
        sequence_number: int = 1,
        test_id: str = '',
        value: str = '',
        units: str = '',
        reference_range: str = '',
        abnormal_flag: str = '',
        result_status: str = 'F',  # F=Final, P=Preliminary
        datetime_completed: Optional[datetime] = None,
        operator_id: str = '',
        instrument_id: str = '',
    ) -> str:
        """Encode a result record."""
        datetime_str = datetime_completed.strftime('%Y%m%d%H%M%S') if datetime_completed else ''

        fields = [
            f'R{sequence_number}',
            test_id,
            value,
            units,
            reference_range,
            abnormal_flag,
            '',  # Nature of abnormality
            result_status,
            '',  # Date of change
            operator_id,
            '',  # Datetime started
            datetime_str,
            instrument_id,
        ]

        return self.field_delimiter.join(fields)

    def encode_comment(
        self,
        sequence_number: int = 1,
        source: str = 'L',  # L=Laboratory, I=Instrument
        text: str = '',
        comment_type: str = 'G',  # G=Generic, T=Test-related
    ) -> str:
        """Encode a comment record."""
        fields = [
            f'C{sequence_number}',
            source,
            text,
            comment_type,
        ]

        return self.field_delimiter.join(fields)

    def encode_terminator(self, sequence_number: int = 1, terminator_code: str = 'N') -> str:
        """Encode a terminator record."""
        # N=Normal termination, I=Request for samples, Q=Error
        fields = [
            f'L{sequence_number}',
            terminator_code,
        ]

        return self.field_delimiter.join(fields)

    def encode_query(
        self,
        sequence_number: int = 1,
        starting_range_id: str = '',
        ending_range_id: str = '',
        test_id: str = '',
        request_type: str = 'S',  # S=Sample, P=Patient
        beginning_datetime: Optional[datetime] = None,
        ending_datetime: Optional[datetime] = None,
    ) -> str:
        """Encode a query record for requesting samples from the host."""
        begin_str = beginning_datetime.strftime('%Y%m%d%H%M%S') if beginning_datetime else ''
        end_str = ending_datetime.strftime('%Y%m%d%H%M%S') if ending_datetime else ''

        fields = [
            f'Q{sequence_number}',
            starting_range_id,
            ending_range_id,
            test_id,
            request_type,
            begin_str,
            end_str,
        ]

        return self.field_delimiter.join(fields)

    def build_worklist_message(
        self,
        samples: List[Dict[str, Any]],
        sender_name: str = 'LIMS',
        receiver_id: str = '',
    ) -> bytes:
        """Build a complete worklist message for download to instrument."""
        records = []

        # Header
        records.append(self.encode_header(
            sender_name=sender_name,
            receiver_id=receiver_id,
        ))

        # Patient and Order records for each sample
        for i, sample in enumerate(samples, start=1):
            # Patient record
            records.append(self.encode_patient(
                sequence_number=i,
                patient_id=sample.get('patient_id', ''),
                laboratory_patient_id=sample.get('laboratory_patient_id', ''),
                patient_name=sample.get('patient_name', ''),
                birthdate=sample.get('birthdate', ''),
                sex=sample.get('sex', ''),
            ))

            # Order record
            records.append(self.encode_order(
                sequence_number=1,
                specimen_id=sample.get('specimen_id', ''),
                instrument_specimen_id=sample.get('instrument_specimen_id', ''),
                test_ids=sample.get('test_ids', []),
                priority=sample.get('priority', 'R'),
                action_code='A',
            ))

        # Terminator
        records.append(self.encode_terminator(sequence_number=1))

        return self.encode_message(records)

    def build_acknowledgment(self, ack_type: str = 'ACK') -> bytes:
        """Build an acknowledgment message."""
        if ack_type.upper() == 'ACK':
            return ACK
        else:
            return NAK

    def build_enq(self) -> bytes:
        """Build an ENQ message to initiate transmission."""
        return ENQ

    def build_eot(self) -> bytes:
        """Build an EOT message to end transmission."""
        return EOT

# instruments/protocols/astm/parser.py

"""
ASTM E1381/E1394 Protocol Parser

Parses ASTM messages from laboratory instruments.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
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


@dataclass
class ASTMRecord:
    """Represents a single ASTM record."""
    record_type: str
    sequence_number: int
    fields: List[str]
    raw_data: str = ''

    def get_field(self, index: int, default: str = '') -> str:
        """Get field by index (0-based)."""
        if 0 <= index < len(self.fields):
            return self.fields[index]
        return default

    def get_component(self, field_index: int, component_index: int, default: str = '') -> str:
        """Get a component from a field."""
        field_value = self.get_field(field_index)
        components = field_value.split(COMPONENT_DELIMITER)
        if 0 <= component_index < len(components):
            return components[component_index]
        return default


@dataclass
class ASTMMessage:
    """Represents a complete ASTM message with all records."""
    header: Optional[ASTMRecord] = None
    patients: List[ASTMRecord] = field(default_factory=list)
    orders: List[ASTMRecord] = field(default_factory=list)
    results: List[ASTMRecord] = field(default_factory=list)
    comments: List[ASTMRecord] = field(default_factory=list)
    queries: List[ASTMRecord] = field(default_factory=list)
    terminator: Optional[ASTMRecord] = None
    raw_data: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'header': self._record_to_dict(self.header) if self.header else None,
            'patients': [self._record_to_dict(p) for p in self.patients],
            'orders': [self._record_to_dict(o) for o in self.orders],
            'results': [self._record_to_dict(r) for r in self.results],
            'comments': [self._record_to_dict(c) for c in self.comments],
            'queries': [self._record_to_dict(q) for q in self.queries],
            'terminator': self._record_to_dict(self.terminator) if self.terminator else None,
        }

    def _record_to_dict(self, record: ASTMRecord) -> Dict[str, Any]:
        """Convert a record to dictionary."""
        return {
            'record_type': record.record_type,
            'sequence_number': record.sequence_number,
            'fields': record.fields,
        }


class ASTMParser:
    """Parser for ASTM E1381/E1394 protocol messages."""

    def __init__(self, encoding: str = 'latin-1'):
        self.encoding = encoding
        self.field_delimiter = FIELD_DELIMITER
        self.repeat_delimiter = REPEAT_DELIMITER
        self.component_delimiter = COMPONENT_DELIMITER
        self.escape_delimiter = ESCAPE_DELIMITER

    def parse(self, data: bytes) -> ASTMMessage:
        """Parse ASTM message from raw bytes."""
        message = ASTMMessage()
        message.raw_data = data.decode(self.encoding, errors='replace')

        # Extract frames from the data
        frames = self._extract_frames(data)

        for frame_data, checksum_valid in frames:
            if not checksum_valid:
                logger.warning(f"Invalid checksum in frame: {frame_data[:50]}...")

            # Parse record from frame
            record = self._parse_record(frame_data)
            if record:
                self._add_record_to_message(message, record)

        return message

    def parse_string(self, data: str) -> ASTMMessage:
        """Parse ASTM message from string."""
        return self.parse(data.encode(self.encoding))

    def _extract_frames(self, data: bytes) -> List[Tuple[str, bool]]:
        """Extract individual frames from raw data."""
        frames = []
        current_frame = b''
        in_frame = False

        i = 0
        while i < len(data):
            byte = bytes([data[i]])

            if byte == STX:
                in_frame = True
                current_frame = b''
            elif byte in (ETX, ETB) and in_frame:
                # Extract checksum (next 2 bytes)
                checksum_bytes = data[i+1:i+3] if i+2 < len(data) else b''
                checksum_valid = self._verify_checksum(current_frame + byte, checksum_bytes)

                frame_str = current_frame.decode(self.encoding, errors='replace')
                # Remove frame number at the start
                if frame_str and frame_str[0].isdigit():
                    frame_str = frame_str[1:]

                frames.append((frame_str, checksum_valid))
                in_frame = False
                i += 2  # Skip checksum bytes
            elif in_frame:
                current_frame += byte

            i += 1

        # Handle case where data doesn't have framing
        if not frames and data:
            # Try parsing as plain records
            text = data.decode(self.encoding, errors='replace')
            for line in text.split('\r\n'):
                line = line.strip()
                if line:
                    frames.append((line, True))

        return frames

    def _verify_checksum(self, frame: bytes, checksum_bytes: bytes) -> bool:
        """Verify the checksum of a frame."""
        if len(checksum_bytes) < 2:
            return False

        try:
            expected = int(checksum_bytes.decode('ascii'), 16)
            calculated = sum(frame) % 256
            return expected == calculated
        except (ValueError, UnicodeDecodeError):
            return False

    def _parse_record(self, frame_data: str) -> Optional[ASTMRecord]:
        """Parse a single record from frame data."""
        if not frame_data:
            return None

        fields = frame_data.split(self.field_delimiter)
        if not fields:
            return None

        # First field contains record type and sequence number
        first_field = fields[0]
        if not first_field:
            return None

        record_type = first_field[0].upper()
        sequence_number = 1

        # Extract sequence number if present
        if len(first_field) > 1 and first_field[1:].isdigit():
            sequence_number = int(first_field[1:])

        return ASTMRecord(
            record_type=record_type,
            sequence_number=sequence_number,
            fields=fields[1:],  # Exclude the record type field
            raw_data=frame_data
        )

    def _add_record_to_message(self, message: ASTMMessage, record: ASTMRecord):
        """Add a record to the appropriate list in the message."""
        if record.record_type == 'H':
            message.header = record
            # Parse delimiters from header if present
            self._parse_delimiters(record)
        elif record.record_type == 'P':
            message.patients.append(record)
        elif record.record_type == 'O':
            message.orders.append(record)
        elif record.record_type == 'R':
            message.results.append(record)
        elif record.record_type == 'C':
            message.comments.append(record)
        elif record.record_type == 'Q':
            message.queries.append(record)
        elif record.record_type == 'L':
            message.terminator = record

    def _parse_delimiters(self, header_record: ASTMRecord):
        """Parse delimiter definitions from header record."""
        if header_record.fields:
            delimiter_field = header_record.fields[0]
            if len(delimiter_field) >= 4:
                self.field_delimiter = delimiter_field[0]
                self.repeat_delimiter = delimiter_field[1]
                self.component_delimiter = delimiter_field[2]
                self.escape_delimiter = delimiter_field[3]

    def parse_result_record(self, record: ASTMRecord) -> Dict[str, Any]:
        """Parse a result record into structured data."""
        return {
            'sequence_number': record.sequence_number,
            'test_id': record.get_field(0),
            'value': record.get_field(1),
            'units': record.get_field(2),
            'reference_range': record.get_field(3),
            'abnormal_flag': record.get_field(4),
            'nature_of_abnormality': record.get_field(5),
            'result_status': record.get_field(6),
            'date_of_change': record.get_field(7),
            'operator_id': record.get_field(8),
            'date_time_started': record.get_field(9),
            'date_time_completed': record.get_field(10),
            'instrument_id': record.get_field(11),
        }

    def parse_order_record(self, record: ASTMRecord) -> Dict[str, Any]:
        """Parse an order record into structured data."""
        return {
            'sequence_number': record.sequence_number,
            'specimen_id': record.get_field(0),
            'instrument_specimen_id': record.get_field(1),
            'universal_test_id': record.get_field(2),
            'priority': record.get_field(3),
            'requested_datetime': record.get_field(4),
            'specimen_collection_datetime': record.get_field(5),
            'collection_end_datetime': record.get_field(6),
            'collection_volume': record.get_field(7),
            'collector_id': record.get_field(8),
            'action_code': record.get_field(9),
            'danger_code': record.get_field(10),
            'clinical_info': record.get_field(11),
            'specimen_received_datetime': record.get_field(12),
            'specimen_descriptor': record.get_field(13),
            'ordering_physician': record.get_field(14),
            'physician_telephone': record.get_field(15),
            'user_field_1': record.get_field(16),
            'user_field_2': record.get_field(17),
            'laboratory_field_1': record.get_field(18),
            'laboratory_field_2': record.get_field(19),
            'datetime_reported': record.get_field(20),
            'instrument_charge': record.get_field(21),
            'instrument_section_id': record.get_field(22),
            'report_type': record.get_field(23),
        }

    def parse_patient_record(self, record: ASTMRecord) -> Dict[str, Any]:
        """Parse a patient record into structured data."""
        return {
            'sequence_number': record.sequence_number,
            'patient_id': record.get_field(0),
            'laboratory_patient_id': record.get_field(1),
            'patient_id_3': record.get_field(2),
            'patient_name': record.get_field(3),
            'mothers_maiden_name': record.get_field(4),
            'birthdate': record.get_field(5),
            'sex': record.get_field(6),
            'race': record.get_field(7),
            'address': record.get_field(8),
            'telephone': record.get_field(9),
            'physician_id': record.get_field(10),
            'special_field_1': record.get_field(11),
            'special_field_2': record.get_field(12),
            'height': record.get_field(13),
            'weight': record.get_field(14),
            'diagnosis': record.get_field(15),
            'medications': record.get_field(16),
            'diet': record.get_field(17),
            'practice_field_1': record.get_field(18),
            'practice_field_2': record.get_field(19),
            'admission_date': record.get_field(20),
            'admission_status': record.get_field(21),
            'location': record.get_field(22),
        }

    def parse_query_record(self, record: ASTMRecord) -> Dict[str, Any]:
        """Parse a query record into structured data."""
        return {
            'sequence_number': record.sequence_number,
            'starting_range_id': record.get_field(0),
            'ending_range_id': record.get_field(1),
            'universal_test_id': record.get_field(2),
            'nature_of_request': record.get_field(3),
            'beginning_datetime': record.get_field(4),
            'ending_datetime': record.get_field(5),
            'physician_name': record.get_field(6),
            'physician_telephone': record.get_field(7),
            'user_field_1': record.get_field(8),
            'user_field_2': record.get_field(9),
            'request_information_status': record.get_field(10),
        }

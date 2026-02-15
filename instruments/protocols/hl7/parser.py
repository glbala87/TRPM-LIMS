# instruments/protocols/hl7/parser.py

"""
HL7 v2.x Protocol Parser

Parses HL7 messages from laboratory instruments.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# MLLP (Minimal Lower Layer Protocol) framing characters
VT = b'\x0B'   # Vertical Tab - Start of message
FS = b'\x1C'   # File Separator - End of message
CR = b'\x0D'   # Carriage Return

# Default HL7 delimiters
FIELD_SEPARATOR = '|'
COMPONENT_SEPARATOR = '^'
REPETITION_SEPARATOR = '~'
ESCAPE_CHARACTER = '\\'
SUBCOMPONENT_SEPARATOR = '&'


@dataclass
class HL7Field:
    """Represents an HL7 field with components and subcomponents."""
    value: str
    components: List[str] = field(default_factory=list)
    repetitions: List[List[str]] = field(default_factory=list)

    def __str__(self):
        return self.value

    def get_component(self, index: int, default: str = '') -> str:
        """Get component by index (1-based as per HL7 convention)."""
        if 1 <= index <= len(self.components):
            return self.components[index - 1]
        return default

    def get_subcomponent(self, comp_index: int, sub_index: int, default: str = '') -> str:
        """Get subcomponent (1-based indices)."""
        component = self.get_component(comp_index)
        subcomponents = component.split(SUBCOMPONENT_SEPARATOR)
        if 1 <= sub_index <= len(subcomponents):
            return subcomponents[sub_index - 1]
        return default


@dataclass
class HL7Segment:
    """Represents an HL7 segment."""
    segment_type: str
    fields: List[HL7Field] = field(default_factory=list)
    raw_data: str = ''

    def get_field(self, index: int, default: str = '') -> str:
        """Get field value by index (1-based)."""
        # For MSH segment, field 1 is the field separator itself
        if self.segment_type == 'MSH':
            if index == 1:
                return FIELD_SEPARATOR
            index -= 1

        if 1 <= index <= len(self.fields):
            return str(self.fields[index - 1])
        return default

    def get_field_obj(self, index: int) -> Optional[HL7Field]:
        """Get field object by index (1-based)."""
        if self.segment_type == 'MSH':
            index -= 1

        if 1 <= index <= len(self.fields):
            return self.fields[index - 1]
        return None

    def get_component(self, field_index: int, comp_index: int, default: str = '') -> str:
        """Get component from a field (1-based indices)."""
        field_obj = self.get_field_obj(field_index)
        if field_obj:
            return field_obj.get_component(comp_index, default)
        return default


@dataclass
class HL7Message:
    """Represents a complete HL7 message."""
    segments: List[HL7Segment] = field(default_factory=list)
    raw_data: str = ''

    # Parsed message info
    message_type: str = ''
    trigger_event: str = ''
    control_id: str = ''
    version: str = ''

    def get_segment(self, segment_type: str, index: int = 0) -> Optional[HL7Segment]:
        """Get segment by type. Index for multiple segments of same type."""
        matching = [s for s in self.segments if s.segment_type == segment_type]
        if 0 <= index < len(matching):
            return matching[index]
        return None

    def get_all_segments(self, segment_type: str) -> List[HL7Segment]:
        """Get all segments of a given type."""
        return [s for s in self.segments if s.segment_type == segment_type]

    @property
    def msh(self) -> Optional[HL7Segment]:
        """Get the MSH segment."""
        return self.get_segment('MSH')

    @property
    def pid(self) -> Optional[HL7Segment]:
        """Get the first PID segment."""
        return self.get_segment('PID')

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'message_type': self.message_type,
            'trigger_event': self.trigger_event,
            'control_id': self.control_id,
            'version': self.version,
            'segments': [
                {
                    'type': seg.segment_type,
                    'fields': [str(f) for f in seg.fields]
                }
                for seg in self.segments
            ]
        }


class HL7Parser:
    """Parser for HL7 v2.x protocol messages."""

    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        self.field_separator = FIELD_SEPARATOR
        self.component_separator = COMPONENT_SEPARATOR
        self.repetition_separator = REPETITION_SEPARATOR
        self.escape_character = ESCAPE_CHARACTER
        self.subcomponent_separator = SUBCOMPONENT_SEPARATOR

    def parse(self, data: bytes) -> HL7Message:
        """Parse HL7 message from raw bytes."""
        # Remove MLLP framing if present
        text = self._strip_mllp(data)
        return self.parse_string(text)

    def parse_string(self, text: str) -> HL7Message:
        """Parse HL7 message from string."""
        message = HL7Message()
        message.raw_data = text

        # Split into segments
        segments = re.split(r'[\r\n]+', text.strip())

        for segment_text in segments:
            segment_text = segment_text.strip()
            if not segment_text:
                continue

            segment = self._parse_segment(segment_text)
            if segment:
                message.segments.append(segment)

                # Parse delimiters from MSH if it's the first segment
                if segment.segment_type == 'MSH' and len(message.segments) == 1:
                    self._parse_delimiters(segment)
                    self._extract_message_info(message, segment)

        return message

    def _strip_mllp(self, data: bytes) -> str:
        """Remove MLLP framing characters."""
        # Remove VT at start
        if data.startswith(VT):
            data = data[1:]

        # Remove FS CR at end
        if data.endswith(FS + CR):
            data = data[:-2]
        elif data.endswith(FS):
            data = data[:-1]

        return data.decode(self.encoding, errors='replace')

    def _parse_segment(self, segment_text: str) -> Optional[HL7Segment]:
        """Parse a single segment."""
        if len(segment_text) < 3:
            return None

        segment_type = segment_text[:3]

        # For MSH segment, the delimiter is at position 3
        if segment_type == 'MSH':
            self.field_separator = segment_text[3] if len(segment_text) > 3 else '|'
            # Fields start after the encoding characters
            if len(segment_text) > 4:
                # First field after MSH is the encoding characters
                remaining = segment_text[4:]
                fields_text = remaining.split(self.field_separator)
            else:
                fields_text = []
        else:
            # Regular segment - split on field separator
            parts = segment_text.split(self.field_separator)
            fields_text = parts[1:] if len(parts) > 1 else []

        fields = []
        for field_text in fields_text:
            field_obj = self._parse_field(field_text)
            fields.append(field_obj)

        return HL7Segment(
            segment_type=segment_type,
            fields=fields,
            raw_data=segment_text
        )

    def _parse_field(self, field_text: str) -> HL7Field:
        """Parse a field into components and repetitions."""
        # Handle repetitions
        repetitions = field_text.split(self.repetition_separator)

        # Parse components of first (or only) repetition
        components = repetitions[0].split(self.component_separator)

        # Parse all repetitions
        all_repetitions = [
            rep.split(self.component_separator) for rep in repetitions
        ]

        return HL7Field(
            value=field_text,
            components=components,
            repetitions=all_repetitions
        )

    def _parse_delimiters(self, msh_segment: HL7Segment):
        """Parse delimiter definitions from MSH segment."""
        if msh_segment.fields:
            encoding_chars = str(msh_segment.fields[0])
            if len(encoding_chars) >= 4:
                self.component_separator = encoding_chars[0]
                self.repetition_separator = encoding_chars[1]
                self.escape_character = encoding_chars[2]
                self.subcomponent_separator = encoding_chars[3]

    def _extract_message_info(self, message: HL7Message, msh: HL7Segment):
        """Extract message type and control ID from MSH segment."""
        # MSH-9: Message Type
        msg_type_field = msh.get_field_obj(9)
        if msg_type_field:
            message.message_type = msg_type_field.get_component(1)
            message.trigger_event = msg_type_field.get_component(2)

        # MSH-10: Message Control ID
        message.control_id = msh.get_field(10)

        # MSH-12: Version ID
        message.version = msh.get_field(12)

    def parse_obx_segment(self, segment: HL7Segment) -> Dict[str, Any]:
        """Parse an OBX (Observation Result) segment into structured data."""
        return {
            'set_id': segment.get_field(1),
            'value_type': segment.get_field(2),
            'observation_identifier': segment.get_field(3),
            'observation_identifier_text': segment.get_component(3, 2),
            'observation_sub_id': segment.get_field(4),
            'observation_value': segment.get_field(5),
            'units': segment.get_field(6),
            'units_text': segment.get_component(6, 2),
            'reference_range': segment.get_field(7),
            'abnormal_flags': segment.get_field(8),
            'probability': segment.get_field(9),
            'nature_of_abnormality': segment.get_field(10),
            'observation_result_status': segment.get_field(11),
            'effective_date': segment.get_field(12),
            'user_defined_access_checks': segment.get_field(13),
            'date_time_of_observation': segment.get_field(14),
            'producer_id': segment.get_field(15),
            'responsible_observer': segment.get_field(16),
            'observation_method': segment.get_field(17),
            'equipment_instance_identifier': segment.get_field(18),
            'date_time_of_analysis': segment.get_field(19),
        }

    def parse_obr_segment(self, segment: HL7Segment) -> Dict[str, Any]:
        """Parse an OBR (Observation Request) segment into structured data."""
        return {
            'set_id': segment.get_field(1),
            'placer_order_number': segment.get_field(2),
            'filler_order_number': segment.get_field(3),
            'universal_service_identifier': segment.get_field(4),
            'universal_service_text': segment.get_component(4, 2),
            'priority': segment.get_field(5),
            'requested_date_time': segment.get_field(6),
            'observation_date_time': segment.get_field(7),
            'observation_end_date_time': segment.get_field(8),
            'collection_volume': segment.get_field(9),
            'collector_identifier': segment.get_field(10),
            'specimen_action_code': segment.get_field(11),
            'danger_code': segment.get_field(12),
            'relevant_clinical_info': segment.get_field(13),
            'specimen_received_date_time': segment.get_field(14),
            'specimen_source': segment.get_field(15),
            'ordering_provider': segment.get_field(16),
            'order_callback_phone': segment.get_field(17),
            'placer_field_1': segment.get_field(18),
            'placer_field_2': segment.get_field(19),
            'filler_field_1': segment.get_field(20),
            'filler_field_2': segment.get_field(21),
            'results_status_change_date_time': segment.get_field(22),
            'charge_to_practice': segment.get_field(23),
            'diagnostic_service_section_id': segment.get_field(24),
            'result_status': segment.get_field(25),
            'parent_result': segment.get_field(26),
            'quantity_timing': segment.get_field(27),
            'result_copies_to': segment.get_field(28),
            'parent_number': segment.get_field(29),
            'transportation_mode': segment.get_field(30),
            'reason_for_study': segment.get_field(31),
            'principal_result_interpreter': segment.get_field(32),
            'assistant_result_interpreter': segment.get_field(33),
            'technician': segment.get_field(34),
            'transcriptionist': segment.get_field(35),
            'scheduled_date_time': segment.get_field(36),
        }

    def parse_pid_segment(self, segment: HL7Segment) -> Dict[str, Any]:
        """Parse a PID (Patient Identification) segment into structured data."""
        # Parse patient name components
        name_field = segment.get_field_obj(5)
        family_name = name_field.get_component(1) if name_field else ''
        given_name = name_field.get_component(2) if name_field else ''

        return {
            'set_id': segment.get_field(1),
            'patient_id': segment.get_field(2),
            'patient_identifier_list': segment.get_field(3),
            'alternate_patient_id': segment.get_field(4),
            'patient_name': segment.get_field(5),
            'family_name': family_name,
            'given_name': given_name,
            'mothers_maiden_name': segment.get_field(6),
            'date_of_birth': segment.get_field(7),
            'administrative_sex': segment.get_field(8),
            'patient_alias': segment.get_field(9),
            'race': segment.get_field(10),
            'patient_address': segment.get_field(11),
            'county_code': segment.get_field(12),
            'phone_number_home': segment.get_field(13),
            'phone_number_business': segment.get_field(14),
            'primary_language': segment.get_field(15),
            'marital_status': segment.get_field(16),
            'religion': segment.get_field(17),
            'patient_account_number': segment.get_field(18),
            'ssn_number': segment.get_field(19),
            'drivers_license_number': segment.get_field(20),
        }

    def parse_orc_segment(self, segment: HL7Segment) -> Dict[str, Any]:
        """Parse an ORC (Common Order) segment into structured data."""
        return {
            'order_control': segment.get_field(1),
            'placer_order_number': segment.get_field(2),
            'filler_order_number': segment.get_field(3),
            'placer_group_number': segment.get_field(4),
            'order_status': segment.get_field(5),
            'response_flag': segment.get_field(6),
            'quantity_timing': segment.get_field(7),
            'parent': segment.get_field(8),
            'date_time_of_transaction': segment.get_field(9),
            'entered_by': segment.get_field(10),
            'verified_by': segment.get_field(11),
            'ordering_provider': segment.get_field(12),
            'enterers_location': segment.get_field(13),
            'call_back_phone_number': segment.get_field(14),
            'order_effective_date_time': segment.get_field(15),
            'order_control_code_reason': segment.get_field(16),
            'entering_organization': segment.get_field(17),
            'entering_device': segment.get_field(18),
            'action_by': segment.get_field(19),
        }

    def extract_results(self, message: HL7Message) -> List[Dict[str, Any]]:
        """Extract all results from an ORU message."""
        results = []

        # Get patient info
        pid = message.pid
        patient_info = self.parse_pid_segment(pid) if pid else {}

        # Get all OBR segments (test orders)
        obr_segments = message.get_all_segments('OBR')
        obx_segments = message.get_all_segments('OBX')

        # Group OBX segments under their OBR
        current_obr = None
        current_obr_data = None

        for segment in message.segments:
            if segment.segment_type == 'OBR':
                current_obr = segment
                current_obr_data = self.parse_obr_segment(segment)
            elif segment.segment_type == 'OBX' and current_obr_data:
                obx_data = self.parse_obx_segment(segment)
                results.append({
                    'patient': patient_info,
                    'order': current_obr_data,
                    'result': obx_data,
                })

        return results

# instruments/protocols/hl7/encoder.py

"""
HL7 v2.x Protocol Encoder

Encodes HL7 messages for sending to laboratory instruments.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# MLLP framing characters
VT = b'\x0B'   # Vertical Tab - Start of message
FS = b'\x1C'   # File Separator - End of message
CR = b'\x0D'   # Carriage Return

# Default delimiters
FIELD_SEPARATOR = '|'
COMPONENT_SEPARATOR = '^'
REPETITION_SEPARATOR = '~'
ESCAPE_CHARACTER = '\\'
SUBCOMPONENT_SEPARATOR = '&'


class HL7Encoder:
    """Encoder for HL7 v2.x protocol messages."""

    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        self.field_separator = FIELD_SEPARATOR
        self.component_separator = COMPONENT_SEPARATOR
        self.repetition_separator = REPETITION_SEPARATOR
        self.escape_character = ESCAPE_CHARACTER
        self.subcomponent_separator = SUBCOMPONENT_SEPARATOR

    @property
    def encoding_characters(self) -> str:
        """Get the encoding characters string for MSH-2."""
        return (
            self.component_separator +
            self.repetition_separator +
            self.escape_character +
            self.subcomponent_separator
        )

    def _format_datetime(self, dt: Optional[datetime] = None) -> str:
        """Format datetime for HL7 (YYYYMMDDHHmmss)."""
        if dt is None:
            dt = datetime.now()
        return dt.strftime('%Y%m%d%H%M%S')

    def _generate_control_id(self) -> str:
        """Generate a unique message control ID."""
        return str(uuid.uuid4())[:20].replace('-', '')

    def _join_fields(self, fields: List[str]) -> str:
        """Join fields with field separator."""
        return self.field_separator.join(fields)

    def _join_components(self, components: List[str]) -> str:
        """Join components with component separator."""
        return self.component_separator.join(components)

    def _join_repetitions(self, repetitions: List[str]) -> str:
        """Join repetitions with repetition separator."""
        return self.repetition_separator.join(repetitions)

    def encode_msh(
        self,
        sending_application: str = 'LIMS',
        sending_facility: str = '',
        receiving_application: str = '',
        receiving_facility: str = '',
        message_type: str = 'ORM',
        trigger_event: str = 'O01',
        message_control_id: str = '',
        processing_id: str = 'P',  # P=Production, T=Training, D=Debugging
        version_id: str = '2.4',
        message_datetime: Optional[datetime] = None,
    ) -> str:
        """Encode MSH (Message Header) segment."""
        if not message_control_id:
            message_control_id = self._generate_control_id()

        datetime_str = self._format_datetime(message_datetime)
        msg_type = self._join_components([message_type, trigger_event])

        fields = [
            'MSH',
            self.encoding_characters,
            sending_application,
            sending_facility,
            receiving_application,
            receiving_facility,
            datetime_str,
            '',  # Security
            msg_type,
            message_control_id,
            processing_id,
            version_id,
        ]

        return self._join_fields(fields)

    def encode_pid(
        self,
        set_id: int = 1,
        patient_id: str = '',
        patient_identifier_list: str = '',
        alternate_patient_id: str = '',
        patient_name: str = '',
        family_name: str = '',
        given_name: str = '',
        middle_name: str = '',
        date_of_birth: str = '',
        sex: str = '',
        address: str = '',
        phone_home: str = '',
        phone_business: str = '',
        patient_account_number: str = '',
    ) -> str:
        """Encode PID (Patient Identification) segment."""
        # Format patient name: Family^Given^Middle
        if family_name or given_name:
            name_components = [family_name, given_name, middle_name]
            patient_name = self._join_components(name_components)

        fields = [
            'PID',
            str(set_id),
            patient_id,
            patient_identifier_list,
            alternate_patient_id,
            patient_name,
            '',  # Mother's maiden name
            date_of_birth,
            sex,
            '',  # Patient alias
            '',  # Race
            address,
            '',  # County code
            phone_home,
            phone_business,
            '',  # Primary language
            '',  # Marital status
            '',  # Religion
            patient_account_number,
        ]

        return self._join_fields(fields)

    def encode_orc(
        self,
        order_control: str = 'NW',  # NW=New Order, CA=Cancel, SC=Status Changed
        placer_order_number: str = '',
        filler_order_number: str = '',
        order_status: str = '',
        datetime_of_transaction: Optional[datetime] = None,
        ordering_provider: str = '',
    ) -> str:
        """Encode ORC (Common Order) segment."""
        datetime_str = self._format_datetime(datetime_of_transaction)

        fields = [
            'ORC',
            order_control,
            placer_order_number,
            filler_order_number,
            '',  # Placer group number
            order_status,
            '',  # Response flag
            '',  # Quantity/timing
            '',  # Parent
            datetime_str,
            '',  # Entered by
            '',  # Verified by
            ordering_provider,
        ]

        return self._join_fields(fields)

    def encode_obr(
        self,
        set_id: int = 1,
        placer_order_number: str = '',
        filler_order_number: str = '',
        universal_service_identifier: str = '',
        universal_service_text: str = '',
        priority: str = 'R',  # R=Routine, S=Stat
        requested_datetime: Optional[datetime] = None,
        observation_datetime: Optional[datetime] = None,
        specimen_source: str = '',
        ordering_provider: str = '',
        result_status: str = '',
    ) -> str:
        """Encode OBR (Observation Request) segment."""
        requested_str = self._format_datetime(requested_datetime) if requested_datetime else ''
        observation_str = self._format_datetime(observation_datetime) if observation_datetime else ''

        # Universal service ID: code^text
        if universal_service_text:
            service_id = self._join_components([universal_service_identifier, universal_service_text])
        else:
            service_id = universal_service_identifier

        fields = [
            'OBR',
            str(set_id),
            placer_order_number,
            filler_order_number,
            service_id,
            priority,
            requested_str,
            observation_str,
            '',  # Observation end datetime
            '',  # Collection volume
            '',  # Collector identifier
            '',  # Specimen action code
            '',  # Danger code
            '',  # Relevant clinical info
            '',  # Specimen received datetime
            specimen_source,
            ordering_provider,
            '',  # Order callback phone
            '',  # Placer field 1
            '',  # Placer field 2
            '',  # Filler field 1
            '',  # Filler field 2
            '',  # Results status change datetime
            '',  # Charge to practice
            '',  # Diagnostic service section ID
            result_status,
        ]

        return self._join_fields(fields)

    def encode_obx(
        self,
        set_id: int = 1,
        value_type: str = 'NM',  # NM=Numeric, ST=String, TX=Text, CE=Coded
        observation_identifier: str = '',
        observation_identifier_text: str = '',
        observation_sub_id: str = '',
        observation_value: str = '',
        units: str = '',
        units_text: str = '',
        reference_range: str = '',
        abnormal_flags: str = '',
        result_status: str = 'F',  # F=Final, P=Preliminary, C=Corrected
        observation_datetime: Optional[datetime] = None,
        producer_id: str = '',
    ) -> str:
        """Encode OBX (Observation Result) segment."""
        # Observation identifier: code^text
        if observation_identifier_text:
            obs_id = self._join_components([observation_identifier, observation_identifier_text])
        else:
            obs_id = observation_identifier

        # Units: code^text
        if units_text:
            units_full = self._join_components([units, units_text])
        else:
            units_full = units

        datetime_str = self._format_datetime(observation_datetime) if observation_datetime else ''

        fields = [
            'OBX',
            str(set_id),
            value_type,
            obs_id,
            observation_sub_id,
            observation_value,
            units_full,
            reference_range,
            abnormal_flags,
            '',  # Probability
            '',  # Nature of abnormal test
            result_status,
            '',  # Effective date of reference range
            '',  # User defined access checks
            datetime_str,
            producer_id,
        ]

        return self._join_fields(fields)

    def encode_msa(
        self,
        acknowledgment_code: str = 'AA',  # AA=Accept, AE=Error, AR=Reject
        message_control_id: str = '',
        text_message: str = '',
        error_condition: str = '',
    ) -> str:
        """Encode MSA (Message Acknowledgment) segment."""
        fields = [
            'MSA',
            acknowledgment_code,
            message_control_id,
            text_message,
            '',  # Expected sequence number
            '',  # Delayed acknowledgment type
            error_condition,
        ]

        return self._join_fields(fields)

    def encode_err(
        self,
        error_code: str = '',
        error_location: str = '',
        error_text: str = '',
        severity: str = 'E',  # E=Error, W=Warning, I=Information
    ) -> str:
        """Encode ERR (Error) segment."""
        fields = [
            'ERR',
            error_location,
            '',  # Error location
            error_code,
            error_text,
            '',  # Severity
        ]

        return self._join_fields(fields)

    def build_message(self, segments: List[str]) -> str:
        """Build a complete HL7 message from segments."""
        return '\r'.join(segments)

    def wrap_mllp(self, message: str) -> bytes:
        """Wrap a message with MLLP framing."""
        return VT + message.encode(self.encoding) + FS + CR

    def build_orm_message(
        self,
        patient_info: Dict[str, Any],
        order_info: Dict[str, Any],
        tests: List[Dict[str, Any]],
        sending_application: str = 'LIMS',
        receiving_application: str = '',
    ) -> bytes:
        """Build a complete ORM (Order) message."""
        segments = []

        # MSH segment
        segments.append(self.encode_msh(
            sending_application=sending_application,
            receiving_application=receiving_application,
            message_type='ORM',
            trigger_event='O01',
        ))

        # PID segment
        segments.append(self.encode_pid(
            patient_id=patient_info.get('patient_id', ''),
            patient_identifier_list=patient_info.get('identifier_list', ''),
            family_name=patient_info.get('family_name', ''),
            given_name=patient_info.get('given_name', ''),
            date_of_birth=patient_info.get('date_of_birth', ''),
            sex=patient_info.get('sex', ''),
        ))

        # ORC segment
        segments.append(self.encode_orc(
            order_control='NW',
            placer_order_number=order_info.get('placer_order_number', ''),
            ordering_provider=order_info.get('ordering_provider', ''),
        ))

        # OBR segment for each test
        for i, test in enumerate(tests, start=1):
            segments.append(self.encode_obr(
                set_id=i,
                placer_order_number=order_info.get('placer_order_number', ''),
                universal_service_identifier=test.get('test_code', ''),
                universal_service_text=test.get('test_name', ''),
                priority=test.get('priority', 'R'),
                specimen_source=test.get('specimen_source', ''),
            ))

        message = self.build_message(segments)
        return self.wrap_mllp(message)

    def build_ack_message(
        self,
        original_control_id: str,
        acknowledgment_code: str = 'AA',
        text_message: str = '',
        sending_application: str = 'LIMS',
        receiving_application: str = '',
    ) -> bytes:
        """Build an ACK (Acknowledgment) message."""
        segments = []

        # MSH segment
        segments.append(self.encode_msh(
            sending_application=sending_application,
            receiving_application=receiving_application,
            message_type='ACK',
            trigger_event='',
        ))

        # MSA segment
        segments.append(self.encode_msa(
            acknowledgment_code=acknowledgment_code,
            message_control_id=original_control_id,
            text_message=text_message,
        ))

        message = self.build_message(segments)
        return self.wrap_mllp(message)

    def build_oru_message(
        self,
        patient_info: Dict[str, Any],
        order_info: Dict[str, Any],
        results: List[Dict[str, Any]],
        sending_application: str = 'LIMS',
        receiving_application: str = '',
    ) -> bytes:
        """Build an ORU (Observation Result) message."""
        segments = []

        # MSH segment
        segments.append(self.encode_msh(
            sending_application=sending_application,
            receiving_application=receiving_application,
            message_type='ORU',
            trigger_event='R01',
        ))

        # PID segment
        segments.append(self.encode_pid(
            patient_id=patient_info.get('patient_id', ''),
            family_name=patient_info.get('family_name', ''),
            given_name=patient_info.get('given_name', ''),
            date_of_birth=patient_info.get('date_of_birth', ''),
            sex=patient_info.get('sex', ''),
        ))

        # ORC segment
        segments.append(self.encode_orc(
            order_control='RE',  # RE = Observations/Result
            placer_order_number=order_info.get('placer_order_number', ''),
            filler_order_number=order_info.get('filler_order_number', ''),
        ))

        # OBR segment
        segments.append(self.encode_obr(
            placer_order_number=order_info.get('placer_order_number', ''),
            filler_order_number=order_info.get('filler_order_number', ''),
            result_status='F',
        ))

        # OBX segments for each result
        for i, result in enumerate(results, start=1):
            segments.append(self.encode_obx(
                set_id=i,
                value_type=result.get('value_type', 'NM'),
                observation_identifier=result.get('test_code', ''),
                observation_identifier_text=result.get('test_name', ''),
                observation_value=str(result.get('value', '')),
                units=result.get('units', ''),
                reference_range=result.get('reference_range', ''),
                abnormal_flags=result.get('abnormal_flag', ''),
                result_status='F',
            ))

        message = self.build_message(segments)
        return self.wrap_mllp(message)

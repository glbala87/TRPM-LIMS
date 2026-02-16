# data_exchange/services/hl7_service.py
"""
HL7 v2.x message generation and parsing service.

Supports generation of ORU^R01 (Observation Results) messages
for sending laboratory results to EHR systems.
"""

import logging
from datetime import datetime
from typing import Optional
import uuid

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class HL7ServiceError(Exception):
    """Exception raised for HL7 service errors."""
    pass


class HL7Service:
    """
    Service for generating and parsing HL7 v2.x messages.

    Supports:
    - ORU^R01: Observation Result
    - ACK: Acknowledgment parsing
    """

    # HL7 control characters
    SEGMENT_SEPARATOR = '\r'
    FIELD_SEPARATOR = '|'
    COMPONENT_SEPARATOR = '^'
    REPETITION_SEPARATOR = '~'
    ESCAPE_CHARACTER = '\\'
    SUBCOMPONENT_SEPARATOR = '&'

    def __init__(self, external_system=None):
        """
        Initialize HL7 service.

        Args:
            external_system: Optional ExternalSystem instance for configuration
        """
        self.external_system = external_system
        self._set_defaults()

    def _set_defaults(self):
        """Set default values from external system or settings."""
        if self.external_system:
            self.sending_app = self.external_system.hl7_sending_application
            self.sending_facility = self.external_system.hl7_sending_facility
            self.receiving_app = self.external_system.hl7_receiving_application
            self.receiving_facility = self.external_system.hl7_receiving_facility
            self.version = self.external_system.hl7_version
            self.encoding = self.external_system.message_encoding
        else:
            self.sending_app = 'TRPM-LIMS'
            self.sending_facility = getattr(settings, 'LAB_NAME', 'TRPM')
            self.receiving_app = ''
            self.receiving_facility = ''
            self.version = '2.5.1'
            self.encoding = 'UTF-8'

    def generate_oru_r01(self, molecular_result) -> str:
        """
        Generate an ORU^R01 message for a molecular result.

        Args:
            molecular_result: MolecularResult instance

        Returns:
            HL7 message string
        """
        sample = molecular_result.sample
        patient = sample.lab_order.patient

        segments = []

        # MSH - Message Header
        segments.append(self._build_msh('ORU', 'R01'))

        # PID - Patient Identification
        segments.append(self._build_pid(patient))

        # PV1 - Patient Visit (optional but common)
        segments.append(self._build_pv1(sample.lab_order))

        # ORC - Common Order
        segments.append(self._build_orc(sample.lab_order, molecular_result))

        # OBR - Observation Request
        segments.append(self._build_obr(molecular_result))

        # OBX - Observation Results
        obx_segments = self._build_obx_segments(molecular_result)
        segments.extend(obx_segments)

        # NTE - Notes (if present)
        if molecular_result.notes:
            segments.append(self._build_nte(molecular_result.notes))

        return self.SEGMENT_SEPARATOR.join(segments) + self.SEGMENT_SEPARATOR

    def _build_msh(self, message_type: str, trigger_event: str) -> str:
        """Build MSH (Message Header) segment."""
        now = timezone.now()
        message_datetime = now.strftime('%Y%m%d%H%M%S')
        message_control_id = str(uuid.uuid4())[:20]

        encoding_chars = (
            f'{self.COMPONENT_SEPARATOR}'
            f'{self.REPETITION_SEPARATOR}'
            f'{self.ESCAPE_CHARACTER}'
            f'{self.SUBCOMPONENT_SEPARATOR}'
        )

        fields = [
            'MSH',
            encoding_chars,  # MSH-2: Encoding Characters
            self.sending_app,  # MSH-3: Sending Application
            self.sending_facility,  # MSH-4: Sending Facility
            self.receiving_app,  # MSH-5: Receiving Application
            self.receiving_facility,  # MSH-6: Receiving Facility
            message_datetime,  # MSH-7: Date/Time of Message
            '',  # MSH-8: Security
            f'{message_type}{self.COMPONENT_SEPARATOR}{trigger_event}',  # MSH-9: Message Type
            message_control_id,  # MSH-10: Message Control ID
            'P',  # MSH-11: Processing ID (P=Production, D=Debugging, T=Training)
            self.version,  # MSH-12: Version ID
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_pid(self, patient) -> str:
        """Build PID (Patient Identification) segment."""
        # Format date of birth
        dob = ''
        if patient.date_of_birth:
            dob = patient.date_of_birth.strftime('%Y%m%d')

        # Patient name (Family^Given^Middle)
        patient_name = f"{patient.last_name}{self.COMPONENT_SEPARATOR}{patient.first_name}"
        if hasattr(patient, 'middle_name') and patient.middle_name:
            patient_name += f"{self.COMPONENT_SEPARATOR}{patient.middle_name}"

        # Gender code
        gender_map = {'M': 'M', 'F': 'F', 'O': 'O', 'U': 'U'}
        gender = gender_map.get(patient.gender, 'U')

        fields = [
            'PID',
            '1',  # PID-1: Set ID
            '',  # PID-2: Patient ID (External)
            str(patient.OP_NO or patient.id),  # PID-3: Patient Identifier List
            '',  # PID-4: Alternate Patient ID
            patient_name,  # PID-5: Patient Name
            '',  # PID-6: Mother's Maiden Name
            dob,  # PID-7: Date/Time of Birth
            gender,  # PID-8: Administrative Sex
            '',  # PID-9: Patient Alias
            '',  # PID-10: Race
            '',  # PID-11: Patient Address
            '',  # PID-12: County Code
            '',  # PID-13: Phone Number - Home
            '',  # PID-14: Phone Number - Business
            '',  # PID-15: Primary Language
            '',  # PID-16: Marital Status
            '',  # PID-17: Religion
            '',  # PID-18: Patient Account Number
            '',  # PID-19: SSN
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_pv1(self, lab_order) -> str:
        """Build PV1 (Patient Visit) segment."""
        fields = [
            'PV1',
            '1',  # PV1-1: Set ID
            'O',  # PV1-2: Patient Class (O=Outpatient, I=Inpatient, E=Emergency)
            '',  # PV1-3: Assigned Patient Location
            '',  # PV1-4: Admission Type
            '',  # PV1-5: Preadmit Number
            '',  # PV1-6: Prior Patient Location
            '',  # PV1-7: Attending Doctor
            '',  # PV1-8: Referring Doctor
            '',  # PV1-9: Consulting Doctor
            '',  # PV1-10: Hospital Service
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_orc(self, lab_order, molecular_result) -> str:
        """Build ORC (Common Order) segment."""
        order_datetime = lab_order.order_datetime.strftime('%Y%m%d%H%M%S') if lab_order.order_datetime else ''

        fields = [
            'ORC',
            'RE',  # ORC-1: Order Control (RE=Observations/Results)
            str(lab_order.id),  # ORC-2: Placer Order Number
            str(molecular_result.id),  # ORC-3: Filler Order Number
            '',  # ORC-4: Placer Group Number
            'CM',  # ORC-5: Order Status (CM=Complete)
            '',  # ORC-6: Response Flag
            '',  # ORC-7: Quantity/Timing
            '',  # ORC-8: Parent
            order_datetime,  # ORC-9: Date/Time of Transaction
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_obr(self, molecular_result) -> str:
        """Build OBR (Observation Request) segment."""
        sample = molecular_result.sample
        test_panel = molecular_result.test_panel

        collection_datetime = ''
        if sample.collection_datetime:
            collection_datetime = sample.collection_datetime.strftime('%Y%m%d%H%M%S')

        result_datetime = ''
        if molecular_result.approved_at:
            result_datetime = molecular_result.approved_at.strftime('%Y%m%d%H%M%S')

        # Universal Service Identifier (Test Code^Test Name)
        universal_service = f"{test_panel.code}{self.COMPONENT_SEPARATOR}{test_panel.name}"

        # Result Status
        status_map = {
            'PENDING': 'I',
            'PRELIMINARY': 'P',
            'FINAL': 'F',
            'AMENDED': 'C',
            'CANCELLED': 'X',
        }
        result_status = status_map.get(molecular_result.status, 'F')

        fields = [
            'OBR',
            '1',  # OBR-1: Set ID
            str(sample.lab_order_id),  # OBR-2: Placer Order Number
            str(molecular_result.id),  # OBR-3: Filler Order Number
            universal_service,  # OBR-4: Universal Service Identifier
            '',  # OBR-5: Priority
            '',  # OBR-6: Requested Date/Time
            collection_datetime,  # OBR-7: Observation Date/Time
            '',  # OBR-8: Observation End Date/Time
            '',  # OBR-9: Collection Volume
            '',  # OBR-10: Collector Identifier
            '',  # OBR-11: Specimen Action Code
            '',  # OBR-12: Danger Code
            '',  # OBR-13: Relevant Clinical Information
            '',  # OBR-14: Specimen Received Date/Time
            str(sample.sample_type or ''),  # OBR-15: Specimen Source
            '',  # OBR-16: Ordering Provider
            '',  # OBR-17: Order Callback Phone Number
            '',  # OBR-18: Placer Field 1
            '',  # OBR-19: Placer Field 2
            '',  # OBR-20: Filler Field 1
            '',  # OBR-21: Filler Field 2
            result_datetime,  # OBR-22: Results Rpt/Status Chng - Date/Time
            '',  # OBR-23: Charge to Practice
            '',  # OBR-24: Diagnostic Serv Sect ID
            result_status,  # OBR-25: Result Status
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_obx_segments(self, molecular_result) -> list:
        """Build OBX (Observation/Result) segments."""
        segments = []
        set_id = 1

        # Overall interpretation
        if molecular_result.interpretation:
            segments.append(self._build_obx(
                set_id=set_id,
                value_type='ST',
                observation_id='INTERP',
                observation_name='Interpretation',
                value=molecular_result.get_interpretation_display(),
                units='',
                abnormal_flag='',
                status='F'
            ))
            set_id += 1

        # Clinical significance
        if molecular_result.clinical_significance:
            segments.append(self._build_obx(
                set_id=set_id,
                value_type='TX',
                observation_id='CLINSIG',
                observation_name='Clinical Significance',
                value=molecular_result.clinical_significance[:200],  # Truncate if needed
                units='',
                abnormal_flag='',
                status='F'
            ))
            set_id += 1

        # Variant calls (for NGS results)
        for variant in molecular_result.variant_calls.select_related('gene').all():
            variant_desc = f"{variant.gene.symbol if variant.gene else 'Unknown'}: {variant.hgvs_c or f'{variant.ref_allele}>{variant.alt_allele}'}"

            abnormal_flag = ''
            if variant.classification in ['PATHOGENIC', 'LIKELY_PATHOGENIC']:
                abnormal_flag = 'A'  # Abnormal

            segments.append(self._build_obx(
                set_id=set_id,
                value_type='ST',
                observation_id=f'VAR{variant.id}',
                observation_name='Variant',
                value=variant_desc,
                units='',
                abnormal_flag=abnormal_flag,
                status='F'
            ))
            set_id += 1

            # Add classification as sub-observation
            if variant.classification:
                segments.append(self._build_obx(
                    set_id=set_id,
                    value_type='CE',
                    observation_id=f'CLASS{variant.id}',
                    observation_name='Classification',
                    value=variant.get_classification_display(),
                    units='',
                    abnormal_flag='',
                    status='F'
                ))
                set_id += 1

        # PCR results
        for pcr_result in molecular_result.pcr_results.select_related('target_gene').all():
            target_name = pcr_result.target_gene.symbol if pcr_result.target_gene else 'Unknown'

            abnormal_flag = ''
            if pcr_result.is_detected == 'DETECTED':
                abnormal_flag = 'A'

            segments.append(self._build_obx(
                set_id=set_id,
                value_type='ST',
                observation_id=f'PCR_{target_name}',
                observation_name=f'{target_name} Detection',
                value=pcr_result.get_is_detected_display(),
                units='',
                abnormal_flag=abnormal_flag,
                status='F'
            ))
            set_id += 1

            if pcr_result.ct_value:
                segments.append(self._build_obx(
                    set_id=set_id,
                    value_type='NM',
                    observation_id=f'CT_{target_name}',
                    observation_name=f'{target_name} Ct Value',
                    value=str(pcr_result.ct_value),
                    units='cycles',
                    abnormal_flag='',
                    status='F'
                ))
                set_id += 1

        return segments

    def _build_obx(
        self,
        set_id: int,
        value_type: str,
        observation_id: str,
        observation_name: str,
        value: str,
        units: str,
        abnormal_flag: str,
        status: str
    ) -> str:
        """Build a single OBX segment."""
        observation_identifier = f"{observation_id}{self.COMPONENT_SEPARATOR}{observation_name}"

        fields = [
            'OBX',
            str(set_id),  # OBX-1: Set ID
            value_type,  # OBX-2: Value Type (ST, NM, CE, TX, etc.)
            observation_identifier,  # OBX-3: Observation Identifier
            '',  # OBX-4: Observation Sub-ID
            value,  # OBX-5: Observation Value
            units,  # OBX-6: Units
            '',  # OBX-7: References Range
            abnormal_flag,  # OBX-8: Abnormal Flags (A, H, L, etc.)
            '',  # OBX-9: Probability
            '',  # OBX-10: Nature of Abnormal Test
            status,  # OBX-11: Observation Result Status (F=Final)
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _build_nte(self, note: str) -> str:
        """Build NTE (Notes and Comments) segment."""
        # Escape special characters in the note
        escaped_note = note.replace('\\', '\\E\\').replace('|', '\\F\\').replace('^', '\\S\\')

        fields = [
            'NTE',
            '1',  # NTE-1: Set ID
            '',  # NTE-2: Source of Comment
            escaped_note[:200],  # NTE-3: Comment (truncate to fit)
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def parse_ack(self, ack_message: str) -> dict:
        """
        Parse an ACK (Acknowledgment) message.

        Args:
            ack_message: Raw ACK message string

        Returns:
            Dictionary with acknowledgment details
        """
        result = {
            'is_valid': False,
            'ack_code': '',
            'message_control_id': '',
            'text_message': '',
            'error_code': '',
            'error_message': '',
        }

        try:
            segments = ack_message.strip().split(self.SEGMENT_SEPARATOR)

            for segment in segments:
                fields = segment.split(self.FIELD_SEPARATOR)

                if fields[0] == 'MSA':
                    result['ack_code'] = fields[1] if len(fields) > 1 else ''
                    result['message_control_id'] = fields[2] if len(fields) > 2 else ''
                    result['text_message'] = fields[3] if len(fields) > 3 else ''
                    result['is_valid'] = result['ack_code'] in ['AA', 'CA']

                elif fields[0] == 'ERR':
                    result['error_code'] = fields[1] if len(fields) > 1 else ''
                    result['error_message'] = fields[4] if len(fields) > 4 else ''

        except Exception as e:
            logger.error(f"Error parsing ACK message: {e}")
            result['error_message'] = str(e)

        return result

    def validate_message(self, message: str) -> dict:
        """
        Validate an HL7 message structure.

        Args:
            message: HL7 message string

        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'segment_count': 0,
        }

        try:
            segments = message.strip().split(self.SEGMENT_SEPARATOR)
            result['segment_count'] = len(segments)

            if not segments:
                result['is_valid'] = False
                result['errors'].append('Message is empty')
                return result

            # Check MSH segment
            msh = segments[0].split(self.FIELD_SEPARATOR)
            if msh[0] != 'MSH':
                result['is_valid'] = False
                result['errors'].append('Message must start with MSH segment')

            # Check for required segments
            segment_types = [s.split(self.FIELD_SEPARATOR)[0] for s in segments]

            if 'PID' not in segment_types:
                result['warnings'].append('PID segment not found')

            if 'OBR' not in segment_types:
                result['warnings'].append('OBR segment not found')

            if 'OBX' not in segment_types:
                result['warnings'].append('OBX segment not found')

        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f'Parse error: {e}')

        return result

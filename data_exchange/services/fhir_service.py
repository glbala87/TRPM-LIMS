# data_exchange/services/fhir_service.py
"""
FHIR R4 resource generation service.

Generates FHIR resources for laboratory results using the
Genomics Reporting Implementation Guide where applicable.
"""

import logging
import json
from datetime import datetime
from typing import Optional, List
import uuid

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class FHIRServiceError(Exception):
    """Exception raised for FHIR service errors."""
    pass


class FHIRService:
    """
    Service for generating FHIR R4 resources.

    Supports:
    - DiagnosticReport (genomics profile)
    - Observation (variants, interpretations)
    - Patient
    - Specimen
    - Bundle (for batch operations)
    """

    FHIR_VERSION = 'R4'
    LOINC_SYSTEM = 'http://loinc.org'
    SNOMED_SYSTEM = 'http://snomed.info/sct'
    HGVS_SYSTEM = 'http://varnomen.hgvs.org'

    # LOINC codes for genomic observations
    LOINC_CODES = {
        'diagnostic_report': '51969-4',  # Genetic analysis report
        'variant': '69548-6',  # Genetic variant assessment
        'gene_studied': '48018-6',  # Gene studied
        'variant_display': '81252-9',  # Discrete genetic variant
        'clinical_significance': '53037-8',  # Genetic disease analysis interpretation
        'allele_frequency': '81258-6',  # Allele frequency
    }

    def __init__(self, base_url: str = None):
        """
        Initialize FHIR service.

        Args:
            base_url: Optional base URL for resource references
        """
        self.base_url = base_url or getattr(
            settings, 'FHIR_BASE_URL',
            'http://localhost:8000/fhir'
        )

    def generate_diagnostic_report(self, molecular_result) -> dict:
        """
        Generate a FHIR DiagnosticReport for a molecular result.

        Uses the Genomics Reporting profile for NGS results.

        Args:
            molecular_result: MolecularResult instance

        Returns:
            FHIR DiagnosticReport resource dictionary
        """
        sample = molecular_result.sample
        patient = sample.lab_order.patient

        # Generate contained resources
        contained = []
        result_references = []

        # Add patient reference
        patient_resource = self._generate_patient(patient)
        patient_resource['id'] = 'patient1'
        contained.append(patient_resource)

        # Add specimen reference
        specimen_resource = self._generate_specimen(sample)
        specimen_resource['id'] = 'specimen1'
        contained.append(specimen_resource)

        # Generate observations for variants
        obs_index = 1
        for variant in molecular_result.variant_calls.select_related('gene').all():
            obs_resource = self._generate_variant_observation(variant)
            obs_resource['id'] = f'obs{obs_index}'
            contained.append(obs_resource)
            result_references.append({
                'reference': f'#obs{obs_index}'
            })
            obs_index += 1

        # Generate observations for PCR results
        for pcr in molecular_result.pcr_results.select_related('target_gene').all():
            obs_resource = self._generate_pcr_observation(pcr)
            obs_resource['id'] = f'obs{obs_index}'
            contained.append(obs_resource)
            result_references.append({
                'reference': f'#obs{obs_index}'
            })
            obs_index += 1

        # Determine status
        status_map = {
            'PENDING': 'registered',
            'PRELIMINARY': 'preliminary',
            'FINAL': 'final',
            'AMENDED': 'amended',
            'CANCELLED': 'cancelled',
        }
        status = status_map.get(molecular_result.status, 'final')

        # Build DiagnosticReport
        report = {
            'resourceType': 'DiagnosticReport',
            'id': str(molecular_result.id),
            'meta': {
                'profile': [
                    'http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/genomics-report'
                ]
            },
            'contained': contained,
            'status': status,
            'category': [
                {
                    'coding': [
                        {
                            'system': self.LOINC_SYSTEM,
                            'code': 'GE',
                            'display': 'Genetics'
                        }
                    ]
                }
            ],
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': self.LOINC_CODES['diagnostic_report'],
                        'display': 'Genetic analysis report'
                    }
                ],
                'text': molecular_result.test_panel.name
            },
            'subject': {
                'reference': '#patient1'
            },
            'effectiveDateTime': self._format_datetime(
                sample.collection_datetime or molecular_result.created_at
            ),
            'issued': self._format_datetime(
                molecular_result.approved_at or timezone.now()
            ),
            'specimen': [
                {
                    'reference': '#specimen1'
                }
            ],
            'result': result_references,
        }

        # Add performer
        if molecular_result.performed_by:
            report['performer'] = [
                {
                    'display': molecular_result.performed_by.get_full_name()
                }
            ]

        # Add conclusion
        if molecular_result.clinical_significance:
            report['conclusion'] = molecular_result.clinical_significance

        # Add interpretation code
        if molecular_result.interpretation:
            interp_codes = {
                'POSITIVE': {'code': 'POS', 'display': 'Positive'},
                'NEGATIVE': {'code': 'NEG', 'display': 'Negative'},
                'INDETERMINATE': {'code': 'IND', 'display': 'Indeterminate'},
            }
            interp = interp_codes.get(molecular_result.interpretation, {})
            if interp:
                report['conclusionCode'] = [
                    {
                        'coding': [
                            {
                                'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
                                'code': interp['code'],
                                'display': interp['display']
                            }
                        ]
                    }
                ]

        return report

    def _generate_patient(self, patient) -> dict:
        """Generate FHIR Patient resource."""
        resource = {
            'resourceType': 'Patient',
            'identifier': [
                {
                    'system': f'{self.base_url}/patient-id',
                    'value': str(patient.OP_NO or patient.id)
                }
            ],
            'name': [
                {
                    'use': 'official',
                    'family': patient.last_name,
                    'given': [patient.first_name]
                }
            ],
        }

        # Add date of birth
        if patient.date_of_birth:
            resource['birthDate'] = patient.date_of_birth.strftime('%Y-%m-%d')

        # Add gender
        gender_map = {'M': 'male', 'F': 'female', 'O': 'other', 'U': 'unknown'}
        resource['gender'] = gender_map.get(patient.gender, 'unknown')

        return resource

    def _generate_specimen(self, sample) -> dict:
        """Generate FHIR Specimen resource."""
        resource = {
            'resourceType': 'Specimen',
            'identifier': [
                {
                    'system': f'{self.base_url}/specimen-id',
                    'value': sample.sample_id
                }
            ],
            'status': 'available',
        }

        # Add specimen type
        if sample.sample_type:
            resource['type'] = {
                'coding': [
                    {
                        'system': self.SNOMED_SYSTEM,
                        'display': str(sample.sample_type)
                    }
                ],
                'text': str(sample.sample_type)
            }

        # Add collection info
        if sample.collection_datetime:
            resource['collection'] = {
                'collectedDateTime': self._format_datetime(sample.collection_datetime)
            }

        # Add received time
        if sample.received_datetime:
            resource['receivedTime'] = self._format_datetime(sample.received_datetime)

        return resource

    def _generate_variant_observation(self, variant) -> dict:
        """Generate FHIR Observation for a variant."""
        resource = {
            'resourceType': 'Observation',
            'meta': {
                'profile': [
                    'http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant'
                ]
            },
            'status': 'final',
            'category': [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                            'code': 'laboratory'
                        }
                    ]
                }
            ],
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': self.LOINC_CODES['variant'],
                        'display': 'Genetic variant assessment'
                    }
                ]
            },
            'component': []
        }

        # Add gene studied
        if variant.gene:
            resource['component'].append({
                'code': {
                    'coding': [
                        {
                            'system': self.LOINC_SYSTEM,
                            'code': self.LOINC_CODES['gene_studied'],
                            'display': 'Gene studied'
                        }
                    ]
                },
                'valueCodeableConcept': {
                    'coding': [
                        {
                            'system': 'http://www.genenames.org',
                            'display': variant.gene.symbol
                        }
                    ],
                    'text': variant.gene.symbol
                }
            })

        # Add HGVS notation
        if variant.hgvs_c:
            resource['component'].append({
                'code': {
                    'coding': [
                        {
                            'system': self.LOINC_SYSTEM,
                            'code': '48004-6',
                            'display': 'DNA change (c.HGVS)'
                        }
                    ]
                },
                'valueCodeableConcept': {
                    'coding': [
                        {
                            'system': self.HGVS_SYSTEM,
                            'code': variant.hgvs_c
                        }
                    ]
                }
            })

        if variant.hgvs_p:
            resource['component'].append({
                'code': {
                    'coding': [
                        {
                            'system': self.LOINC_SYSTEM,
                            'code': '48005-3',
                            'display': 'Amino acid change (p.HGVS)'
                        }
                    ]
                },
                'valueCodeableConcept': {
                    'coding': [
                        {
                            'system': self.HGVS_SYSTEM,
                            'code': variant.hgvs_p
                        }
                    ]
                }
            })

        # Add chromosome and position
        resource['component'].append({
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': '48000-4',
                        'display': 'Chromosome'
                    }
                ]
            },
            'valueCodeableConcept': {
                'text': f'chr{variant.chromosome}'
            }
        })

        resource['component'].append({
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': '69547-8',
                        'display': 'Genomic ref allele'
                    }
                ]
            },
            'valueString': variant.ref_allele
        })

        resource['component'].append({
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': '69551-0',
                        'display': 'Genomic alt allele'
                    }
                ]
            },
            'valueString': variant.alt_allele
        })

        # Add clinical significance
        if variant.classification:
            significance_map = {
                'PATHOGENIC': 'LA6668-3',
                'LIKELY_PATHOGENIC': 'LA26332-9',
                'VUS': 'LA26333-7',
                'LIKELY_BENIGN': 'LA26334-5',
                'BENIGN': 'LA6675-8',
            }
            loinc_code = significance_map.get(variant.classification)
            if loinc_code:
                resource['component'].append({
                    'code': {
                        'coding': [
                            {
                                'system': self.LOINC_SYSTEM,
                                'code': self.LOINC_CODES['clinical_significance'],
                                'display': 'Clinical significance'
                            }
                        ]
                    },
                    'valueCodeableConcept': {
                        'coding': [
                            {
                                'system': self.LOINC_SYSTEM,
                                'code': loinc_code,
                                'display': variant.get_classification_display()
                            }
                        ]
                    }
                })

        # Add allele frequency
        if variant.population_frequency:
            resource['component'].append({
                'code': {
                    'coding': [
                        {
                            'system': self.LOINC_SYSTEM,
                            'code': self.LOINC_CODES['allele_frequency'],
                            'display': 'Population allele frequency'
                        }
                    ]
                },
                'valueQuantity': {
                    'value': float(variant.population_frequency),
                    'unit': 'decimal',
                    'system': 'http://unitsofmeasure.org',
                    'code': '1'
                }
            })

        return resource

    def _generate_pcr_observation(self, pcr_result) -> dict:
        """Generate FHIR Observation for a PCR result."""
        resource = {
            'resourceType': 'Observation',
            'status': 'final',
            'category': [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                            'code': 'laboratory'
                        }
                    ]
                }
            ],
            'code': {
                'coding': [
                    {
                        'system': self.LOINC_SYSTEM,
                        'code': '94500-6',  # SARS-CoV-2 RT-PCR (example)
                        'display': f'{pcr_result.target_gene.symbol if pcr_result.target_gene else "Target"} Detection'
                    }
                ],
                'text': f'{pcr_result.target_gene.symbol if pcr_result.target_gene else "Target"} PCR'
            },
        }

        # Add value
        if pcr_result.is_detected:
            detection_map = {
                'DETECTED': {'code': '260373001', 'display': 'Detected'},
                'NOT_DETECTED': {'code': '260415000', 'display': 'Not detected'},
                'INDETERMINATE': {'code': '82334004', 'display': 'Indeterminate'},
            }
            detection = detection_map.get(pcr_result.is_detected, {})
            resource['valueCodeableConcept'] = {
                'coding': [
                    {
                        'system': self.SNOMED_SYSTEM,
                        'code': detection.get('code', ''),
                        'display': detection.get('display', pcr_result.is_detected)
                    }
                ]
            }

        # Add interpretation
        if pcr_result.is_detected == 'DETECTED':
            resource['interpretation'] = [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
                            'code': 'POS',
                            'display': 'Positive'
                        }
                    ]
                }
            ]
        elif pcr_result.is_detected == 'NOT_DETECTED':
            resource['interpretation'] = [
                {
                    'coding': [
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
                            'code': 'NEG',
                            'display': 'Negative'
                        }
                    ]
                }
            ]

        return resource

    def generate_bundle(
        self,
        resources: List[dict],
        bundle_type: str = 'collection'
    ) -> dict:
        """
        Generate a FHIR Bundle containing multiple resources.

        Args:
            resources: List of FHIR resource dictionaries
            bundle_type: Bundle type (collection, transaction, batch)

        Returns:
            FHIR Bundle resource dictionary
        """
        bundle = {
            'resourceType': 'Bundle',
            'id': str(uuid.uuid4()),
            'type': bundle_type,
            'timestamp': self._format_datetime(timezone.now()),
            'entry': []
        }

        for resource in resources:
            entry = {
                'resource': resource,
            }

            # Add request for transaction bundles
            if bundle_type == 'transaction':
                resource_type = resource.get('resourceType', '')
                resource_id = resource.get('id', '')
                entry['request'] = {
                    'method': 'PUT' if resource_id else 'POST',
                    'url': f'{resource_type}/{resource_id}' if resource_id else resource_type
                }

            # Add fullUrl for references
            if resource.get('id'):
                entry['fullUrl'] = f"{self.base_url}/{resource['resourceType']}/{resource['id']}"

            bundle['entry'].append(entry)

        bundle['total'] = len(bundle['entry'])

        return bundle

    def _format_datetime(self, dt) -> str:
        """Format datetime for FHIR."""
        if dt is None:
            return timezone.now().isoformat()
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)

    def to_json(self, resource: dict, indent: int = 2) -> str:
        """Convert FHIR resource to JSON string."""
        return json.dumps(resource, indent=indent, default=str)

    def validate_resource(self, resource: dict) -> dict:
        """
        Basic validation of a FHIR resource.

        Args:
            resource: FHIR resource dictionary

        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
        }

        # Check required fields
        if 'resourceType' not in resource:
            result['is_valid'] = False
            result['errors'].append('Missing resourceType')

        # Resource-specific validation
        resource_type = resource.get('resourceType')

        if resource_type == 'DiagnosticReport':
            if 'status' not in resource:
                result['errors'].append('DiagnosticReport missing required status')
                result['is_valid'] = False
            if 'code' not in resource:
                result['errors'].append('DiagnosticReport missing required code')
                result['is_valid'] = False

        elif resource_type == 'Observation':
            if 'status' not in resource:
                result['errors'].append('Observation missing required status')
                result['is_valid'] = False
            if 'code' not in resource:
                result['errors'].append('Observation missing required code')
                result['is_valid'] = False

        elif resource_type == 'Patient':
            if 'identifier' not in resource and 'name' not in resource:
                result['warnings'].append('Patient should have identifier or name')

        return result

# pathology/services/staging_service.py
"""
TNM staging service for pathology reports.
"""

from typing import Dict, Tuple, Optional
from ..models import Pathology, TumorSite


class TNMStagingService:
    """
    Service for TNM staging calculations and validation.
    Based on AJCC 8th Edition staging guidelines.
    """

    # Simplified stage group mappings (site-specific rules apply in practice)
    # Format: {(T, N, M): stage_group}
    GENERIC_STAGE_MAPPING = {
        # Stage 0
        ('Tis', 'N0', 'M0'): '0',
        # Stage I
        ('T1', 'N0', 'M0'): 'I',
        ('T1a', 'N0', 'M0'): 'IA',
        ('T1b', 'N0', 'M0'): 'IA',
        ('T1c', 'N0', 'M0'): 'IB',
        ('T2', 'N0', 'M0'): 'IB',
        # Stage II
        ('T2a', 'N0', 'M0'): 'IIA',
        ('T2b', 'N0', 'M0'): 'IIA',
        ('T3', 'N0', 'M0'): 'IIB',
        # Stage III (with node involvement)
        ('T1', 'N1', 'M0'): 'IIIA',
        ('T2', 'N1', 'M0'): 'IIIA',
        ('T3', 'N1', 'M0'): 'IIIB',
        ('T4', 'N0', 'M0'): 'IIIB',
        ('T4', 'N1', 'M0'): 'IIIB',
        ('T1', 'N2', 'M0'): 'IIIB',
        ('T2', 'N2', 'M0'): 'IIIB',
        ('T3', 'N2', 'M0'): 'IIIC',
        ('T4', 'N2', 'M0'): 'IIIC',
        # Stage IV (any M1)
        ('T1', 'N0', 'M1'): 'IV',
        ('T2', 'N0', 'M1'): 'IV',
        ('T3', 'N0', 'M1'): 'IV',
        ('T4', 'N0', 'M1'): 'IV',
        ('T1', 'N1', 'M1'): 'IV',
        ('T2', 'N1', 'M1'): 'IV',
        ('T3', 'N1', 'M1'): 'IV',
        ('T4', 'N1', 'M1'): 'IV',
        ('T1', 'N2', 'M1'): 'IV',
        ('T2', 'N2', 'M1'): 'IV',
        ('T3', 'N2', 'M1'): 'IV',
        ('T4', 'N2', 'M1'): 'IV',
    }

    @classmethod
    def calculate_stage_group(
        cls,
        t_stage: str,
        n_stage: str,
        m_stage: str,
        tumor_site: Optional[TumorSite] = None,
    ) -> Tuple[str, str]:
        """
        Calculate AJCC stage group from TNM values.

        Args:
            t_stage: T stage (e.g., 'T1', 'T2a')
            n_stage: N stage (e.g., 'N0', 'N1')
            m_stage: M stage (e.g., 'M0', 'M1')
            tumor_site: Optional tumor site for site-specific staging

        Returns:
            Tuple of (stage_group, staging_notes)
        """
        # Handle unknown/not assessable stages
        if t_stage.startswith('TX') or n_stage.startswith('NX') or m_stage.startswith('MX'):
            return ('', 'Stage cannot be determined (missing TNM values)')

        # Normalize stages (remove substages for lookup)
        t_base = cls._normalize_stage(t_stage, 'T')
        n_base = cls._normalize_stage(n_stage, 'N')
        m_base = cls._normalize_stage(m_stage, 'M')

        # Try exact match first
        key = (t_stage, n_stage, m_stage)
        if key in cls.GENERIC_STAGE_MAPPING:
            return (cls.GENERIC_STAGE_MAPPING[key], '')

        # Try with base stages
        key = (t_base, n_base, m_base)
        if key in cls.GENERIC_STAGE_MAPPING:
            return (cls.GENERIC_STAGE_MAPPING[key], 'Stage derived from base TNM values')

        # Any M1 is Stage IV
        if m_stage.startswith('M1'):
            return ('IV', 'Any M1 disease is Stage IV')

        # Default fallback based on N status
        if n_stage.startswith('N0'):
            if t_stage in ('T1', 'T1a', 'T1b'):
                return ('I', 'Estimated stage based on T1 N0 M0')
            elif t_stage in ('T2', 'T2a', 'T2b'):
                return ('II', 'Estimated stage based on T2 N0 M0')
            elif t_stage in ('T3', 'T3a', 'T3b'):
                return ('II', 'Estimated stage based on T3 N0 M0')
            elif t_stage.startswith('T4'):
                return ('III', 'Estimated stage based on T4 N0 M0')
        elif n_stage.startswith('N1') or n_stage.startswith('N2') or n_stage.startswith('N3'):
            return ('III', 'Estimated stage based on node-positive disease')

        return ('', 'Unable to determine stage group')

    @classmethod
    def _normalize_stage(cls, stage: str, prefix: str) -> str:
        """Normalize stage to base value (e.g., T2a -> T2)."""
        if len(stage) > 2 and stage[2].isalpha():
            return stage[:2]
        return stage

    @classmethod
    def validate_tnm_values(
        cls,
        t_stage: str,
        n_stage: str,
        m_stage: str,
    ) -> Tuple[bool, list]:
        """
        Validate TNM values.

        Args:
            t_stage: T stage value
            n_stage: N stage value
            m_stage: M stage value

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Valid T stages
        valid_t = {'TX', 'T0', 'Tis', 'T1', 'T1a', 'T1b', 'T1c', 'T2', 'T2a', 'T2b',
                   'T3', 'T3a', 'T3b', 'T4', 'T4a', 'T4b'}
        if t_stage and t_stage not in valid_t:
            errors.append(f"Invalid T stage: {t_stage}")

        # Valid N stages
        valid_n = {'NX', 'N0', 'N1', 'N1a', 'N1b', 'N1c', 'N2', 'N2a', 'N2b', 'N2c',
                   'N3', 'N3a', 'N3b'}
        if n_stage and n_stage not in valid_n:
            errors.append(f"Invalid N stage: {n_stage}")

        # Valid M stages
        valid_m = {'MX', 'M0', 'M1', 'M1a', 'M1b', 'M1c'}
        if m_stage and m_stage not in valid_m:
            errors.append(f"Invalid M stage: {m_stage}")

        return (len(errors) == 0, errors)

    @classmethod
    def get_staging_summary(cls, pathology: Pathology) -> Dict:
        """
        Get comprehensive staging summary for a pathology report.

        Args:
            pathology: Pathology instance

        Returns:
            Dictionary with staging summary
        """
        summary = {
            'pathological': {
                't_stage': pathology.t_stage,
                'n_stage': pathology.n_stage,
                'm_stage': pathology.m_stage,
                'tnm': pathology.tnm_stage,
                'stage_group': pathology.stage_group,
            },
            'clinical': {
                't_stage': pathology.clinical_t_stage,
                'n_stage': pathology.clinical_n_stage,
                'm_stage': pathology.clinical_m_stage,
                'tnm': pathology.clinical_tnm_stage,
                'stage_group': pathology.clinical_stage_group,
            },
            'grade': pathology.grade,
            'staging_system': pathology.staging_system,
            'margin_status': pathology.margin_status,
            'lymph_nodes': {
                'examined': pathology.lymph_nodes_examined,
                'positive': pathology.lymph_nodes_positive,
                'ratio': pathology.lymph_node_ratio,
            },
            'invasion': {
                'lymphovascular': pathology.lymphovascular_invasion,
                'perineural': pathology.perineural_invasion,
            },
        }

        # Calculate stage if not set
        if not pathology.stage_group and pathology.t_stage and pathology.n_stage and pathology.m_stage:
            calculated_stage, notes = cls.calculate_stage_group(
                pathology.t_stage,
                pathology.n_stage,
                pathology.m_stage,
                pathology.tumor_site
            )
            summary['calculated_stage'] = {
                'stage_group': calculated_stage,
                'notes': notes,
            }

        return summary

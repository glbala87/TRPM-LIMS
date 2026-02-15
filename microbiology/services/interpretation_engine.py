# microbiology/services/interpretation_engine.py
"""
AST Interpretation Engine for automated susceptibility interpretation.
"""

from decimal import Decimal
from typing import Optional, List, Dict, Tuple
from django.db.models import Q, Count
from django.utils import timezone

from ..models import (
    Organism, Antibiotic, Breakpoint, ASTGuideline,
    ASTResult, OrganismResult, ASTPanel
)


class ASTInterpretationEngine:
    """
    Engine for interpreting antimicrobial susceptibility test results.
    Supports MIC and disk diffusion interpretation against CLSI/EUCAST guidelines.
    """

    def __init__(self, guideline: Optional[ASTGuideline] = None):
        """
        Initialize the interpretation engine.

        Args:
            guideline: Specific guideline to use. If None, uses current active guideline.
        """
        self.guideline = guideline or self._get_current_guideline()

    def _get_current_guideline(self) -> Optional[ASTGuideline]:
        """Get the current active CLSI guideline."""
        return ASTGuideline.objects.filter(
            is_current=True,
            is_active=True
        ).first()

    def interpret_result(
        self,
        organism: Organism,
        antibiotic: Antibiotic,
        raw_value: str,
        test_method: str = 'MIC',
        host: Optional[str] = None,
        site_of_infection: Optional[str] = None,
    ) -> Tuple[str, Optional[Breakpoint]]:
        """
        Interpret a raw AST value and return the interpretation.

        Args:
            organism: The organism tested
            antibiotic: The antibiotic tested
            raw_value: Raw MIC or zone diameter value (e.g., "<=0.5", ">=32", "22")
            test_method: 'MIC' or 'DISK'
            host: Optional host type for veterinary breakpoints
            site_of_infection: Optional site of infection

        Returns:
            Tuple of (interpretation_code, breakpoint_used)
            interpretation_code: 'S', 'I', 'R', 'SDD', 'NS', or 'NI'
        """
        # Parse the raw value
        numeric_value = self._parse_raw_value(raw_value)
        if numeric_value is None:
            return ('NI', None)

        # Find applicable breakpoint
        breakpoint = self.get_applicable_breakpoint(
            organism=organism,
            antibiotic=antibiotic,
            test_method=test_method,
            host=host,
            site_of_infection=site_of_infection
        )

        if not breakpoint:
            return ('NI', None)

        # Interpret based on test method
        if test_method == 'MIC':
            interpretation = breakpoint.interpret_mic(numeric_value)
        else:
            interpretation = breakpoint.interpret_disk(numeric_value)

        return (interpretation or 'NI', breakpoint)

    def _parse_raw_value(self, raw_value: str) -> Optional[Decimal]:
        """
        Parse a raw MIC or zone diameter value.
        Handles modifiers like <=, >=, <, >.
        """
        if not raw_value:
            return None

        raw_value = raw_value.strip().upper()

        # Handle special values
        if raw_value in ('NG', 'NO GROWTH', '-'):
            return None

        # Remove modifiers
        for prefix in ('<=', '>=', '<', '>', '='):
            if raw_value.startswith(prefix):
                raw_value = raw_value[len(prefix):]
                break

        try:
            return Decimal(raw_value)
        except Exception:
            return None

    def get_applicable_breakpoint(
        self,
        organism: Organism,
        antibiotic: Antibiotic,
        test_method: str = 'MIC',
        host: Optional[str] = None,
        site_of_infection: Optional[str] = None,
    ) -> Optional[Breakpoint]:
        """
        Find the most applicable breakpoint for an organism-antibiotic combination.
        Searches from most specific to least specific.
        """
        if not self.guideline:
            return None

        # Build base query
        base_query = Q(
            guideline=self.guideline,
            antibiotic=antibiotic,
            test_method__code=test_method,
            is_active=True
        )

        # Try organism-specific breakpoint first
        breakpoints = Breakpoint.objects.filter(
            base_query,
            organism=organism
        )

        # Filter by host and site if provided
        if host:
            breakpoints = breakpoints.filter(
                Q(host__code=host) | Q(host__isnull=True)
            )
        if site_of_infection:
            breakpoints = breakpoints.filter(
                Q(site_of_infection__code=site_of_infection) | Q(site_of_infection__isnull=True)
            )

        breakpoint = breakpoints.first()
        if breakpoint:
            return breakpoint

        # Try genus-level breakpoint
        if organism.genus:
            breakpoints = Breakpoint.objects.filter(
                base_query,
                organism_group__icontains=organism.genus.name
            )
            breakpoint = breakpoints.first()
            if breakpoint:
                return breakpoint

        # Try family-level breakpoint
        if organism.family:
            breakpoints = Breakpoint.objects.filter(
                base_query,
                organism_group__icontains=organism.family.name
            )
            breakpoint = breakpoints.first()
            if breakpoint:
                return breakpoint

        # Try broader organism groups
        group_names = [
            'Enterobacteriaceae',
            'Enterobacterales',
            'Pseudomonas',
            'Staphylococcus',
            'Streptococcus',
            'Enterococcus',
        ]

        for group in group_names:
            if organism.full_name.lower().startswith(group.lower()):
                breakpoints = Breakpoint.objects.filter(
                    base_query,
                    organism_group__icontains=group
                )
                breakpoint = breakpoints.first()
                if breakpoint:
                    return breakpoint

        return None

    def interpret_organism_result(
        self,
        organism_result: OrganismResult,
        ast_panel: Optional[ASTPanel] = None,
    ) -> List[Dict]:
        """
        Interpret all AST results for an organism isolate.

        Args:
            organism_result: The organism result to interpret
            ast_panel: Optional panel to use for antibiotic selection

        Returns:
            List of interpretation results
        """
        results = []

        ast_results = organism_result.ast_results.select_related(
            'antibiotic', 'breakpoint_used'
        )

        for ast_result in ast_results:
            if ast_result.is_manual_override:
                # Keep manual override
                results.append({
                    'antibiotic': ast_result.antibiotic,
                    'interpretation': ast_result.interpretation,
                    'breakpoint': ast_result.breakpoint_used,
                    'is_override': True,
                })
            else:
                # Re-interpret
                interpretation, breakpoint = self.interpret_result(
                    organism=organism_result.organism,
                    antibiotic=ast_result.antibiotic,
                    raw_value=ast_result.raw_value,
                    test_method=ast_result.test_method,
                )

                # Update the result
                ast_result.interpretation = interpretation
                ast_result.interpretation_guideline = self.guideline
                ast_result.breakpoint_used = breakpoint
                ast_result.save()

                results.append({
                    'antibiotic': ast_result.antibiotic,
                    'interpretation': interpretation,
                    'breakpoint': breakpoint,
                    'is_override': False,
                })

        return results

    def generate_antibiogram(
        self,
        laboratory_id: int,
        organisms: Optional[List[Organism]] = None,
        antibiotics: Optional[List[Antibiotic]] = None,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        specimen_types: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate cumulative antibiogram data.

        Args:
            laboratory_id: Laboratory to generate antibiogram for
            organisms: Specific organisms to include (optional)
            antibiotics: Specific antibiotics to include (optional)
            start_date: Start of date range (default: 1 year ago)
            end_date: End of date range (default: now)
            specimen_types: Specific specimen types to include (optional)

        Returns:
            Antibiogram data structure
        """
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timezone.timedelta(days=365)

        # Build base query
        results_query = ASTResult.objects.filter(
            organism_result__sample__laboratory_id=laboratory_id,
            organism_result__sample__received_datetime__gte=start_date,
            organism_result__sample__received_datetime__lte=end_date,
            organism_result__is_significant=True,
            organism_result__is_contaminant=False,
        )

        if organisms:
            results_query = results_query.filter(
                organism_result__organism__in=organisms
            )

        if antibiotics:
            results_query = results_query.filter(antibiotic__in=antibiotics)

        if specimen_types:
            results_query = results_query.filter(
                organism_result__sample__specimen_type__in=specimen_types
            )

        # Aggregate results
        aggregation = results_query.values(
            'organism_result__organism__id',
            'organism_result__organism__genus__name',
            'organism_result__organism__species',
            'antibiotic__id',
            'antibiotic__abbreviation',
            'antibiotic__name',
        ).annotate(
            total=Count('id'),
            susceptible=Count('id', filter=Q(interpretation='S')),
            intermediate=Count('id', filter=Q(interpretation__in=['I', 'SDD'])),
            resistant=Count('id', filter=Q(interpretation='R')),
        )

        # Structure the data
        antibiogram = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'data': [],
        }

        for row in aggregation:
            if row['total'] >= 30:  # Minimum sample size for reporting
                susceptibility_rate = (row['susceptible'] / row['total']) * 100

                antibiogram['data'].append({
                    'organism': {
                        'id': row['organism_result__organism__id'],
                        'name': f"{row['organism_result__organism__genus__name']} {row['organism_result__organism__species']}",
                    },
                    'antibiotic': {
                        'id': row['antibiotic__id'],
                        'abbreviation': row['antibiotic__abbreviation'],
                        'name': row['antibiotic__name'],
                    },
                    'total': row['total'],
                    'susceptible': row['susceptible'],
                    'intermediate': row['intermediate'],
                    'resistant': row['resistant'],
                    'susceptibility_rate': round(susceptibility_rate, 1),
                })

        return antibiogram

    def check_resistance_patterns(
        self,
        organism_result: OrganismResult,
    ) -> List[Dict]:
        """
        Check for known resistance patterns (e.g., ESBL, MRSA, VRE).

        Args:
            organism_result: The organism result to check

        Returns:
            List of detected resistance patterns
        """
        patterns = []
        ast_results = {
            r.antibiotic.abbreviation: r.interpretation
            for r in organism_result.ast_results.select_related('antibiotic')
        }

        organism_name = organism_result.organism.full_name.lower()

        # MRSA detection
        if 'staphylococcus aureus' in organism_name:
            if ast_results.get('OXA') == 'R' or ast_results.get('FOX') == 'R':
                patterns.append({
                    'code': 'MRSA',
                    'name': 'Methicillin-Resistant Staphylococcus aureus',
                    'antibiotics': ['OXA', 'FOX'],
                    'action': 'Report as MRSA. All beta-lactams considered resistant.',
                })

        # VRE detection
        if 'enterococcus' in organism_name:
            if ast_results.get('VAN') == 'R':
                patterns.append({
                    'code': 'VRE',
                    'name': 'Vancomycin-Resistant Enterococcus',
                    'antibiotics': ['VAN'],
                    'action': 'Report as VRE. Consider infection control notification.',
                })

        # ESBL detection (simplified)
        enterobacterales = ['escherichia', 'klebsiella', 'enterobacter', 'citrobacter']
        if any(name in organism_name for name in enterobacterales):
            ceph_resistance = [
                ast_results.get(abx) == 'R'
                for abx in ['CTX', 'CAZ', 'CRO', 'FEP']
                if abx in ast_results
            ]
            if any(ceph_resistance):
                patterns.append({
                    'code': 'ESBL_SUSPECT',
                    'name': 'Possible ESBL Producer',
                    'antibiotics': ['CTX', 'CAZ', 'CRO', 'FEP'],
                    'action': 'Confirm with ESBL testing. If positive, report cephalosporins and aztreonam as resistant.',
                })

        # CRE detection
        if any(name in organism_name for name in enterobacterales):
            carb_resistance = [
                ast_results.get(abx) == 'R'
                for abx in ['MEM', 'IPM', 'ETP', 'DOR']
                if abx in ast_results
            ]
            if any(carb_resistance):
                patterns.append({
                    'code': 'CRE',
                    'name': 'Carbapenem-Resistant Enterobacterales',
                    'antibiotics': ['MEM', 'IPM', 'ETP', 'DOR'],
                    'action': 'Report as CRE. Mandatory notification required.',
                })

        return patterns

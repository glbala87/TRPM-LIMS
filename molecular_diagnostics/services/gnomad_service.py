# molecular_diagnostics/services/gnomad_service.py
"""
gnomAD API integration service using GraphQL.

Provides methods to query gnomAD for population allele frequencies,
gene constraint metrics, and variant quality flags.
"""

import logging
import time
from typing import Optional

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GnomADServiceError(Exception):
    """Exception raised for gnomAD API errors."""
    pass


class GnomADService:
    """
    Service for querying gnomAD via GraphQL API.

    gnomAD v4 API endpoint: https://gnomad.broadinstitute.org/api
    Supports GRCh38 coordinates.
    """

    API_URL = "https://gnomad.broadinstitute.org/api"

    # Rate limiting - be conservative
    MIN_REQUEST_INTERVAL = 0.5  # 500ms between requests

    # Population codes
    POPULATIONS = {
        'afr': 'African/African American',
        'amr': 'Latino/Admixed American',
        'asj': 'Ashkenazi Jewish',
        'eas': 'East Asian',
        'fin': 'Finnish',
        'mid': 'Middle Eastern',
        'nfe': 'Non-Finnish European',
        'sas': 'South Asian',
        'remaining': 'Remaining',
    }

    def __init__(self):
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, query: str, variables: dict = None, retries: int = 3) -> dict:
        """Make a GraphQL request to gnomAD API."""
        payload = {'query': query}
        if variables:
            payload['variables'] = variables

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        for attempt in range(retries):
            try:
                self._rate_limit()
                response = requests.post(
                    self.API_URL,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()

                data = response.json()

                if 'errors' in data:
                    errors = data['errors']
                    error_msg = '; '.join(e.get('message', str(e)) for e in errors)
                    logger.warning(f"gnomAD GraphQL errors: {error_msg}")
                    # Some errors are non-fatal (e.g., variant not found)
                    if not data.get('data'):
                        raise GnomADServiceError(f"GraphQL errors: {error_msg}")

                return data.get('data', {})

            except requests.RequestException as e:
                logger.warning(f"gnomAD request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise GnomADServiceError(f"Failed to query gnomAD: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def get_variant(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        dataset: str = "gnomad_r4"
    ) -> Optional[dict]:
        """
        Query gnomAD for a specific variant.

        Args:
            chromosome: Chromosome (e.g., "1", "X")
            position: Genomic position (GRCh38)
            ref: Reference allele
            alt: Alternate allele
            dataset: gnomAD dataset version

        Returns:
            Dictionary with variant data or None if not found
        """
        # Normalize chromosome
        chrom = chromosome.replace('chr', '').upper()
        if chrom == '23':
            chrom = 'X'
        elif chrom == '24':
            chrom = 'Y'

        # Build variant ID
        variant_id = f"{chrom}-{position}-{ref}-{alt}"

        # Check cache
        cache_key = f"gnomad_variant_{variant_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached if cached else None

        query = """
        query GnomadVariant($variantId: String!, $datasetId: DatasetId!) {
            variant(variantId: $variantId, dataset: $datasetId) {
                variant_id
                reference_genome
                chrom
                pos
                ref
                alt
                rsids
                exome {
                    ac
                    an
                    af
                    ac_hom
                    populations {
                        id
                        ac
                        an
                        af
                        ac_hom
                    }
                    filters
                }
                genome {
                    ac
                    an
                    af
                    ac_hom
                    populations {
                        id
                        ac
                        an
                        af
                        ac_hom
                    }
                    filters
                }
                flags
                transcript_consequences {
                    gene_id
                    gene_symbol
                    transcript_id
                    consequence
                    hgvsc
                    hgvsp
                    is_canonical
                    lof
                    lof_filter
                    lof_flags
                }
            }
        }
        """

        variables = {
            'variantId': variant_id,
            'datasetId': dataset
        }

        try:
            data = self._make_request(query, variables)
            variant_data = data.get('variant')

            if variant_data:
                result = self._parse_variant_response(variant_data)
                cache.set(cache_key, result, 3600)  # Cache for 1 hour
                return result

            # Cache negative result briefly
            cache.set(cache_key, False, 300)  # Cache for 5 minutes
            return None

        except GnomADServiceError:
            return None

    def _parse_variant_response(self, variant_data: dict) -> dict:
        """Parse gnomAD variant response into structured data."""
        result = {
            'variant_id': variant_data.get('variant_id', ''),
            'rsids': variant_data.get('rsids', []),
            'flags': variant_data.get('flags', []),
            'genome': {},
            'exome': {},
            'populations': {},
            'transcript_consequences': [],
            'gene_constraint': {},
        }

        # Parse genome data
        genome = variant_data.get('genome')
        if genome:
            result['genome'] = {
                'ac': genome.get('ac'),
                'an': genome.get('an'),
                'af': genome.get('af'),
                'homozygotes': genome.get('ac_hom'),
                'filters': genome.get('filters', []),
            }

            # Parse population frequencies
            for pop in genome.get('populations', []):
                pop_id = pop.get('id', '').lower()
                if pop_id and pop.get('af') is not None:
                    result['populations'][f"genome_{pop_id}"] = pop.get('af')

        # Parse exome data
        exome = variant_data.get('exome')
        if exome:
            result['exome'] = {
                'ac': exome.get('ac'),
                'an': exome.get('an'),
                'af': exome.get('af'),
                'homozygotes': exome.get('ac_hom'),
                'filters': exome.get('filters', []),
            }

            # Parse population frequencies
            for pop in exome.get('populations', []):
                pop_id = pop.get('id', '').lower()
                if pop_id and pop.get('af') is not None:
                    result['populations'][f"exome_{pop_id}"] = pop.get('af')

        # Combine populations for simpler access
        combined_pops = {}
        for key, value in result['populations'].items():
            pop_name = key.split('_')[-1]
            if pop_name not in combined_pops:
                combined_pops[pop_name] = value
            else:
                # Take max of genome/exome
                if value and (combined_pops[pop_name] is None or value > combined_pops[pop_name]):
                    combined_pops[pop_name] = value
        result['populations'] = combined_pops

        # Parse transcript consequences
        for conseq in variant_data.get('transcript_consequences', []):
            result['transcript_consequences'].append({
                'gene_id': conseq.get('gene_id', ''),
                'gene_symbol': conseq.get('gene_symbol', ''),
                'transcript_id': conseq.get('transcript_id', ''),
                'consequence': conseq.get('consequence', ''),
                'hgvsc': conseq.get('hgvsc', ''),
                'hgvsp': conseq.get('hgvsp', ''),
                'is_canonical': conseq.get('is_canonical', False),
                'lof': conseq.get('lof', ''),
                'lof_filter': conseq.get('lof_filter', ''),
            })

        return result

    def get_gene_constraint(self, gene_symbol: str, dataset: str = "gnomad_r4") -> Optional[dict]:
        """
        Get gene constraint metrics from gnomAD.

        Args:
            gene_symbol: Gene symbol (e.g., "BRCA1")
            dataset: gnomAD dataset version

        Returns:
            Dictionary with constraint metrics or None
        """
        # Check cache
        cache_key = f"gnomad_constraint_{gene_symbol}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached if cached else None

        query = """
        query GnomadGeneConstraint($geneSymbol: String!, $datasetId: DatasetId!) {
            gene(gene_symbol: $geneSymbol, reference_genome: GRCh38) {
                gene_id
                symbol
                name
                gnomad_constraint(dataset: $datasetId) {
                    exp_lof
                    exp_mis
                    exp_syn
                    obs_lof
                    obs_mis
                    obs_syn
                    oe_lof
                    oe_lof_lower
                    oe_lof_upper
                    oe_mis
                    oe_syn
                    lof_z
                    mis_z
                    syn_z
                    pLI
                    flags
                }
            }
        }
        """

        variables = {
            'geneSymbol': gene_symbol.upper(),
            'datasetId': dataset
        }

        try:
            data = self._make_request(query, variables)
            gene_data = data.get('gene')

            if gene_data and gene_data.get('gnomad_constraint'):
                constraint = gene_data['gnomad_constraint']
                result = {
                    'gene_id': gene_data.get('gene_id', ''),
                    'symbol': gene_data.get('symbol', ''),
                    'name': gene_data.get('name', ''),
                    'pLI': constraint.get('pLI'),
                    'loeuf': constraint.get('oe_lof_upper'),  # LOEUF = oe_lof upper bound
                    'oe_lof': constraint.get('oe_lof'),
                    'oe_mis': constraint.get('oe_mis'),
                    'oe_syn': constraint.get('oe_syn'),
                    'lof_z': constraint.get('lof_z'),
                    'mis_z': constraint.get('mis_z'),
                    'syn_z': constraint.get('syn_z'),
                    'exp_lof': constraint.get('exp_lof'),
                    'obs_lof': constraint.get('obs_lof'),
                    'flags': constraint.get('flags', []),
                }
                cache.set(cache_key, result, 86400)  # Cache for 24 hours
                return result

            cache.set(cache_key, False, 3600)
            return None

        except GnomADServiceError:
            return None

    def annotate_variant(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        gene_symbol: str = None
    ) -> Optional[dict]:
        """
        Full annotation workflow for a variant.

        Args:
            chromosome: Chromosome
            position: Genomic position (GRCh38)
            ref: Reference allele
            alt: Alternate allele
            gene_symbol: Optional gene symbol for constraint data

        Returns:
            Dictionary with gnomAD annotation data or None
        """
        result = self.get_variant(chromosome, position, ref, alt)

        if result and gene_symbol:
            # Add gene constraint if available
            constraint = self.get_gene_constraint(gene_symbol)
            if constraint:
                result['gene_constraint'] = constraint

        return result

    def batch_annotate(self, variants: list) -> dict:
        """
        Annotate multiple variants.

        Note: gnomAD GraphQL doesn't support batch variant queries efficiently,
        so this iterates through variants with rate limiting.

        Args:
            variants: List of variant dictionaries with keys:
                      chromosome, position, ref, alt, gene_symbol (optional)

        Returns:
            Dictionary mapping variant keys to annotation data
        """
        results = {}

        for i, variant in enumerate(variants):
            key = f"{variant['chromosome']}-{variant['position']}-{variant['ref']}-{variant['alt']}"

            try:
                annotation = self.annotate_variant(
                    chromosome=variant['chromosome'],
                    position=variant['position'],
                    ref=variant['ref'],
                    alt=variant['alt'],
                    gene_symbol=variant.get('gene_symbol')
                )
                results[key] = annotation

            except GnomADServiceError as e:
                logger.error(f"Error annotating variant {key}: {e}")
                results[key] = None

            # Log progress
            if (i + 1) % 10 == 0:
                logger.info(f"gnomAD batch progress: {i + 1}/{len(variants)}")

        return results

    def get_region_variants(
        self,
        chromosome: str,
        start: int,
        stop: int,
        dataset: str = "gnomad_r4"
    ) -> list:
        """
        Get all variants in a genomic region.

        Args:
            chromosome: Chromosome
            start: Start position
            stop: Stop position
            dataset: gnomAD dataset version

        Returns:
            List of variant data dictionaries
        """
        chrom = chromosome.replace('chr', '').upper()

        query = """
        query GnomadRegion($chrom: String!, $start: Int!, $stop: Int!, $datasetId: DatasetId!) {
            region(chrom: $chrom, start: $start, stop: $stop, reference_genome: GRCh38) {
                variants(dataset: $datasetId) {
                    variant_id
                    pos
                    ref
                    alt
                    rsids
                    exome {
                        ac
                        an
                        af
                    }
                    genome {
                        ac
                        an
                        af
                    }
                    flags
                }
            }
        }
        """

        variables = {
            'chrom': chrom,
            'start': start,
            'stop': stop,
            'datasetId': dataset
        }

        try:
            data = self._make_request(query, variables)
            region_data = data.get('region', {})
            variants = region_data.get('variants', [])

            return [
                {
                    'variant_id': v.get('variant_id', ''),
                    'position': v.get('pos'),
                    'ref': v.get('ref', ''),
                    'alt': v.get('alt', ''),
                    'rsids': v.get('rsids', []),
                    'genome_af': v.get('genome', {}).get('af'),
                    'exome_af': v.get('exome', {}).get('af'),
                    'flags': v.get('flags', []),
                }
                for v in variants
            ]

        except GnomADServiceError:
            return []

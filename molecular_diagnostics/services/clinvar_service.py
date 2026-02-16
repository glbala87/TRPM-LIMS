# molecular_diagnostics/services/clinvar_service.py
"""
ClinVar API integration service using NCBI E-utilities.

Provides methods to query ClinVar for variant annotations including:
- Clinical significance
- Review status
- Associated conditions
- Submitter information
"""

import logging
import time
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ClinVarServiceError(Exception):
    """Exception raised for ClinVar API errors."""
    pass


class ClinVarService:
    """
    Service for querying ClinVar via NCBI E-utilities.

    ClinVar API endpoints:
    - esearch: Search for variation IDs
    - efetch: Fetch detailed variation data
    - elink: Get related records

    Rate limiting: Without API key: 3 requests/second
                   With API key: 10 requests/second
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    DATABASE = "clinvar"

    # Rate limiting
    MIN_REQUEST_INTERVAL = 0.1  # 100ms between requests with API key
    MIN_REQUEST_INTERVAL_NO_KEY = 0.34  # ~3 requests/second without key

    def __init__(self):
        self.api_key = getattr(settings, 'NCBI_API_KEY', '')
        self.email = getattr(settings, 'NCBI_EMAIL', 'admin@trpm-lims.org')
        self.tool = 'TRPM-LIMS'
        self._last_request_time = 0

    def _get_request_interval(self):
        """Get the minimum interval between requests."""
        if self.api_key:
            return self.MIN_REQUEST_INTERVAL
        return self.MIN_REQUEST_INTERVAL_NO_KEY

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        interval = self._get_request_interval()
        elapsed = time.time() - self._last_request_time
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._last_request_time = time.time()

    def _build_params(self, **kwargs) -> dict:
        """Build common E-utilities parameters."""
        params = {
            'db': self.DATABASE,
            'tool': self.tool,
            'email': self.email,
        }
        if self.api_key:
            params['api_key'] = self.api_key
        params.update(kwargs)
        return params

    def _make_request(self, endpoint: str, params: dict, retries: int = 3) -> requests.Response:
        """Make a rate-limited request to NCBI E-utilities."""
        url = f"{self.BASE_URL}/{endpoint}"

        for attempt in range(retries):
            try:
                self._rate_limit()
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"ClinVar request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise ClinVarServiceError(f"Failed to query ClinVar: {e}")
                time.sleep(1)  # Wait before retry

    def search_variant(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        assembly: str = "GRCh38"
    ) -> Optional[str]:
        """
        Search for a variant in ClinVar by genomic coordinates.

        Args:
            chromosome: Chromosome (e.g., "1", "X")
            position: Genomic position
            ref: Reference allele
            alt: Alternate allele
            assembly: Genome assembly (GRCh37 or GRCh38)

        Returns:
            ClinVar Variation ID if found, None otherwise
        """
        # Build search term using variant notation
        # ClinVar accepts various formats
        chrom = chromosome.replace('chr', '')

        # Try multiple search strategies
        search_terms = [
            f"{chrom}[chr] AND {position}[chrpos38] AND {ref}>{alt}",
            f"{chrom}:{position} {ref}>{alt}",
            f"chr{chrom}:g.{position}{ref}>{alt}",
        ]

        for term in search_terms:
            result = self._search(term)
            if result:
                return result

        return None

    def search_by_rsid(self, rsid: str) -> Optional[str]:
        """
        Search for a variant by dbSNP rsID.

        Args:
            rsid: dbSNP ID (e.g., "rs12345" or "12345")

        Returns:
            ClinVar Variation ID if found, None otherwise
        """
        if not rsid:
            return None

        # Normalize rsID
        rsid = rsid.lower()
        if not rsid.startswith('rs'):
            rsid = f'rs{rsid}'

        return self._search(f"{rsid}[dbSNP]")

    def search_by_hgvs(self, hgvs: str) -> Optional[str]:
        """
        Search for a variant by HGVS notation.

        Args:
            hgvs: HGVS notation (e.g., "NM_001005484.2:c.34G>A")

        Returns:
            ClinVar Variation ID if found, None otherwise
        """
        if not hgvs:
            return None

        return self._search(hgvs)

    def _search(self, term: str) -> Optional[str]:
        """Execute a search query and return the first variation ID."""
        params = self._build_params(
            term=term,
            retmax=1,
            retmode='json'
        )

        try:
            response = self._make_request('esearch.fcgi', params)
            data = response.json()

            result = data.get('esearchresult', {})
            id_list = result.get('idlist', [])

            if id_list:
                return id_list[0]
            return None

        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing ClinVar search response: {e}")
            return None

    def fetch_variation(self, variation_id: str) -> Optional[dict]:
        """
        Fetch detailed variation data from ClinVar.

        Args:
            variation_id: ClinVar Variation ID

        Returns:
            Dictionary with variation data or None
        """
        if not variation_id:
            return None

        # Check cache first
        cache_key = f"clinvar_variation_{variation_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        params = self._build_params(
            id=variation_id,
            rettype='vcv',  # Variation Clinical View
            retmode='xml'
        )

        try:
            response = self._make_request('efetch.fcgi', params)
            data = self._parse_clinvar_xml(response.text)

            if data:
                # Cache for 1 hour
                cache.set(cache_key, data, 3600)

            return data

        except Exception as e:
            logger.error(f"Error fetching ClinVar variation {variation_id}: {e}")
            return None

    def _parse_clinvar_xml(self, xml_content: str) -> Optional[dict]:
        """Parse ClinVar XML response into structured data."""
        try:
            root = ET.fromstring(xml_content)

            # Find the VariationArchive element
            variation = root.find('.//VariationArchive')
            if variation is None:
                # Try alternative structure
                variation = root.find('.//ClinVarSet/ReferenceClinVarAssertion')
                if variation is None:
                    return None

            data = {
                'variation_id': variation.get('VariationID', variation.get('Accession', '')),
                'allele_id': '',
                'clinical_significance': '',
                'review_status': '',
                'review_stars': None,
                'conditions': [],
                'submitters': [],
                'submission_count': 0,
                'last_evaluated': '',
                'pubmed_ids': [],
            }

            # Get clinical significance
            interp = variation.find('.//InterpretedRecord/Interpretations/Interpretation')
            if interp is None:
                interp = variation.find('.//ClinicalSignificance')

            if interp is not None:
                desc = interp.find('Description')
                if desc is not None:
                    data['clinical_significance'] = desc.text or ''

                review = interp.find('ReviewStatus')
                if review is not None:
                    data['review_status'] = review.text or ''
                    data['review_stars'] = self._get_review_stars(review.text)

                last_eval = interp.get('DateLastEvaluated')
                if last_eval:
                    data['last_evaluated'] = last_eval

            # Get conditions/traits
            for trait in variation.findall('.//TraitSet/Trait'):
                trait_data = {
                    'name': '',
                    'medgen_id': '',
                    'trait_type': trait.get('Type', ''),
                }

                name = trait.find('Name/ElementValue')
                if name is not None:
                    trait_data['name'] = name.text or ''

                for xref in trait.findall('XRef'):
                    if xref.get('DB') == 'MedGen':
                        trait_data['medgen_id'] = xref.get('ID', '')
                        break

                if trait_data['name']:
                    data['conditions'].append(trait_data)

            # Get submitters
            for assertion in variation.findall('.//ClinicalAssertion'):
                submitter_data = {
                    'name': '',
                    'significance': '',
                    'date': '',
                }

                submitter = assertion.find('ClinVarSubmissionID')
                if submitter is not None:
                    submitter_data['name'] = submitter.get('submitter', '')

                sig = assertion.find('.//ClinicalSignificance/Description')
                if sig is not None:
                    submitter_data['significance'] = sig.text or ''

                date = assertion.find('.//ClinicalSignificance')
                if date is not None:
                    submitter_data['date'] = date.get('DateLastEvaluated', '')

                if submitter_data['name']:
                    data['submitters'].append(submitter_data)

            data['submission_count'] = len(data['submitters'])

            # Get PubMed IDs
            for citation in variation.findall('.//Citation/ID'):
                if citation.get('Source') == 'PubMed':
                    data['pubmed_ids'].append(citation.text)

            return data

        except ET.ParseError as e:
            logger.error(f"Error parsing ClinVar XML: {e}")
            return None

    def _get_review_stars(self, review_status: str) -> int:
        """Convert ClinVar review status to star rating."""
        if not review_status:
            return 0

        status_lower = review_status.lower()

        if 'practice guideline' in status_lower:
            return 4
        elif 'expert panel' in status_lower:
            return 3
        elif 'multiple submitters' in status_lower and 'no conflicts' in status_lower:
            return 2
        elif 'single submitter' in status_lower or 'criteria provided' in status_lower:
            return 1
        else:
            return 0

    def annotate_variant(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        rsid: str = None,
        hgvs: str = None
    ) -> Optional[dict]:
        """
        Full annotation workflow for a variant.

        Tries multiple search strategies in order:
        1. rsID lookup (fastest)
        2. HGVS notation lookup
        3. Genomic coordinates lookup

        Args:
            chromosome: Chromosome
            position: Genomic position
            ref: Reference allele
            alt: Alternate allele
            rsid: Optional dbSNP ID
            hgvs: Optional HGVS notation

        Returns:
            Dictionary with ClinVar annotation data or None
        """
        variation_id = None

        # Try rsID first (most reliable)
        if rsid:
            variation_id = self.search_by_rsid(rsid)

        # Try HGVS notation
        if not variation_id and hgvs:
            variation_id = self.search_by_hgvs(hgvs)

        # Try genomic coordinates
        if not variation_id:
            variation_id = self.search_variant(chromosome, position, ref, alt)

        if not variation_id:
            logger.info(f"Variant not found in ClinVar: {chromosome}:{position}{ref}>{alt}")
            return None

        return self.fetch_variation(variation_id)

    def batch_annotate(self, variants: list, batch_size: int = 50) -> dict:
        """
        Annotate multiple variants in batch.

        Args:
            variants: List of variant dictionaries with keys:
                      chromosome, position, ref, alt, rsid (optional), hgvs (optional)
            batch_size: Number of variants to process at once

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
                    rsid=variant.get('rsid'),
                    hgvs=variant.get('hgvs')
                )
                results[key] = annotation

            except ClinVarServiceError as e:
                logger.error(f"Error annotating variant {key}: {e}")
                results[key] = None

            # Log progress for large batches
            if (i + 1) % 10 == 0:
                logger.info(f"ClinVar batch progress: {i + 1}/{len(variants)}")

        return results

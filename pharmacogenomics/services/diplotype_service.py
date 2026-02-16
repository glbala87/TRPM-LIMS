# pharmacogenomics/services/diplotype_service.py
"""
Diplotype calling service for pharmacogenes.

Calls star alleles from detected variants and calculates activity scores.
"""

import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from pharmacogenomics.models import (
    PGxGene, StarAllele, Phenotype, PGxResult, PGxPanel
)

logger = logging.getLogger(__name__)


class DiplotypeServiceError(Exception):
    """Exception raised for diplotype calling errors."""
    pass


class DiplotypeService:
    """
    Service for calling diplotypes from variant data.

    Supports:
    - Star allele calling based on defining variants
    - Activity score calculation
    - Phenotype assignment
    - Copy number variation handling (e.g., CYP2D6)
    """

    def __init__(self):
        self._allele_cache = {}

    def call_diplotype(
        self,
        molecular_result,
        gene: PGxGene,
        panel: PGxPanel = None,
        auto_phenotype: bool = True
    ) -> PGxResult:
        """
        Call diplotype for a gene from molecular result variants.

        Args:
            molecular_result: MolecularResult instance
            gene: PGxGene to call
            panel: Optional PGxPanel
            auto_phenotype: Automatically assign phenotype

        Returns:
            PGxResult instance
        """
        # Get or create PGx result
        pgx_result, created = PGxResult.objects.get_or_create(
            molecular_result=molecular_result,
            gene=gene,
            defaults={
                'panel': panel,
                'status': 'CALLING',
                'calling_method': 'variant_matching',
            }
        )

        if not created:
            pgx_result.status = 'CALLING'
            pgx_result.save(update_fields=['status'])

        try:
            # Get variants for this gene
            gene_variants = self._get_gene_variants(molecular_result, gene)
            pgx_result.detected_variants = gene_variants

            # Call alleles
            allele1, allele2, confidence = self._call_alleles(gene, gene_variants)

            pgx_result.allele1 = allele1
            pgx_result.allele2 = allele2
            pgx_result.diplotype = f"{allele1.name}/{allele2.name}" if allele1 and allele2 else ""
            pgx_result.calling_confidence = confidence

            # Check for copy number variations
            if gene.copy_number_relevant:
                pgx_result.copy_number = self._detect_copy_number(molecular_result, gene)

            # Calculate activity score
            pgx_result.calculate_activity_score()

            # Assign phenotype
            if auto_phenotype and gene.uses_activity_score:
                pgx_result.determine_phenotype()

            pgx_result.status = 'CALLED'
            pgx_result.called_at = timezone.now()
            pgx_result.save()

            logger.info(
                f"Called diplotype for {gene.symbol}: {pgx_result.diplotype} "
                f"(AS={pgx_result.activity_score}, {pgx_result.phenotype})"
            )

            return pgx_result

        except Exception as e:
            pgx_result.status = 'FAILED'
            pgx_result.notes = f"Diplotype calling failed: {e}"
            pgx_result.save()
            logger.error(f"Diplotype calling failed for {gene.symbol}: {e}")
            raise DiplotypeServiceError(f"Failed to call diplotype: {e}")

    def _get_gene_variants(self, molecular_result, gene: PGxGene) -> list:
        """Extract variants for a specific gene from molecular result."""
        variants = []

        # Get variant calls for this gene
        variant_calls = molecular_result.variant_calls.filter(
            gene__symbol=gene.symbol
        ).select_related('gene')

        for vc in variant_calls:
            variant_data = {
                'id': vc.id,
                'chromosome': vc.chromosome,
                'position': vc.position,
                'ref': vc.ref_allele,
                'alt': vc.alt_allele,
                'hgvs_c': vc.hgvs_c,
                'hgvs_p': vc.hgvs_p,
                'dbsnp_id': vc.dbsnp_id,
                'zygosity': vc.zygosity,
                'allele_frequency': float(vc.allele_frequency) if vc.allele_frequency else None,
            }
            variants.append(variant_data)

        return variants

    def _call_alleles(
        self,
        gene: PGxGene,
        variants: list
    ) -> Tuple[Optional[StarAllele], Optional[StarAllele], Decimal]:
        """
        Call star alleles based on detected variants.

        Uses a matching algorithm to find alleles whose defining
        variants are present in the sample.

        Returns:
            Tuple of (allele1, allele2, confidence_score)
        """
        # Load alleles for this gene
        alleles = list(gene.alleles.filter(is_active=True).order_by('name'))

        if not alleles:
            logger.warning(f"No alleles defined for {gene.symbol}")
            return None, None, Decimal('0')

        # Get reference allele (*1)
        ref_allele = next((a for a in alleles if a.is_reference), None)
        if not ref_allele:
            ref_allele = next((a for a in alleles if a.name == '*1'), alleles[0])

        # Build variant lookup
        variant_rsids = {v.get('dbsnp_id', '').lower() for v in variants if v.get('dbsnp_id')}
        variant_hgvs = {v.get('hgvs_c', '').lower() for v in variants if v.get('hgvs_c')}

        # Score each allele
        allele_scores = []
        for allele in alleles:
            if allele.is_reference:
                continue

            score = self._score_allele_match(allele, variant_rsids, variant_hgvs)
            if score > 0:
                allele_scores.append((allele, score))

        # Sort by score
        allele_scores.sort(key=lambda x: x[1], reverse=True)

        # Determine diplotype based on zygosity
        het_variants = [v for v in variants if v.get('zygosity') == 'HETEROZYGOUS']
        hom_variants = [v for v in variants if v.get('zygosity') == 'HOMOZYGOUS']

        if allele_scores:
            top_allele, top_score = allele_scores[0]

            # Check if homozygous for this allele
            is_homozygous = self._check_homozygosity(top_allele, variants)

            if is_homozygous:
                return top_allele, top_allele, Decimal(str(min(top_score * 100, 100)))

            # Check for compound heterozygous
            if len(allele_scores) >= 2:
                second_allele, second_score = allele_scores[1]
                combined_score = (top_score + second_score) / 2
                return top_allele, second_allele, Decimal(str(min(combined_score * 100, 100)))

            # Single variant allele + reference
            return top_allele, ref_allele, Decimal(str(min(top_score * 100, 100)))

        # No variants found - likely reference
        return ref_allele, ref_allele, Decimal('95.0')

    def _score_allele_match(
        self,
        allele: StarAllele,
        variant_rsids: set,
        variant_hgvs: set
    ) -> float:
        """
        Score how well detected variants match an allele's defining variants.

        Returns score from 0 to 1.
        """
        defining_variants = allele.defining_variants
        if not defining_variants:
            return 0

        matches = 0
        total = len(defining_variants)

        for dv in defining_variants:
            rsid = dv.get('rsid', '').lower()
            hgvs = dv.get('hgvs', '').lower()

            if rsid and rsid in variant_rsids:
                matches += 1
            elif hgvs and hgvs in variant_hgvs:
                matches += 1

        return matches / total if total > 0 else 0

    def _check_homozygosity(self, allele: StarAllele, variants: list) -> bool:
        """Check if all defining variants are homozygous."""
        defining_variants = allele.defining_variants
        if not defining_variants:
            return False

        for dv in defining_variants:
            rsid = dv.get('rsid', '').lower()
            hgvs = dv.get('hgvs', '').lower()

            for v in variants:
                v_rsid = v.get('dbsnp_id', '').lower()
                v_hgvs = v.get('hgvs_c', '').lower()

                if (rsid and rsid == v_rsid) or (hgvs and hgvs == v_hgvs):
                    if v.get('zygosity') != 'HOMOZYGOUS':
                        return False
                    break

        return True

    def _detect_copy_number(self, molecular_result, gene: PGxGene) -> int:
        """
        Detect gene copy number from coverage or CNV data.

        For now, assumes diploid unless CNV data is available.
        """
        # This would integrate with CNV calling pipeline
        # For now, return default diploid
        return 2

    def call_panel(
        self,
        molecular_result,
        panel: PGxPanel,
        auto_phenotype: bool = True
    ) -> List[PGxResult]:
        """
        Call diplotypes for all genes in a panel.

        Args:
            molecular_result: MolecularResult instance
            panel: PGxPanel to call
            auto_phenotype: Automatically assign phenotypes

        Returns:
            List of PGxResult instances
        """
        results = []

        for gene in panel.genes.filter(is_active=True):
            try:
                result = self.call_diplotype(
                    molecular_result,
                    gene,
                    panel=panel,
                    auto_phenotype=auto_phenotype
                )
                results.append(result)
            except DiplotypeServiceError as e:
                logger.error(f"Failed to call {gene.symbol}: {e}")

        return results

    def recalculate_phenotype(self, pgx_result: PGxResult) -> Optional[Phenotype]:
        """
        Recalculate phenotype for an existing result.

        Args:
            pgx_result: PGxResult to update

        Returns:
            Assigned Phenotype or None
        """
        pgx_result.calculate_activity_score()
        phenotype = pgx_result.determine_phenotype()
        pgx_result.save()
        return phenotype

    def get_activity_score_interpretation(
        self,
        gene: PGxGene,
        activity_score: Decimal
    ) -> dict:
        """
        Get interpretation of activity score for a gene.

        Args:
            gene: PGxGene
            activity_score: Activity score to interpret

        Returns:
            Dictionary with phenotype and clinical implications
        """
        phenotype = Phenotype.objects.filter(
            gene=gene,
            activity_score_min__lte=activity_score,
            activity_score_max__gte=activity_score
        ).first()

        if phenotype:
            return {
                'phenotype_code': phenotype.code,
                'phenotype_name': phenotype.name,
                'activity_score': float(activity_score),
                'clinical_implications': phenotype.clinical_implications,
            }

        return {
            'phenotype_code': 'INDETERMINATE',
            'phenotype_name': 'Indeterminate',
            'activity_score': float(activity_score),
            'clinical_implications': 'Activity score does not map to a defined phenotype.',
        }

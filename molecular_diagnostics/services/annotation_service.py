# molecular_diagnostics/services/annotation_service.py
"""
Annotation orchestration service that coordinates ClinVar and gnomAD lookups.

Provides a unified interface for variant annotation with caching,
error handling, and batch processing capabilities.
"""

import logging
from typing import Optional, List
from django.db import transaction
from django.utils import timezone

from molecular_diagnostics.models import VariantCall, VariantAnnotation, AnnotationCache
from .clinvar_service import ClinVarService, ClinVarServiceError
from .gnomad_service import GnomADService, GnomADServiceError

logger = logging.getLogger(__name__)


class AnnotationServiceError(Exception):
    """Exception raised for annotation service errors."""
    pass


class AnnotationService:
    """
    Orchestration service for variant annotations.

    Coordinates lookups to ClinVar and gnomAD, manages caching,
    and updates VariantAnnotation records.
    """

    def __init__(self):
        self.clinvar = ClinVarService()
        self.gnomad = GnomADService()

    def annotate_variant(
        self,
        variant_call: VariantCall,
        force_refresh: bool = False,
        sources: List[str] = None
    ) -> VariantAnnotation:
        """
        Annotate a single variant call.

        Args:
            variant_call: VariantCall instance to annotate
            force_refresh: Skip cache and fetch fresh data
            sources: List of sources to query ('clinvar', 'gnomad'), defaults to both

        Returns:
            VariantAnnotation instance
        """
        sources = sources or ['clinvar', 'gnomad']

        # Get or create annotation record
        annotation, created = VariantAnnotation.objects.get_or_create(
            variant_call=variant_call,
            defaults={'annotation_status': 'PENDING'}
        )

        if not created and annotation.is_complete and not force_refresh:
            logger.info(f"Annotation already complete for {variant_call}")
            return annotation

        # Update status
        annotation.annotation_status = 'IN_PROGRESS'
        annotation.error_message = ''
        annotation.save(update_fields=['annotation_status', 'error_message'])

        # Try to get from cache first
        cache_entry = self._get_or_create_cache(variant_call)
        annotation.cache_entry = cache_entry

        errors = []

        # Fetch ClinVar data
        if 'clinvar' in sources:
            try:
                clinvar_data = self._fetch_clinvar(
                    variant_call, cache_entry, force_refresh
                )
                if clinvar_data:
                    annotation.update_from_clinvar(clinvar_data)
            except ClinVarServiceError as e:
                logger.error(f"ClinVar error for {variant_call}: {e}")
                errors.append(f"ClinVar: {e}")

        # Fetch gnomAD data
        if 'gnomad' in sources:
            try:
                gnomad_data = self._fetch_gnomad(
                    variant_call, cache_entry, force_refresh
                )
                if gnomad_data:
                    annotation.update_from_gnomad(gnomad_data)
            except GnomADServiceError as e:
                logger.error(f"gnomAD error for {variant_call}: {e}")
                errors.append(f"gnomAD: {e}")

        # Determine final status
        if errors:
            if annotation.clinvar_fetched_at or annotation.gnomad_fetched_at:
                annotation.annotation_status = 'PARTIAL'
            else:
                annotation.annotation_status = 'FAILED'
            annotation.error_message = '; '.join(errors)
        elif not annotation.clinvar_fetched_at and not annotation.gnomad_fetched_at:
            annotation.annotation_status = 'NOT_FOUND'
        else:
            annotation.annotation_status = 'COMPLETED'

        annotation.save()

        # Update cache entry hit counter
        if cache_entry:
            cache_entry.record_hit()

        return annotation

    def _get_or_create_cache(self, variant_call: VariantCall) -> Optional[AnnotationCache]:
        """Get or create a cache entry for the variant."""
        try:
            cache_entry, created = AnnotationCache.get_or_create_for_variant(
                chromosome=variant_call.chromosome,
                position=variant_call.position,
                ref=variant_call.ref_allele,
                alt=variant_call.alt_allele
            )

            # Update alternate keys if available
            if variant_call.hgvs_c and not cache_entry.hgvs_notation:
                cache_entry.hgvs_notation = variant_call.hgvs_c
            if variant_call.dbsnp_id and not cache_entry.dbsnp_id:
                cache_entry.dbsnp_id = variant_call.dbsnp_id
            cache_entry.save()

            return cache_entry
        except Exception as e:
            logger.warning(f"Failed to create cache entry: {e}")
            return None

    def _fetch_clinvar(
        self,
        variant_call: VariantCall,
        cache_entry: Optional[AnnotationCache],
        force_refresh: bool
    ) -> Optional[dict]:
        """Fetch ClinVar data, using cache if available."""
        # Check cache
        if not force_refresh and cache_entry and not cache_entry.clinvar_expired:
            if cache_entry.clinvar_data:
                logger.debug(f"Using cached ClinVar data for {variant_call}")
                return cache_entry.clinvar_data

        # Fetch from API
        data = self.clinvar.annotate_variant(
            chromosome=variant_call.chromosome,
            position=variant_call.position,
            ref=variant_call.ref_allele,
            alt=variant_call.alt_allele,
            rsid=variant_call.dbsnp_id,
            hgvs=variant_call.hgvs_c
        )

        # Update cache
        if cache_entry and data:
            cache_entry.clinvar_data = data
            cache_entry.clinvar_fetched_at = timezone.now()
            cache_entry.save(update_fields=['clinvar_data', 'clinvar_fetched_at'])

        return data

    def _fetch_gnomad(
        self,
        variant_call: VariantCall,
        cache_entry: Optional[AnnotationCache],
        force_refresh: bool
    ) -> Optional[dict]:
        """Fetch gnomAD data, using cache if available."""
        # Check cache
        if not force_refresh and cache_entry and not cache_entry.gnomad_expired:
            if cache_entry.gnomad_data:
                logger.debug(f"Using cached gnomAD data for {variant_call}")
                return cache_entry.gnomad_data

        # Fetch from API
        gene_symbol = variant_call.gene.symbol if variant_call.gene else None
        data = self.gnomad.annotate_variant(
            chromosome=variant_call.chromosome,
            position=variant_call.position,
            ref=variant_call.ref_allele,
            alt=variant_call.alt_allele,
            gene_symbol=gene_symbol
        )

        # Update cache
        if cache_entry and data:
            cache_entry.gnomad_data = data
            cache_entry.gnomad_fetched_at = timezone.now()
            cache_entry.save(update_fields=['gnomad_data', 'gnomad_fetched_at'])

        return data

    def annotate_result(
        self,
        molecular_result,
        force_refresh: bool = False
    ) -> List[VariantAnnotation]:
        """
        Annotate all variants in a molecular result.

        Args:
            molecular_result: MolecularResult instance
            force_refresh: Skip cache and fetch fresh data

        Returns:
            List of VariantAnnotation instances
        """
        annotations = []
        variant_calls = molecular_result.variant_calls.select_related('gene').all()

        for variant_call in variant_calls:
            try:
                annotation = self.annotate_variant(variant_call, force_refresh)
                annotations.append(annotation)
            except Exception as e:
                logger.error(f"Failed to annotate {variant_call}: {e}")

        return annotations

    def bulk_annotate(
        self,
        variant_calls: List[VariantCall],
        force_refresh: bool = False,
        progress_callback=None
    ) -> dict:
        """
        Bulk annotate multiple variant calls.

        Args:
            variant_calls: List of VariantCall instances
            force_refresh: Skip cache and fetch fresh data
            progress_callback: Optional callback(current, total, variant_call)

        Returns:
            Dictionary with stats: success_count, failed_count, annotations
        """
        stats = {
            'total': len(variant_calls),
            'success_count': 0,
            'failed_count': 0,
            'partial_count': 0,
            'not_found_count': 0,
            'annotations': []
        }

        for i, variant_call in enumerate(variant_calls):
            try:
                annotation = self.annotate_variant(variant_call, force_refresh)
                stats['annotations'].append(annotation)

                if annotation.annotation_status == 'COMPLETED':
                    stats['success_count'] += 1
                elif annotation.annotation_status == 'PARTIAL':
                    stats['partial_count'] += 1
                elif annotation.annotation_status == 'NOT_FOUND':
                    stats['not_found_count'] += 1
                else:
                    stats['failed_count'] += 1

            except Exception as e:
                logger.error(f"Bulk annotation error for {variant_call}: {e}")
                stats['failed_count'] += 1

            if progress_callback:
                progress_callback(i + 1, stats['total'], variant_call)

        return stats

    def get_annotation_summary(self, variant_call: VariantCall) -> dict:
        """
        Get a summary of annotation data for a variant.

        Args:
            variant_call: VariantCall instance

        Returns:
            Dictionary with summarized annotation data
        """
        try:
            annotation = variant_call.annotation
        except VariantAnnotation.DoesNotExist:
            return {'status': 'NOT_ANNOTATED'}

        summary = {
            'status': annotation.annotation_status,
            'clinical_significance': annotation.clinical_significance,
            'review_status': annotation.review_status,
            'review_stars': annotation.review_status_stars,
            'conditions': [c.get('name', '') for c in annotation.conditions[:3]],
            'condition_count': len(annotation.conditions),
            'genome_af': float(annotation.genome_af) if annotation.genome_af else None,
            'exome_af': float(annotation.exome_af) if annotation.exome_af else None,
            'max_population_af': float(annotation.max_population_af) if annotation.max_population_af else None,
            'max_population': annotation.max_population,
            'is_rare': annotation.is_rare,
            'flags': annotation.flags,
            'submission_count': annotation.submission_count,
            'pubmed_count': len(annotation.pubmed_ids),
        }

        # Add gene constraint if available
        if annotation.gene_constraint:
            summary['gene_constraint'] = {
                'pLI': annotation.gene_constraint.get('pLI'),
                'loeuf': annotation.gene_constraint.get('loeuf'),
            }

        return summary

    def refresh_stale_annotations(self, days_old: int = 30) -> dict:
        """
        Refresh annotations older than specified days.

        Args:
            days_old: Refresh annotations older than this many days

        Returns:
            Dictionary with refresh stats
        """
        cutoff = timezone.now() - timezone.timedelta(days=days_old)

        stale_annotations = VariantAnnotation.objects.filter(
            annotation_status='COMPLETED',
            updated_at__lt=cutoff
        ).select_related('variant_call', 'variant_call__gene')

        variant_calls = [a.variant_call for a in stale_annotations]

        logger.info(f"Refreshing {len(variant_calls)} stale annotations")

        return self.bulk_annotate(variant_calls, force_refresh=True)

    def cleanup_cache(self, days_old: int = 90, min_hits: int = 0) -> int:
        """
        Clean up old cache entries.

        Args:
            days_old: Delete entries older than this
            min_hits: Only delete entries with fewer hits

        Returns:
            Number of deleted entries
        """
        cutoff = timezone.now() - timezone.timedelta(days=days_old)

        deleted, _ = AnnotationCache.objects.filter(
            updated_at__lt=cutoff,
            hit_count__lte=min_hits
        ).delete()

        logger.info(f"Cleaned up {deleted} stale cache entries")
        return deleted

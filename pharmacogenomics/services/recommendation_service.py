# pharmacogenomics/services/recommendation_service.py
"""
Drug recommendation service based on PGx results.

Generates personalized drug dosing recommendations based on
patient genotype/phenotype using CPIC guidelines.
"""

import logging
from typing import Optional, List
from django.db import transaction

from pharmacogenomics.models import (
    PGxResult, PGxDrugResult, Drug, DrugGeneInteraction, DrugRecommendation
)

logger = logging.getLogger(__name__)


class RecommendationServiceError(Exception):
    """Exception raised for recommendation service errors."""
    pass


class RecommendationService:
    """
    Service for generating drug recommendations from PGx results.

    Provides:
    - Drug-specific recommendations based on phenotype
    - Multi-gene interaction handling
    - Clinical summaries
    """

    def generate_recommendations(
        self,
        pgx_result: PGxResult,
        drugs: List[Drug] = None
    ) -> List[PGxDrugResult]:
        """
        Generate drug recommendations for a PGx result.

        Args:
            pgx_result: PGxResult instance with phenotype assigned
            drugs: Optional list of drugs to check. If None, checks all drugs
                   with interactions for this gene.

        Returns:
            List of PGxDrugResult instances
        """
        if not pgx_result.phenotype:
            logger.warning(f"No phenotype assigned for {pgx_result}")
            return []

        # Get drug-gene interactions for this gene
        interactions = DrugGeneInteraction.objects.filter(
            gene=pgx_result.gene,
            is_active=True
        ).select_related('drug')

        if drugs:
            drug_ids = [d.id for d in drugs]
            interactions = interactions.filter(drug_id__in=drug_ids)

        results = []

        for interaction in interactions:
            try:
                drug_result = self._generate_drug_recommendation(
                    pgx_result, interaction
                )
                if drug_result:
                    results.append(drug_result)
            except Exception as e:
                logger.error(
                    f"Failed to generate recommendation for "
                    f"{interaction.drug.name}: {e}"
                )

        return results

    def _generate_drug_recommendation(
        self,
        pgx_result: PGxResult,
        interaction: DrugGeneInteraction
    ) -> Optional[PGxDrugResult]:
        """Generate recommendation for a specific drug-gene interaction."""
        # Find matching recommendation for this phenotype
        recommendation = DrugRecommendation.objects.filter(
            interaction=interaction,
            phenotype=pgx_result.phenotype,
            is_active=True
        ).first()

        # Get or create drug result
        drug_result, created = PGxDrugResult.objects.update_or_create(
            pgx_result=pgx_result,
            drug=interaction.drug,
            defaults={
                'recommendation': recommendation,
                'action': recommendation.action if recommendation else '',
                'is_actionable': self._is_actionable(recommendation),
            }
        )

        # Generate personalized recommendation text
        drug_result.recommendation_text = self._personalize_recommendation(
            pgx_result, interaction, recommendation
        )
        drug_result.save()

        return drug_result

    def _is_actionable(self, recommendation: Optional[DrugRecommendation]) -> bool:
        """Determine if a recommendation requires clinical action."""
        if not recommendation:
            return False

        actionable_actions = ['REDUCE', 'INCREASE', 'AVOID', 'ALTERNATIVE', 'CAUTION']
        return recommendation.action in actionable_actions

    def _personalize_recommendation(
        self,
        pgx_result: PGxResult,
        interaction: DrugGeneInteraction,
        recommendation: Optional[DrugRecommendation]
    ) -> str:
        """Generate personalized recommendation text."""
        gene = pgx_result.gene.symbol
        diplotype = pgx_result.diplotype_display
        phenotype = pgx_result.phenotype.name if pgx_result.phenotype else "Unknown"
        drug = interaction.drug.name

        if recommendation:
            text = (
                f"Based on {gene} {diplotype} ({phenotype}), "
                f"{recommendation.recommendation_text}"
            )

            if recommendation.dosing_guidance:
                text += f"\n\nDosing guidance: {recommendation.dosing_guidance}"

            if recommendation.alternative_drugs:
                alternatives = ", ".join(recommendation.alternative_drugs)
                text += f"\n\nAlternative options: {alternatives}"

            return text

        # Default text when no specific recommendation exists
        return (
            f"Patient has {gene} {diplotype} ({phenotype}). "
            f"No specific dosing recommendation available for {drug} "
            f"with this phenotype. Consider standard dosing with monitoring."
        )

    def get_summary_for_result(self, molecular_result) -> dict:
        """
        Get a summary of all PGx recommendations for a molecular result.

        Args:
            molecular_result: MolecularResult instance

        Returns:
            Dictionary with summary information
        """
        pgx_results = PGxResult.objects.filter(
            molecular_result=molecular_result,
            status='CALLED'
        ).select_related('gene', 'phenotype', 'allele1', 'allele2')

        summary = {
            'genes_tested': [],
            'actionable_drugs': [],
            'normal_metabolism': [],
            'altered_metabolism': [],
            'recommendations': [],
        }

        for pgx_result in pgx_results:
            gene_info = {
                'gene': pgx_result.gene.symbol,
                'diplotype': pgx_result.diplotype_display,
                'phenotype': pgx_result.phenotype.name if pgx_result.phenotype else 'Unknown',
                'activity_score': float(pgx_result.activity_score) if pgx_result.activity_score else None,
            }
            summary['genes_tested'].append(gene_info)

            # Categorize by phenotype
            if pgx_result.phenotype:
                if pgx_result.phenotype.code == 'NM':
                    summary['normal_metabolism'].append(gene_info)
                else:
                    summary['altered_metabolism'].append(gene_info)

            # Get drug results
            drug_results = pgx_result.drug_results.select_related(
                'drug', 'recommendation'
            )

            for dr in drug_results:
                rec_info = {
                    'gene': pgx_result.gene.symbol,
                    'drug': dr.drug.name,
                    'action': dr.action,
                    'recommendation': dr.recommendation_text,
                    'is_actionable': dr.is_actionable,
                }
                summary['recommendations'].append(rec_info)

                if dr.is_actionable:
                    summary['actionable_drugs'].append(dr.drug.name)

        return summary

    def generate_clinical_summary(self, molecular_result) -> str:
        """
        Generate a clinical summary narrative for PGx results.

        Args:
            molecular_result: MolecularResult instance

        Returns:
            Clinical summary text
        """
        summary_data = self.get_summary_for_result(molecular_result)

        if not summary_data['genes_tested']:
            return "No pharmacogenomic results available."

        sections = []

        # Overview
        gene_count = len(summary_data['genes_tested'])
        sections.append(
            f"Pharmacogenomic testing was performed for {gene_count} gene(s)."
        )

        # Results summary
        if summary_data['altered_metabolism']:
            altered = summary_data['altered_metabolism']
            altered_text = "; ".join(
                f"{g['gene']} {g['diplotype']} ({g['phenotype']})"
                for g in altered
            )
            sections.append(
                f"Altered metabolism detected: {altered_text}"
            )

        if summary_data['normal_metabolism']:
            normal = summary_data['normal_metabolism']
            normal_genes = ", ".join(g['gene'] for g in normal)
            sections.append(
                f"Normal metabolism: {normal_genes}"
            )

        # Actionable recommendations
        if summary_data['actionable_drugs']:
            drugs = list(set(summary_data['actionable_drugs']))
            sections.append(
                f"\nActionable findings for: {', '.join(drugs)}"
            )

            for rec in summary_data['recommendations']:
                if rec['is_actionable']:
                    sections.append(
                        f"\n{rec['drug']} ({rec['gene']}): {rec['action']}"
                    )

        return "\n".join(sections)

    def get_drug_recommendations_for_patient(
        self,
        patient_id: int,
        drug: Drug = None
    ) -> List[dict]:
        """
        Get all PGx recommendations for a patient.

        Args:
            patient_id: Patient ID
            drug: Optional specific drug to query

        Returns:
            List of recommendation dictionaries
        """
        from lab_management.models import Patient

        # Get all PGx results for this patient
        pgx_results = PGxResult.objects.filter(
            molecular_result__sample__lab_order__patient_id=patient_id,
            status__in=['CALLED', 'REVIEWED', 'REPORTED']
        ).select_related('gene', 'phenotype')

        results = []

        for pgx_result in pgx_results:
            drug_results = pgx_result.drug_results.select_related('drug', 'recommendation')

            if drug:
                drug_results = drug_results.filter(drug=drug)

            for dr in drug_results:
                results.append({
                    'gene': pgx_result.gene.symbol,
                    'diplotype': pgx_result.diplotype_display,
                    'phenotype': pgx_result.phenotype.name if pgx_result.phenotype else 'Unknown',
                    'drug': dr.drug.name,
                    'action': dr.action,
                    'recommendation': dr.recommendation_text,
                    'is_actionable': dr.is_actionable,
                    'result_date': pgx_result.molecular_result.created_at,
                })

        return results

    def check_drug_interactions(
        self,
        patient_id: int,
        drug_list: List[str]
    ) -> List[dict]:
        """
        Check a list of drugs against patient's PGx profile.

        Args:
            patient_id: Patient ID
            drug_list: List of drug names to check

        Returns:
            List of interaction alerts
        """
        # Get drugs
        drugs = Drug.objects.filter(name__in=drug_list)

        if not drugs.exists():
            return []

        alerts = []

        for drug in drugs:
            recommendations = self.get_drug_recommendations_for_patient(
                patient_id, drug
            )

            for rec in recommendations:
                if rec['is_actionable']:
                    alerts.append({
                        'drug': drug.name,
                        'gene': rec['gene'],
                        'phenotype': rec['phenotype'],
                        'action': rec['action'],
                        'alert_level': self._get_alert_level(rec['action']),
                        'recommendation': rec['recommendation'],
                    })

        return alerts

    def _get_alert_level(self, action: str) -> str:
        """Get alert level based on action."""
        if action in ['AVOID', 'ALTERNATIVE']:
            return 'HIGH'
        elif action in ['REDUCE', 'INCREASE', 'CAUTION']:
            return 'MODERATE'
        elif action == 'MONITOR':
            return 'LOW'
        return 'INFO'

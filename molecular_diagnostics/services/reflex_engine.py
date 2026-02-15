"""
Reflex testing engine for automated follow-up test ordering.
"""
from typing import List, Dict, Any, Optional, Tuple
from django.db.models import Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ReflexEngine:
    """
    Engine for evaluating reflex rules and triggering follow-up tests.
    """

    def __init__(self):
        self.triggered_orders = []

    def evaluate_condition(self, condition: Dict, result) -> bool:
        """
        Evaluate a condition against a molecular result.

        Supports:
        - Simple field matching: {"interpretation": "POSITIVE"}
        - Target-specific results: {"target": "GENE1", "result": "DETECTED"}
        - Numeric comparisons: {"ct_value": {"lt": 30}}
        - Logical operators: {"and": [...]}, {"or": [...]}, {"not": {...}}

        Args:
            condition: Condition dictionary
            result: MolecularResult instance

        Returns:
            True if condition is met
        """
        if not condition:
            return False

        # Handle logical operators
        if 'and' in condition:
            return all(self.evaluate_condition(c, result) for c in condition['and'])

        if 'or' in condition:
            return any(self.evaluate_condition(c, result) for c in condition['or'])

        if 'not' in condition:
            return not self.evaluate_condition(condition['not'], result)

        # Handle interpretation check
        if 'interpretation' in condition:
            return result.interpretation == condition['interpretation']

        # Handle status check
        if 'status' in condition:
            return result.status == condition['status']

        # Handle target-specific PCR results
        if 'target' in condition:
            target_symbol = condition['target']
            expected_result = condition.get('result')
            ct_condition = condition.get('ct_value')

            # Find PCR result for this target
            pcr_results = result.pcr_results.filter(
                gene_target__symbol=target_symbol
            )

            if not pcr_results.exists():
                return False

            for pcr_result in pcr_results:
                if expected_result and pcr_result.detection != expected_result:
                    continue

                if ct_condition:
                    if not self._evaluate_numeric_condition(pcr_result.ct_value, ct_condition):
                        continue

                return True

            return False

        # Handle ct_value condition (any target)
        if 'ct_value' in condition:
            ct_condition = condition['ct_value']
            for pcr_result in result.pcr_results.all():
                if pcr_result.ct_value and self._evaluate_numeric_condition(
                    pcr_result.ct_value, ct_condition
                ):
                    return True
            return False

        # Handle variant classification
        if 'variant_classification' in condition:
            classifications = condition['variant_classification']
            if isinstance(classifications, str):
                classifications = [classifications]

            return result.variant_calls.filter(
                classification__in=classifications,
                is_reportable=True
            ).exists()

        # Handle gene with pathogenic variant
        if 'pathogenic_in_gene' in condition:
            gene_symbol = condition['pathogenic_in_gene']
            return result.variant_calls.filter(
                gene_target__symbol=gene_symbol,
                classification__in=['PATHOGENIC', 'LIKELY_PATHOGENIC'],
                is_reportable=True
            ).exists()

        return False

    def _evaluate_numeric_condition(self, value: float, condition: Dict) -> bool:
        """
        Evaluate a numeric condition.

        Supports: lt, lte, gt, gte, eq, ne, between
        """
        if value is None:
            return False

        if 'lt' in condition:
            return float(value) < float(condition['lt'])
        if 'lte' in condition:
            return float(value) <= float(condition['lte'])
        if 'gt' in condition:
            return float(value) > float(condition['gt'])
        if 'gte' in condition:
            return float(value) >= float(condition['gte'])
        if 'eq' in condition:
            return float(value) == float(condition['eq'])
        if 'ne' in condition:
            return float(value) != float(condition['ne'])
        if 'between' in condition:
            low, high = condition['between']
            return float(low) <= float(value) <= float(high)

        return False

    def find_applicable_rules(self, result) -> List:
        """
        Find all active reflex rules that apply to a result's test panel.

        Args:
            result: MolecularResult instance

        Returns:
            List of ReflexRule instances
        """
        from molecular_diagnostics.models.reflex_rules import ReflexRule

        return list(ReflexRule.objects.filter(
            trigger_test=result.test_panel,
            is_active=True
        ).order_by('priority'))

    def evaluate_result(self, result) -> List[Tuple]:
        """
        Evaluate a result against all applicable reflex rules.

        Args:
            result: MolecularResult instance

        Returns:
            List of tuples: (rule, should_trigger, reason)
        """
        evaluations = []
        rules = self.find_applicable_rules(result)

        for rule in rules:
            try:
                should_trigger = rule.evaluate_conditions(result)
                reason = "Conditions met" if should_trigger else "Conditions not met"
                evaluations.append((rule, should_trigger, reason))
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")
                evaluations.append((rule, False, f"Error: {str(e)}"))

        return evaluations

    def check_reflex_limit(self, rule, sample) -> Tuple[bool, str]:
        """
        Check if the reflex limit has been reached for this sample.

        Args:
            rule: ReflexRule instance
            sample: MolecularSample instance

        Returns:
            Tuple of (can_trigger, reason)
        """
        from molecular_diagnostics.models.reflex_rules import ReflexTestOrder

        existing_count = ReflexTestOrder.objects.filter(
            reflex_rule=rule,
            sample=sample,
            status__in=['PENDING', 'CONFIRMED', 'ORDERED', 'COMPLETED']
        ).count()

        if existing_count >= rule.max_reflexes_per_sample:
            return False, f"Maximum reflexes ({rule.max_reflexes_per_sample}) reached for this sample"

        return True, "Within limits"

    def trigger_reflex(self, rule, result, auto_confirm: bool = False) -> Optional[Any]:
        """
        Trigger a reflex test based on a rule and result.

        Args:
            rule: ReflexRule instance
            result: MolecularResult instance (the triggering result)
            auto_confirm: Automatically confirm the reflex order

        Returns:
            ReflexTestOrder instance or None if not triggered
        """
        from molecular_diagnostics.models.reflex_rules import ReflexTestOrder

        sample = result.sample

        # Check reflex limit
        can_trigger, reason = self.check_reflex_limit(rule, sample)
        if not can_trigger:
            logger.info(f"Reflex not triggered for rule {rule.id}: {reason}")
            return None

        # Create reflex order
        reflex_order = ReflexTestOrder.objects.create(
            reflex_rule=rule,
            triggering_result=result,
            sample=sample,
            status='PENDING' if rule.require_confirmation else 'ORDERED',
        )

        logger.info(f"Reflex order {reflex_order.id} created for rule {rule.name}")

        # Auto-confirm if configured
        if auto_confirm or (rule.auto_approve and not rule.require_confirmation):
            # Get a system user or the result's performer
            user = result.performed_by
            if user:
                reflex_order.confirm(user)
                logger.info(f"Reflex order {reflex_order.id} auto-confirmed")

        self.triggered_orders.append(reflex_order)
        return reflex_order

    def process_result(self, result, auto_confirm: bool = False) -> List:
        """
        Process a result for all applicable reflex rules.

        This is the main entry point for reflex testing.

        Args:
            result: MolecularResult instance
            auto_confirm: Automatically confirm triggered reflexes

        Returns:
            List of ReflexTestOrder instances created
        """
        self.triggered_orders = []
        evaluations = self.evaluate_result(result)

        for rule, should_trigger, reason in evaluations:
            if should_trigger:
                logger.info(f"Rule {rule.name} triggered for result {result.id}")
                self.trigger_reflex(rule, result, auto_confirm)
            else:
                logger.debug(f"Rule {rule.name} not triggered: {reason}")

        return self.triggered_orders

    def get_pending_reflexes(self, sample=None) -> List:
        """
        Get pending reflex orders awaiting confirmation.

        Args:
            sample: Optional sample to filter by

        Returns:
            QuerySet of pending ReflexTestOrder instances
        """
        from molecular_diagnostics.models.reflex_rules import ReflexTestOrder

        qs = ReflexTestOrder.objects.filter(status='PENDING')
        if sample:
            qs = qs.filter(sample=sample)
        return qs.select_related('reflex_rule', 'sample', 'triggering_result')

    def bulk_confirm(self, reflex_orders, user) -> List:
        """
        Confirm multiple reflex orders at once.

        Args:
            reflex_orders: Iterable of ReflexTestOrder instances
            user: User confirming the orders

        Returns:
            List of created MolecularResult instances
        """
        results = []
        for order in reflex_orders:
            if order.status == 'PENDING':
                result = order.confirm(user)
                results.append(result)
        return results


# Integration hook for workflow engine
def check_reflex_on_result_completion(result, auto_process: bool = True):
    """
    Hook to be called when a result is completed.
    Checks for applicable reflex rules and triggers them.

    Args:
        result: MolecularResult instance
        auto_process: Whether to automatically process reflex rules

    Returns:
        List of triggered ReflexTestOrder instances
    """
    if not auto_process:
        return []

    # Only process final results
    if result.status not in ['FINAL', 'PRELIMINARY']:
        return []

    engine = ReflexEngine()
    return engine.process_result(result)

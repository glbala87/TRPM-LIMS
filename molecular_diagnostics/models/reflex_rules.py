"""
Reflex testing rules for automated follow-up testing.

Reflex testing allows automatic triggering of additional tests based on
the results of an initial test.
"""
from django.db import models
from django.conf import settings


class ReflexRule(models.Model):
    """
    Defines a rule for automatic reflex testing.

    When a trigger_test produces results matching the conditions,
    the reflex_test is automatically ordered.
    """

    name = models.CharField(
        max_length=200,
        help_text="Descriptive name for the reflex rule"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of when and why this rule applies"
    )

    # Trigger configuration
    trigger_test = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.CASCADE,
        related_name='trigger_rules',
        help_text="The test that triggers this reflex rule"
    )

    # What test to order when triggered
    reflex_test = models.ForeignKey(
        'molecular_diagnostics.MolecularTestPanel',
        on_delete=models.CASCADE,
        related_name='reflex_from_rules',
        help_text="The test to automatically order when triggered"
    )

    # Condition configuration (JSON format)
    conditions = models.JSONField(
        default=dict,
        help_text="""
        JSON object defining trigger conditions. Examples:
        {"interpretation": "POSITIVE"}
        {"target": "GENE1", "result": "DETECTED"}
        {"ct_value": {"lt": 30}}
        {"and": [{"interpretation": "POSITIVE"}, {"ct_value": {"lt": 35}}]}
        """
    )

    # Rule priority (lower number = higher priority)
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Rules with lower numbers are evaluated first"
    )

    # Behavior settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is currently active"
    )
    auto_approve = models.BooleanField(
        default=False,
        help_text="Automatically approve the reflex test without review"
    )
    require_confirmation = models.BooleanField(
        default=True,
        help_text="Require user confirmation before ordering reflex test"
    )
    notify_ordering_physician = models.BooleanField(
        default=True,
        help_text="Send notification to ordering physician when reflex triggers"
    )

    # Limits
    max_reflexes_per_sample = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of times this rule can trigger per sample"
    )

    # Clinical context
    clinical_rationale = models.TextField(
        blank=True,
        help_text="Clinical justification for this reflex rule"
    )

    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reflex_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reflex Rule"
        verbose_name_plural = "Reflex Rules"
        ordering = ['priority', 'name']
        unique_together = ['trigger_test', 'reflex_test', 'conditions']

    def __str__(self):
        return f"{self.name}: {self.trigger_test} -> {self.reflex_test}"

    def evaluate_conditions(self, result) -> bool:
        """
        Evaluate if the conditions are met for a given result.

        Args:
            result: MolecularResult instance to evaluate

        Returns:
            True if conditions are met, False otherwise
        """
        from molecular_diagnostics.services.reflex_engine import ReflexEngine
        engine = ReflexEngine()
        return engine.evaluate_condition(self.conditions, result)


class ReflexTestOrder(models.Model):
    """
    Tracks reflex tests that have been triggered.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('ORDERED', 'Ordered'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    # Link to the rule that triggered this
    reflex_rule = models.ForeignKey(
        ReflexRule,
        on_delete=models.PROTECT,
        related_name='triggered_orders'
    )

    # Original result that triggered the reflex
    triggering_result = models.ForeignKey(
        'molecular_diagnostics.MolecularResult',
        on_delete=models.CASCADE,
        related_name='triggered_reflex_orders'
    )

    # The sample to be tested
    sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.CASCADE,
        related_name='reflex_orders'
    )

    # The new result created (if ordered)
    reflex_result = models.ForeignKey(
        'molecular_diagnostics.MolecularResult',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordered_as_reflex'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # Audit information
    triggered_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_reflex_orders'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_reflex_orders'
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Reflex Test Order"
        verbose_name_plural = "Reflex Test Orders"
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Reflex: {self.reflex_rule.reflex_test} for {self.sample}"

    def confirm(self, user):
        """Confirm and order the reflex test."""
        from django.utils import timezone
        from molecular_diagnostics.models import MolecularResult

        self.status = 'CONFIRMED'
        self.confirmed_by = user
        self.confirmed_at = timezone.now()
        self.save()

        # Create the reflex result
        self.reflex_result = MolecularResult.objects.create(
            sample=self.sample,
            test_panel=self.reflex_rule.reflex_test,
            status='PENDING',
        )
        self.status = 'ORDERED'
        self.save()

        return self.reflex_result

    def cancel(self, user, reason=''):
        """Cancel the reflex test order."""
        from django.utils import timezone

        self.status = 'CANCELLED'
        self.cancelled_by = user
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()

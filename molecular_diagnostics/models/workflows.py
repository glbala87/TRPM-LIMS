# molecular_diagnostics/models/workflows.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class WorkflowDefinition(models.Model):
    """Defines a workflow for molecular testing processes"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workflow Definition"
        verbose_name_plural = "Workflow Definitions"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def ordered_steps(self):
        return self.steps.order_by('order')

    def get_first_step(self):
        return self.steps.order_by('order').first()


class WorkflowStep(models.Model):
    """Individual step within a workflow"""

    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    allowed_transitions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='allowed_from',
        blank=True,
        help_text="Steps that can be transitioned to from this step"
    )

    # Status mapping - maps to MolecularSample.WORKFLOW_STATUS_CHOICES
    status_on_entry = models.CharField(
        max_length=20,
        choices=[
            ('RECEIVED', 'Received'),
            ('EXTRACTED', 'Extracted'),
            ('AMPLIFIED', 'Amplified'),
            ('SEQUENCED', 'Sequenced'),
            ('ANALYZED', 'Analyzed'),
            ('REPORTED', 'Reported'),
        ],
        help_text="Sample status when entering this step"
    )

    # QC requirements
    requires_qc = models.BooleanField(
        default=False,
        help_text="Does this step require QC check before proceeding?"
    )
    qc_metrics = models.ManyToManyField(
        'molecular_diagnostics.QCMetricDefinition',
        related_name='required_by_steps',
        blank=True
    )

    # Estimated duration
    estimated_duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated time to complete this step"
    )

    # Equipment requirements
    required_instruments = models.ManyToManyField(
        'equipment.Instrument',
        related_name='required_for_steps',
        blank=True
    )

    is_terminal = models.BooleanField(
        default=False,
        help_text="Is this a terminal step (no further transitions)?"
    )

    class Meta:
        verbose_name = "Workflow Step"
        verbose_name_plural = "Workflow Steps"
        ordering = ['workflow', 'order']
        unique_together = [['workflow', 'code'], ['workflow', 'order']]

    def __str__(self):
        return f"{self.workflow.name} - {self.order}. {self.name}"

    def get_next_steps(self):
        """Get allowed next steps"""
        return self.allowed_transitions.all()

    def can_transition_to(self, target_step):
        """Check if transition to target step is allowed"""
        return self.allowed_transitions.filter(pk=target_step.pk).exists()


class SampleHistory(models.Model):
    """Audit trail for sample status changes"""

    sample = models.ForeignKey(
        'molecular_diagnostics.MolecularSample',
        on_delete=models.CASCADE,
        related_name='history'
    )
    from_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Previous status (blank if initial)"
    )
    to_status = models.CharField(max_length=20)
    from_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_from'
    )
    to_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_to'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)

    # Associated entities
    instrument_run = models.ForeignKey(
        'molecular_diagnostics.InstrumentRun',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sample_history'
    )
    qc_passed = models.BooleanField(null=True, blank=True)
    qc_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Sample History"
        verbose_name_plural = "Sample Histories"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sample.sample_id}: {self.from_status} → {self.to_status} at {self.timestamp}"

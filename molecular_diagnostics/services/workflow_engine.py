# molecular_diagnostics/services/workflow_engine.py

from django.utils import timezone
from django.db import transaction


class WorkflowEngine:
    """
    State machine for managing molecular sample workflow transitions.

    Handles transitions between workflow statuses and maintains full audit trail.
    """

    # Define valid state transitions
    VALID_TRANSITIONS = {
        'RECEIVED': ['EXTRACTED', 'CANCELLED', 'FAILED'],
        'EXTRACTED': ['AMPLIFIED', 'SEQUENCED', 'CANCELLED', 'FAILED'],
        'AMPLIFIED': ['SEQUENCED', 'ANALYZED', 'CANCELLED', 'FAILED'],
        'SEQUENCED': ['ANALYZED', 'CANCELLED', 'FAILED'],
        'ANALYZED': ['REPORTED', 'CANCELLED', 'FAILED'],
        'REPORTED': ['AMENDED'],
        'CANCELLED': [],
        'FAILED': ['RECEIVED'],  # Allow restart from FAILED
    }

    # Statuses that require QC validation before proceeding
    QC_REQUIRED_TRANSITIONS = {
        'EXTRACTED': ['concentration', 'purity'],
        'AMPLIFIED': ['amplification_qc'],
        'SEQUENCED': ['sequencing_qc'],
    }

    def get_available_transitions(self, sample):
        """
        Get list of valid next statuses for a sample.

        Args:
            sample: MolecularSample instance

        Returns:
            List of (status_code, status_display) tuples
        """
        from ..models import MolecularSample

        current_status = sample.workflow_status
        valid_next = self.VALID_TRANSITIONS.get(current_status, [])

        # Convert to display format
        status_choices = dict(MolecularSample.WORKFLOW_STATUS_CHOICES)
        return [(status, status_choices.get(status, status)) for status in valid_next]

    def can_transition(self, sample, new_status):
        """
        Check if a sample can transition to a new status.

        Args:
            sample: MolecularSample instance
            new_status: Target status code

        Returns:
            Tuple of (can_transition: bool, reason: str)
        """
        current_status = sample.workflow_status
        valid_next = self.VALID_TRANSITIONS.get(current_status, [])

        if new_status not in valid_next:
            return False, f"Cannot transition from {current_status} to {new_status}"

        # Check QC requirements if applicable
        if current_status in self.QC_REQUIRED_TRANSITIONS:
            qc_passed, qc_reason = self._check_qc_requirements(sample, current_status)
            if not qc_passed:
                return False, qc_reason

        return True, "Transition allowed"

    def _check_qc_requirements(self, sample, current_status):
        """Check if QC requirements are met for transition from current status."""
        required_qc = self.QC_REQUIRED_TRANSITIONS.get(current_status, [])

        if 'concentration' in required_qc:
            if sample.concentration_ng_ul is None:
                return False, "Concentration measurement required before proceeding"

        if 'purity' in required_qc:
            if sample.a260_280_ratio is None:
                return False, "A260/280 purity ratio required before proceeding"
            # Check acceptable purity range (typically 1.7-2.0 for DNA)
            if sample.a260_280_ratio < 1.7 or sample.a260_280_ratio > 2.1:
                return False, f"Purity ratio {sample.a260_280_ratio} outside acceptable range (1.7-2.1)"

        return True, "QC passed"

    @transaction.atomic
    def transition(self, sample, new_status, user=None, notes='',
                   instrument_run=None, qc_passed=None, qc_notes='',
                   force=False):
        """
        Transition a sample to a new status.

        Args:
            sample: MolecularSample instance
            new_status: Target status code
            user: User performing the transition
            notes: Optional notes about the transition
            instrument_run: Associated InstrumentRun if applicable
            qc_passed: QC result (True/False/None)
            qc_notes: QC-related notes
            force: Force transition even if QC not met (for admin override)

        Returns:
            SampleHistory instance

        Raises:
            ValueError: If transition is not valid
        """
        from ..models import SampleHistory

        old_status = sample.workflow_status
        old_step = sample.current_step

        # Validate transition
        if not force:
            can_transition, reason = self.can_transition(sample, new_status)
            if not can_transition:
                raise ValueError(reason)

        # Update sample status
        sample.workflow_status = new_status

        # Update current step if workflow is defined
        if sample.test_panel and sample.test_panel.workflow:
            new_step = sample.test_panel.workflow.steps.filter(
                status_on_entry=new_status
            ).first()
            if new_step:
                sample.current_step = new_step

        sample.save()

        # Create history record
        history = SampleHistory.objects.create(
            sample=sample,
            from_status=old_status,
            to_status=new_status,
            from_step=old_step,
            to_step=sample.current_step,
            user=user,
            notes=notes,
            instrument_run=instrument_run,
            qc_passed=qc_passed,
            qc_notes=qc_notes,
        )

        # Handle status-specific actions
        self._handle_status_change(sample, old_status, new_status)

        return history

    def _handle_status_change(self, sample, old_status, new_status):
        """Handle any status-specific actions after transition."""
        # Update MolecularSample status on lab_order relationship
        if new_status == 'REPORTED':
            # Update the parent lab order if needed
            pass

        # Handle CANCELLED status
        if new_status == 'CANCELLED':
            sample.is_active = False
            sample.save()

        # Handle FAILED status
        if new_status == 'FAILED':
            # Could trigger alerts, notifications, etc.
            pass

    def bulk_transition(self, samples, new_status, user=None, notes='',
                        instrument_run=None):
        """
        Transition multiple samples to a new status.

        Args:
            samples: Queryset or list of MolecularSample instances
            new_status: Target status code
            user: User performing the transition
            notes: Optional notes
            instrument_run: Associated InstrumentRun

        Returns:
            Tuple of (successful_count, failed_samples)
        """
        successful = 0
        failed = []

        for sample in samples:
            try:
                self.transition(
                    sample=sample,
                    new_status=new_status,
                    user=user,
                    notes=notes,
                    instrument_run=instrument_run
                )
                successful += 1
            except ValueError as e:
                failed.append((sample, str(e)))

        return successful, failed

    def get_workflow_summary(self):
        """Get summary of samples at each workflow stage."""
        from ..models import MolecularSample
        from django.db.models import Count

        return MolecularSample.objects.filter(
            is_active=True
        ).values('workflow_status').annotate(
            count=Count('id')
        ).order_by('workflow_status')

    def get_samples_at_status(self, status):
        """Get all active samples at a specific status."""
        from ..models import MolecularSample

        return MolecularSample.objects.filter(
            workflow_status=status,
            is_active=True
        ).select_related(
            'lab_order__patient',
            'sample_type',
            'test_panel'
        ).order_by('received_datetime')

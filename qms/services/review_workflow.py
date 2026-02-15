# qms/services/review_workflow.py
"""
Document review workflow service.
"""

from typing import List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import (
    Document, DocumentVersion, DocumentStatus,
    DocumentReviewCycle, DocumentReviewStep, DocumentAudit
)

User = get_user_model()


class DocumentReviewWorkflow:
    """
    Service for managing document review workflows.
    """

    VALID_TRANSITIONS = {
        'DRAFT': ['IN_REVIEW', 'WITHDRAWN'],
        'IN_REVIEW': ['APPROVED', 'REJECTED', 'DRAFT'],
        'APPROVED': ['PUBLISHED', 'DRAFT'],
        'PUBLISHED': ['SUPERSEDED', 'ARCHIVED', 'WITHDRAWN'],
        'REJECTED': ['DRAFT'],
        'SUPERSEDED': ['ARCHIVED'],
        'ARCHIVED': ['DRAFT'],  # Allow restoration
        'WITHDRAWN': ['DRAFT'],
    }

    def __init__(self, document: Document):
        """
        Initialize workflow service for a document.

        Args:
            document: The document to manage
        """
        self.document = document

    def initiate_review(
        self,
        version: DocumentVersion,
        reviewers: List[User],
        initiated_by: User,
        due_date: Optional[timezone.datetime] = None,
        comment: str = '',
    ) -> Tuple[bool, str, Optional[DocumentReviewCycle]]:
        """
        Initiate a review cycle for a document version.

        Args:
            version: The version to review
            reviewers: List of users to review the document
            initiated_by: User initiating the review
            due_date: Optional due date for the review
            comment: Optional comment

        Returns:
            Tuple of (success, message, review_cycle)
        """
        current_status = self.document.current_status

        if current_status not in ['DRAFT', 'REJECTED']:
            return (False, f"Cannot initiate review from status: {current_status}", None)

        if not reviewers:
            return (False, "At least one reviewer is required", None)

        with transaction.atomic():
            # Create review cycle
            review_cycle = DocumentReviewCycle.objects.create(
                document=self.document,
                version=version,
                initiated_by=initiated_by,
                due_date=due_date,
                comment=comment,
            )

            # Create review steps
            for i, reviewer in enumerate(reviewers):
                DocumentReviewStep.objects.create(
                    review_cycle=review_cycle,
                    reviewer=reviewer,
                    sequence=i + 1,
                )

            # Transition document to IN_REVIEW
            self.transition_status(
                new_status='IN_REVIEW',
                user=initiated_by,
                version=version,
                comment=f"Review initiated with {len(reviewers)} reviewer(s)"
            )

            # Log audit
            DocumentAudit.objects.create(
                document=self.document,
                version=version,
                action='STATUS_CHANGED',
                user=initiated_by,
                details={'from': 'DRAFT', 'to': 'IN_REVIEW', 'reviewers': [r.id for r in reviewers]}
            )

        return (True, "Review cycle initiated successfully", review_cycle)

    def submit_review(
        self,
        review_step: DocumentReviewStep,
        approved: bool,
        comment: str = '',
    ) -> Tuple[bool, str]:
        """
        Submit a review decision for a review step.

        Args:
            review_step: The review step to update
            approved: True if approved, False if rejected
            comment: Review comment

        Returns:
            Tuple of (success, message)
        """
        if review_step.status != 'PENDING':
            return (False, f"Review step is already {review_step.get_status_display()}")

        with transaction.atomic():
            if approved:
                review_step.approve(comment)
                action = 'APPROVED'
            else:
                review_step.reject(comment)
                action = 'REJECTED'

            # Log audit
            DocumentAudit.objects.create(
                document=self.document,
                version=review_step.review_cycle.version,
                action=action,
                user=review_step.reviewer,
                details={'step_id': review_step.id, 'comment': comment}
            )

            # Check if review cycle is complete
            cycle = review_step.review_cycle

            if cycle.has_rejection:
                # Any rejection fails the review
                cycle.status = 'COMPLETED'
                cycle.completed_at = timezone.now()
                cycle.save()

                self.transition_status(
                    new_status='REJECTED',
                    user=review_step.reviewer,
                    version=cycle.version,
                    comment="Review rejected"
                )
                return (True, "Review rejected. Document returned to draft.")

            elif cycle.all_approved:
                # All required reviews approved
                cycle.status = 'COMPLETED'
                cycle.completed_at = timezone.now()
                cycle.save()

                self.transition_status(
                    new_status='APPROVED',
                    user=review_step.reviewer,
                    version=cycle.version,
                    comment="All reviews approved"
                )
                return (True, "All reviews complete. Document approved.")

        return (True, f"Review {action.lower()}. Waiting for other reviewers.")

    def transition_status(
        self,
        new_status: str,
        user: User,
        version: Optional[DocumentVersion] = None,
        comment: str = '',
        effective_date: Optional[timezone.datetime] = None,
    ) -> Tuple[bool, str]:
        """
        Transition document to a new status.

        Args:
            new_status: Target status
            user: User making the transition
            version: Document version (optional)
            comment: Transition comment
            effective_date: For published documents

        Returns:
            Tuple of (success, message)
        """
        current_status = self.document.current_status
        valid_transitions = self.VALID_TRANSITIONS.get(current_status, [])

        if new_status not in valid_transitions:
            return (False, f"Invalid transition from {current_status} to {new_status}")

        with transaction.atomic():
            status_record = DocumentStatus.objects.create(
                document=self.document,
                version=version or self.document.latest_version,
                status=new_status,
                user=user,
                comment=comment,
                effective_date=effective_date,
            )

            # Handle special status transitions
            if new_status == 'PUBLISHED':
                # Set next review date
                if self.document.review_interval_days:
                    self.document.next_review_date = (
                        timezone.now().date() +
                        timezone.timedelta(days=self.document.review_interval_days)
                    )
                    self.document.save()

            elif new_status == 'ARCHIVED':
                self.document.is_archived = True
                self.document.archived_date = timezone.now()
                self.document.archived_by = user
                self.document.save()

            # Log audit
            DocumentAudit.objects.create(
                document=self.document,
                version=version,
                action='STATUS_CHANGED',
                user=user,
                details={'from': current_status, 'to': new_status, 'comment': comment}
            )

        return (True, f"Document transitioned to {new_status}")

    def publish(
        self,
        user: User,
        effective_date: Optional[timezone.datetime] = None,
    ) -> Tuple[bool, str]:
        """
        Publish an approved document.

        Args:
            user: User publishing the document
            effective_date: When the document becomes effective

        Returns:
            Tuple of (success, message)
        """
        if self.document.current_status != 'APPROVED':
            return (False, "Only approved documents can be published")

        return self.transition_status(
            new_status='PUBLISHED',
            user=user,
            version=self.document.latest_version,
            comment="Document published",
            effective_date=effective_date or timezone.now().date()
        )

    def archive(self, user: User, reason: str = '') -> Tuple[bool, str]:
        """
        Archive a document.

        Args:
            user: User archiving the document
            reason: Reason for archiving

        Returns:
            Tuple of (success, message)
        """
        return self.transition_status(
            new_status='ARCHIVED',
            user=user,
            comment=reason or "Document archived"
        )

    def get_pending_reviews(self, user: User) -> List[DocumentReviewStep]:
        """
        Get pending review steps for a user.

        Args:
            user: The user to check

        Returns:
            List of pending review steps
        """
        return DocumentReviewStep.objects.filter(
            reviewer=user,
            status='PENDING',
            review_cycle__status='IN_PROGRESS'
        ).select_related('review_cycle__document', 'review_cycle__version')

    @classmethod
    def get_documents_due_for_review(cls, laboratory_id: int, days_ahead: int = 30):
        """
        Get documents due for periodic review.

        Args:
            laboratory_id: Laboratory to check
            days_ahead: Days to look ahead

        Returns:
            QuerySet of documents due for review
        """
        cutoff_date = timezone.now().date() + timezone.timedelta(days=days_ahead)

        return Document.objects.filter(
            laboratory_id=laboratory_id,
            is_active=True,
            is_archived=False,
            next_review_date__lte=cutoff_date
        ).order_by('next_review_date')

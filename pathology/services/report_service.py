# pathology/services/report_service.py
"""
Pathology report service for generating, signing, and amending reports.
"""

from typing import Tuple, Optional, Dict
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import hashlib

from ..models import Pathology, PathologyAddendum, Histology

User = get_user_model()


class PathologyReportService:
    """
    Service for managing pathology reports.
    """

    def __init__(self, pathology: Pathology):
        """
        Initialize service for a pathology report.

        Args:
            pathology: The pathology report to manage
        """
        self.pathology = pathology

    def generate_report(
        self,
        diagnosis: str,
        microscopic_description: str = '',
        gross_description: str = '',
        comment: str = '',
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Generate/update report content.

        Args:
            diagnosis: Final diagnosis text
            microscopic_description: Microscopic findings
            gross_description: Gross description
            comment: Additional comments
            **kwargs: Additional fields to update

        Returns:
            Tuple of (success, message)
        """
        if self.pathology.status in ('FINAL', 'AMENDED'):
            return (False, "Cannot modify a finalized report. Use amend_report instead.")

        with transaction.atomic():
            self.pathology.diagnosis = diagnosis
            self.pathology.microscopic_description = microscopic_description
            self.pathology.gross_description = gross_description
            self.pathology.comment = comment

            # Update additional fields
            for field, value in kwargs.items():
                if hasattr(self.pathology, field):
                    setattr(self.pathology, field, value)

            self.pathology.status = 'DRAFT'
            self.pathology.save()

        return (True, "Report generated successfully")

    def submit_for_review(self, user: User) -> Tuple[bool, str]:
        """
        Submit report for pathologist review.

        Args:
            user: User submitting the report

        Returns:
            Tuple of (success, message)
        """
        if self.pathology.status not in ('DRAFT', 'PRELIMINARY'):
            return (False, f"Cannot submit report with status: {self.pathology.status}")

        if not self.pathology.diagnosis:
            return (False, "Cannot submit report without a diagnosis")

        self.pathology.status = 'PENDING_REVIEW'
        self.pathology.save()

        return (True, "Report submitted for review")

    def sign_report(
        self,
        pathologist: User,
        is_preliminary: bool = False,
    ) -> Tuple[bool, str]:
        """
        Sign and finalize the pathology report.

        Args:
            pathologist: Signing pathologist
            is_preliminary: If True, mark as preliminary instead of final

        Returns:
            Tuple of (success, message)
        """
        if self.pathology.status == 'FINAL':
            return (False, "Report is already finalized")

        if not self.pathology.diagnosis:
            return (False, "Cannot sign report without a diagnosis")

        with transaction.atomic():
            self.pathology.pathologist = pathologist
            self.pathology.signed_date = timezone.now()

            # Generate signature hash
            signature_content = f"{self.pathology.pathology_id}:{self.pathology.diagnosis}:{pathologist.id}:{self.pathology.signed_date.isoformat()}"
            self.pathology.signature_hash = hashlib.sha256(signature_content.encode()).hexdigest()

            if is_preliminary:
                self.pathology.status = 'PRELIMINARY'
            else:
                self.pathology.status = 'FINAL'

            self.pathology.save()

            # Update histology status if linked
            if self.pathology.histology:
                self.pathology.histology.status = 'REPORTED'
                self.pathology.histology.save()

        status_text = "preliminary" if is_preliminary else "final"
        return (True, f"Report signed and marked as {status_text}")

    def amend_report(
        self,
        user: User,
        new_diagnosis: str,
        amendment_reason: str,
    ) -> Tuple[bool, str]:
        """
        Amend a finalized report.

        Args:
            user: User making the amendment
            new_diagnosis: New diagnosis text
            amendment_reason: Reason for amendment

        Returns:
            Tuple of (success, message)
        """
        if self.pathology.status not in ('FINAL', 'AMENDED'):
            return (False, "Only finalized reports can be amended")

        if not amendment_reason:
            return (False, "Amendment reason is required")

        with transaction.atomic():
            # Store original diagnosis on first amendment
            if not self.pathology.original_diagnosis:
                self.pathology.original_diagnosis = self.pathology.diagnosis

            self.pathology.diagnosis = new_diagnosis
            self.pathology.status = 'AMENDED'
            self.pathology.amended_by = user
            self.pathology.amended_date = timezone.now()
            self.pathology.amendment_reason = amendment_reason

            # Re-sign with new hash
            signature_content = f"{self.pathology.pathology_id}:{new_diagnosis}:{user.id}:{timezone.now().isoformat()}:AMENDED"
            self.pathology.signature_hash = hashlib.sha256(signature_content.encode()).hexdigest()

            self.pathology.save()

        return (True, "Report amended successfully")

    def add_addendum(
        self,
        author: User,
        content: str,
        reason: str = '',
    ) -> Tuple[bool, str, Optional[PathologyAddendum]]:
        """
        Add an addendum to the report.

        Args:
            author: Author of the addendum
            content: Addendum content
            reason: Reason for addendum

        Returns:
            Tuple of (success, message, addendum)
        """
        if self.pathology.status not in ('PRELIMINARY', 'FINAL', 'AMENDED'):
            return (False, "Addenda can only be added to signed reports", None)

        # Get next addendum number
        last_addendum = self.pathology.addenda.order_by('-addendum_number').first()
        next_number = (last_addendum.addendum_number + 1) if last_addendum else 1

        addendum = PathologyAddendum.objects.create(
            pathology=self.pathology,
            addendum_number=next_number,
            content=content,
            reason=reason,
            author=author,
        )

        return (True, f"Addendum {next_number} added successfully", addendum)

    def get_report_content(self) -> Dict:
        """
        Get complete report content for rendering.

        Returns:
            Dictionary with all report content
        """
        from .staging_service import TNMStagingService

        content = {
            'header': {
                'pathology_id': self.pathology.pathology_id,
                'patient': {
                    'name': str(self.pathology.patient),
                    'id': self.pathology.patient.OP_NO if hasattr(self.pathology.patient, 'OP_NO') else None,
                },
                'specimen_received': self.pathology.histology.received_datetime if self.pathology.histology else None,
                'report_date': self.pathology.signed_date,
                'status': self.pathology.get_status_display(),
            },
            'specimen': {
                'type': str(self.pathology.pathology_type) if self.pathology.pathology_type else None,
                'site': str(self.pathology.tumor_site) if self.pathology.tumor_site else None,
            },
            'diagnosis': self.pathology.diagnosis,
            'gross_description': self.pathology.gross_description,
            'microscopic_description': self.pathology.microscopic_description,
            'comment': self.pathology.comment,
            'clinical_correlation': self.pathology.clinical_correlation,
            'staging': TNMStagingService.get_staging_summary(self.pathology),
            'ihc_results': self.pathology.ihc_results,
            'molecular_findings': self.pathology.molecular_findings,
            'synoptic_data': self.pathology.synoptic_data,
            'signature': {
                'pathologist': str(self.pathology.pathologist) if self.pathology.pathologist else None,
                'signed_date': self.pathology.signed_date,
                'is_amended': self.pathology.status == 'AMENDED',
                'amendment_reason': self.pathology.amendment_reason if self.pathology.status == 'AMENDED' else None,
            },
            'addenda': [
                {
                    'number': a.addendum_number,
                    'content': a.content,
                    'author': str(a.author),
                    'date': a.signed_date,
                }
                for a in self.pathology.addenda.all()
            ],
        }

        return content

    @classmethod
    def create_from_histology(
        cls,
        histology: Histology,
        pathology_type,
        created_by: User,
    ) -> Pathology:
        """
        Create a new pathology report from a histology specimen.

        Args:
            histology: Source histology specimen
            pathology_type: Type of pathology examination
            created_by: User creating the report

        Returns:
            New Pathology instance
        """
        pathology = Pathology.objects.create(
            laboratory=histology.laboratory,
            patient=histology.patient,
            histology=histology,
            lab_order=histology.lab_order,
            pathology_type=pathology_type,
            tumor_site=histology.specimen_site,
            gross_description=histology.gross_description,
            created_by=created_by,
        )

        # Update histology status
        histology.status = 'IN_REVIEW'
        histology.save()

        return pathology

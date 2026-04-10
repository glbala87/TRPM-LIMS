"""
Compliance models for TRPM-LIMS.

Provides models for tracking consent protocols, IRB approvals,
and patient consent management.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class ConsentProtocol(models.Model):
    """
    Model representing an IRB-approved consent protocol.

    Tracks different versions of consent protocols, their effective dates,
    and active status for regulatory compliance.
    """

    PROTOCOL_TYPE_CHOICES = [
        ('GENERAL', 'General Research Consent'),
        ('GENETIC', 'Genetic Testing Consent'),
        ('BIOBANK', 'Biobanking Consent'),
        ('CLINICAL_TRIAL', 'Clinical Trial Consent'),
        ('DATA_SHARING', 'Data Sharing Consent'),
        ('PEDIATRIC', 'Pediatric Assent/Consent'),
        ('EMERGENCY', 'Emergency Research Consent'),
        ('OTHER', 'Other'),
    ]

    # Basic information
    name = models.CharField(
        max_length=255,
        help_text="Name of the consent protocol"
    )
    version = models.CharField(
        max_length=50,
        help_text="Version identifier (e.g., '1.0', '2.1', 'A')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the consent protocol"
    )

    # Protocol type and classification
    protocol_type = models.CharField(
        max_length=20,
        choices=PROTOCOL_TYPE_CHOICES,
        default='GENERAL',
        help_text="Type of consent protocol"
    )

    # IRB information
    irb_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="IRB protocol number"
    )
    irb_approval_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of IRB approval"
    )
    irb_expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of IRB expiration"
    )

    # Dates and status
    effective_date = models.DateField(
        help_text="Date when this protocol version becomes effective"
    )
    expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this protocol version expires (if applicable)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this protocol is currently active"
    )

    # Document storage
    document = models.FileField(
        upload_to='consent_protocols/',
        blank=True,
        null=True,
        help_text="PDF or document file of the consent form"
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_consent_protocols',
        help_text="User who created this protocol"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Requirements
    requires_witness = models.BooleanField(
        default=False,
        help_text="Whether this consent requires a witness signature"
    )
    requires_legal_representative = models.BooleanField(
        default=False,
        help_text="Whether this consent can be signed by a legal representative"
    )
    minimum_age = models.PositiveIntegerField(
        default=18,
        help_text="Minimum age for direct consent"
    )

    class Meta:
        verbose_name = 'Consent Protocol'
        verbose_name_plural = 'Consent Protocols'
        ordering = ['-effective_date', 'name']
        unique_together = ['name', 'version']
        indexes = [
            models.Index(fields=['is_active', 'effective_date']),
            models.Index(fields=['irb_number']),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def clean(self):
        """Validate the protocol data."""
        super().clean()

        # Validate expiration date is after effective date
        if self.expiration_date and self.effective_date:
            if self.expiration_date <= self.effective_date:
                raise ValidationError({
                    'expiration_date': 'Expiration date must be after effective date.'
                })

        # Validate IRB expiration is after approval
        if self.irb_expiration_date and self.irb_approval_date:
            if self.irb_expiration_date <= self.irb_approval_date:
                raise ValidationError({
                    'irb_expiration_date': 'IRB expiration date must be after approval date.'
                })

    @property
    def is_expired(self):
        """Check if the protocol has expired."""
        if self.expiration_date:
            return timezone.now().date() > self.expiration_date
        return False

    @property
    def is_irb_expired(self):
        """Check if the IRB approval has expired."""
        if self.irb_expiration_date:
            return timezone.now().date() > self.irb_expiration_date
        return False

    @classmethod
    def get_active_protocols(cls):
        """Get all currently active protocols."""
        today = timezone.now().date()
        return cls.objects.filter(
            is_active=True,
            effective_date__lte=today
        ).exclude(
            expiration_date__lt=today
        )


class PatientConsent(models.Model):
    """
    Model representing a patient's consent to a specific protocol.

    Tracks consent status, dates, witness information, and withdrawal
    details for regulatory compliance and audit purposes.
    """

    CONSENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONSENTED', 'Consented'),
        ('DECLINED', 'Declined'),
        ('WITHDRAWN', 'Withdrawn'),
        ('EXPIRED', 'Expired'),
    ]

    CONSENT_METHOD_CHOICES = [
        ('IN_PERSON', 'In Person'),
        ('ELECTRONIC', 'Electronic Signature'),
        ('PHONE', 'Phone Consent'),
        ('MAIL', 'Written Mail'),
        ('LAR', 'Legally Authorized Representative'),
    ]

    # Patient reference - using string reference to avoid circular imports
    patient = models.ForeignKey(
        'lab_management.Patient',
        on_delete=models.CASCADE,
        related_name='consents',
        help_text="Patient who provided consent"
    )

    # Protocol reference
    protocol = models.ForeignKey(
        ConsentProtocol,
        on_delete=models.PROTECT,
        related_name='patient_consents',
        help_text="Consent protocol being consented to"
    )

    # Consent information
    status = models.CharField(
        max_length=20,
        choices=CONSENT_STATUS_CHOICES,
        default='PENDING',
        help_text="Current consent status"
    )
    consent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when consent was provided"
    )
    consent_method = models.CharField(
        max_length=20,
        choices=CONSENT_METHOD_CHOICES,
        default='IN_PERSON',
        help_text="Method of obtaining consent"
    )

    # Who obtained consent
    consented_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='obtained_consents',
        help_text="Staff member who obtained the consent"
    )

    # Witness information (if required)
    witness_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the witness (if required)"
    )
    witness_signature_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of witness signature"
    )

    # Legal representative information
    representative_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of legally authorized representative (if applicable)"
    )
    representative_relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Relationship to patient (e.g., Parent, Guardian, POA)"
    )

    # Withdrawal information
    withdrawal_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of consent withdrawal"
    )
    withdrawal_reason = models.TextField(
        blank=True,
        help_text="Reason for withdrawing consent"
    )
    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals',
        help_text="Staff member who processed the withdrawal"
    )

    # Activity status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this consent is currently active"
    )

    # Document storage
    signed_document = models.FileField(
        upload_to='signed_consents/',
        blank=True,
        null=True,
        help_text="Scanned copy of signed consent form"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the consent"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Consent'
        verbose_name_plural = 'Patient Consents'
        ordering = ['-consent_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['protocol', 'status']),
            models.Index(fields=['consent_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        patient_str = str(self.patient) if self.patient else 'Unknown Patient'
        return f"{patient_str} - {self.protocol.name} ({self.status})"

    def clean(self):
        """Validate the consent data."""
        super().clean()

        # Validate consent date for consented status
        if self.status == 'CONSENTED' and not self.consent_date:
            raise ValidationError({
                'consent_date': 'Consent date is required when status is Consented.'
            })

        # Validate withdrawal date for withdrawn status
        if self.status == 'WITHDRAWN' and not self.withdrawal_date:
            raise ValidationError({
                'withdrawal_date': 'Withdrawal date is required when status is Withdrawn.'
            })

        # Validate witness information if required
        if self.protocol and self.protocol.requires_witness:
            if self.status == 'CONSENTED' and not self.witness_name:
                raise ValidationError({
                    'witness_name': 'Witness name is required for this protocol.'
                })

    def give_consent(self, consented_by=None, method='IN_PERSON',
                     witness_name=None, representative_name=None,
                     representative_relationship=None):
        """
        Record that consent was given.

        Args:
            consented_by: User who obtained the consent
            method: Method of obtaining consent
            witness_name: Name of witness (if applicable)
            representative_name: Name of legal representative (if applicable)
            representative_relationship: Relationship to patient (if applicable)
        """
        self.status = 'CONSENTED'
        self.consent_date = timezone.now()
        self.consented_by = consented_by
        self.consent_method = method
        self.is_active = True

        if witness_name:
            self.witness_name = witness_name
            self.witness_signature_date = timezone.now()

        if representative_name:
            self.representative_name = representative_name
            self.representative_relationship = representative_relationship or ''

        self.save()

    def withdraw_consent(self, withdrawn_by=None, reason=''):
        """
        Record that consent was withdrawn.

        Args:
            withdrawn_by: User who processed the withdrawal
            reason: Reason for withdrawal
        """
        self.status = 'WITHDRAWN'
        self.withdrawal_date = timezone.now()
        self.withdrawn_by = withdrawn_by
        self.withdrawal_reason = reason
        self.is_active = False
        self.save()

    def decline_consent(self, consented_by=None, notes=''):
        """
        Record that consent was declined.

        Args:
            consented_by: User who documented the decline
            notes: Notes about the decline
        """
        self.status = 'DECLINED'
        self.consent_date = timezone.now()
        self.consented_by = consented_by
        self.is_active = False
        if notes:
            self.notes = notes
        self.save()

    @property
    def is_valid(self):
        """Check if the consent is currently valid."""
        if not self.is_active:
            return False
        if self.status != 'CONSENTED':
            return False
        if self.protocol.is_expired:
            return False
        return True

    @classmethod
    def get_active_consents_for_patient(cls, patient):
        """Get all active consents for a patient."""
        return cls.objects.filter(
            patient=patient,
            is_active=True,
            status='CONSENTED'
        ).select_related('protocol')

    @classmethod
    def has_valid_consent(cls, patient, protocol):
        """Check if a patient has valid consent for a specific protocol."""
        return cls.objects.filter(
            patient=patient,
            protocol=protocol,
            is_active=True,
            status='CONSENTED'
        ).exists()


# ---------------------------------------------------------------------------
# 21 CFR Part 11 — Electronic signature
# ---------------------------------------------------------------------------
class ElectronicSignature(models.Model):
    """
    21 CFR Part 11-compliant electronic signature.

    An ElectronicSignature record is the machine-readable proof that a
    named, authenticated individual applied a signature to a specific
    record for a specific reason at a specific point in time.

    Per 21 CFR 11.50, an e-signature must capture:
      - The printed name of the signer
      - The date and time of signing
      - The meaning/reason for the signing (e.g., approval, authorship,
        responsibility, review)

    Per 21 CFR 11.70, e-signatures must be linked to their records such
    that they cannot be excised, copied, or otherwise transferred —
    enforced here by the immutable FK + the snapshot JSON of what was
    signed, and by blocking updates/deletes of saved records.

    This model is ALWAYS loaded, but is only *required* on result-release
    workflows when `settings.ENABLE_PART11` is True. Research deployments
    may still record signatures voluntarily.
    """

    REASON_CHOICES = [
        ('AUTHORSHIP', 'Authorship'),
        ('REVIEW', 'Review'),
        ('APPROVAL', 'Approval'),
        ('RESPONSIBILITY', 'Responsibility'),
        ('RELEASE', 'Release to patient/clinician'),
        ('AMENDMENT', 'Amendment'),
        ('WITNESS', 'Witness'),
        ('REJECTION', 'Rejection'),
        ('OTHER', 'Other (see notes)'),
    ]

    METHOD_CHOICES = [
        ('PASSWORD', 'Username + password re-authentication'),
        ('BIOMETRIC', 'Biometric'),
        ('SMARTCARD', 'Smart card / PKI'),
        ('MFA', 'Multi-factor authentication'),
    ]

    # --- What was signed (immutable generic reference) ---
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.PROTECT,
        help_text='Model of the signed record.',
    )
    object_id = models.PositiveIntegerField(
        help_text='Primary key of the signed record.',
    )
    record_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text='Snapshot of the record state at the moment of signing '
                  '(for non-repudiation — prevents after-the-fact edits '
                  'from altering what the signer actually approved).',
    )

    # --- Who signed (frozen at sign time — FK is SET_NULL so user deletion
    # does not erase the audit trail, but signer_name/signer_username are
    # captured verbatim so the signature remains interpretable) ---
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='electronic_signatures',
    )
    signer_username = models.CharField(max_length=150)
    signer_full_name = models.CharField(max_length=300)
    signer_role = models.CharField(
        max_length=100,
        blank=True,
        help_text='Role/title at time of signing (e.g., "Laboratory Director").',
    )

    # --- Why, how, when ---
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    meaning = models.CharField(
        max_length=500,
        help_text='Free-text meaning of the signature, as displayed to the '
                  'signer at the moment of signing (21 CFR 11.50).',
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='PASSWORD',
    )
    signed_at = models.DateTimeField(default=timezone.now, db_index=True)

    # --- Context (for forensic review / chain of custody) ---
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # --- Cryptographic integrity ---
    # sha256 hex digest of a canonical serialization of the signer+reason+
    # snapshot+signed_at tuple. Allows detection of tampering even if DB
    # rows are modified outside the ORM.
    integrity_hash = models.CharField(max_length=64, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Electronic Signature'
        verbose_name_plural = 'Electronic Signatures'
        ordering = ['-signed_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-signed_at']),
            models.Index(fields=['signer', '-signed_at']),
        ]

    def __str__(self):
        return (
            f'{self.signer_username} [{self.get_reason_display()}] '
            f'@ {self.signed_at:%Y-%m-%d %H:%M:%S}'
        )

    # --- Immutability enforcement (21 CFR 11.70) ---
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Saved signatures are immutable. Tampering is an audit failure.
            raise ValidationError(
                'Electronic signatures are immutable and cannot be modified '
                'after creation (21 CFR 11.70).'
            )
        if not self.integrity_hash:
            self.integrity_hash = self._compute_integrity_hash()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            'Electronic signatures are immutable and cannot be deleted.'
        )

    def _compute_integrity_hash(self) -> str:
        import hashlib
        import json
        payload = {
            'content_type_id': self.content_type_id,
            'object_id': self.object_id,
            'signer_username': self.signer_username,
            'signer_full_name': self.signer_full_name,
            'reason': self.reason,
            'meaning': self.meaning,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'record_snapshot': self.record_snapshot,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()

    def verify_integrity(self) -> bool:
        """Recompute the integrity hash and compare to the stored one."""
        return self.integrity_hash == self._compute_integrity_hash()

    @classmethod
    def sign(cls, *, record, signer, reason, meaning, method='PASSWORD',
             request=None, notes=''):
        """
        Record an electronic signature on an arbitrary model instance.

        Callers are responsible for having just re-authenticated the signer
        (per 21 CFR 11.200) before calling this method.
        """
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(record)
        snapshot = cls._build_snapshot(record)

        sig = cls(
            content_type=ct,
            object_id=record.pk,
            record_snapshot=snapshot,
            signer=signer,
            signer_username=signer.get_username() if signer else '',
            signer_full_name=(
                signer.get_full_name() if signer and hasattr(signer, 'get_full_name')
                else ''
            ),
            reason=reason,
            meaning=meaning,
            method=method,
            notes=notes,
        )
        if request is not None:
            sig.ip_address = cls._client_ip(request)
            sig.user_agent = request.META.get('HTTP_USER_AGENT', '')[:1000]
        sig.save()
        return sig

    @staticmethod
    def _build_snapshot(record) -> dict:
        from django.db.models.fields.files import FieldFile
        from decimal import Decimal

        snap = {}
        for f in record._meta.fields:
            val = getattr(record, f.name)
            if val is None:
                snap[f.name] = None
            elif isinstance(val, FieldFile):
                snap[f.name] = val.name or None
            elif isinstance(val, Decimal):
                snap[f.name] = float(val)
            elif hasattr(val, 'isoformat'):
                snap[f.name] = val.isoformat()
            elif hasattr(val, 'pk'):
                snap[f.name] = val.pk
            else:
                snap[f.name] = val if isinstance(val, (str, int, float, bool, list, dict)) else str(val)
        return snap

    @staticmethod
    def _client_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

"""
Part 11 signature enforcement helpers.

When `settings.ENABLE_PART11` is True, critical workflow transitions
(result review, result approval, result release) must be accompanied by
a valid electronic signature per 21 CFR 11.50 / 11.70 / 11.200.

Usage from a DRF view::

    from compliance.enforcement import enforce_esignature

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        result = self.get_object()
        signature = enforce_esignature(
            request=request,
            record=result,
            default_reason='APPROVAL',
            default_meaning='I approve this result for release.',
        )
        # ... proceed with approval; `signature` may be None if
        # enforcement is off and the caller did not volunteer one.

The helper:
  1. Checks `settings.ENABLE_PART11`. When off, accepts an optional
     signature payload but does not require one.
  2. When on, requires `password`, `reason`, `meaning` in the request body
     and re-authenticates the current user.
  3. Creates and returns an immutable :class:`ElectronicSignature`.
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import ElectronicSignature


def enforce_esignature(
    *,
    request,
    record,
    default_reason: str = 'APPROVAL',
    default_meaning: str = '',
) -> ElectronicSignature | None:
    """
    Validate and record an electronic signature for a workflow transition.

    Returns the :class:`ElectronicSignature` instance if one was created,
    or ``None`` when enforcement is off and the caller did not supply
    signature fields.

    Raises :class:`rest_framework.exceptions.ValidationError` if
    enforcement is on and the signature payload is missing/invalid.
    Raises :class:`rest_framework.exceptions.PermissionDenied` on
    re-authentication failure.
    """
    data = request.data or {}
    signing = any(k in data for k in ('password', 'reason', 'meaning'))

    # Fast path: enforcement off and caller didn't try to sign.
    if not getattr(settings, 'ENABLE_PART11', False) and not signing:
        return None

    if getattr(settings, 'ENABLE_PART11', False):
        missing = [k for k in ('password', 'reason', 'meaning') if not data.get(k)]
        if missing:
            raise ValidationError(
                {k: ['This field is required when ENABLE_PART11 is active.'] for k in missing}
            )

    password = data.get('password')
    if password:
        # 21 CFR 11.200(a)(1) — non-biometric e-sigs require two components;
        # we combine the active session with a re-entered password.
        user = authenticate(request, username=request.user.get_username(), password=password)
        if user is None or user.pk != request.user.pk:
            raise PermissionDenied('Signature re-authentication failed.')

    reason = (data.get('reason') or default_reason).upper()
    valid_reasons = {k for k, _ in ElectronicSignature.REASON_CHOICES}
    if reason not in valid_reasons:
        raise ValidationError({'reason': [f'Must be one of: {sorted(valid_reasons)}']})

    meaning = data.get('meaning') or default_meaning
    if not meaning:
        raise ValidationError({'meaning': ['A human-readable meaning is required.']})

    return ElectronicSignature.sign(
        record=record,
        signer=request.user,
        reason=reason,
        meaning=meaning,
        method='PASSWORD',
        request=request,
    )

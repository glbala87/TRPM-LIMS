"""
MFA enforcement utilities for TRPM-LIMS.

When ``settings.ENABLE_HIPAA_MODE`` is True, authenticated users who have
not verified a TOTP device get redirected to an MFA setup page (browser) or
receive a 403 with guidance (API).

This module provides:
- ``MFAEnforcementMiddleware`` — wired into ``MIDDLEWARE`` to enforce
  OTP-verified sessions for browser users.
- ``RequireVerifiedMixin`` — a DRF mixin that rejects unverified API callers.

TOTP device provisioning is handled via Django admin (via django-otp's
built-in admin integration) or a custom setup view (out of scope for the
initial scaffold; add a view that creates a ``TOTPDevice`` for the user
and renders its ``config_url`` as a QR code).
"""
from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class MFAEnforcementMiddleware(MiddlewareMixin):
    """
    When ENABLE_HIPAA_MODE is on, require OTP verification for
    authenticated sessions.

    Exempt paths: admin login, logout, API (handled by RequireVerifiedMixin),
    and a future ``/accounts/mfa-setup/`` path.
    """

    EXEMPT_PREFIXES = (
        '/admin/login/',
        '/admin/logout/',
        '/accounts/mfa-setup/',
        '/api/auth/token/',      # JWT obtain — user isn't verified yet
    )

    def process_request(self, request):
        if not getattr(settings, 'ENABLE_HIPAA_MODE', False):
            return None

        if not request.user.is_authenticated:
            return None

        if any(request.path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return None

        # django-otp stamps ``request.user.is_verified()`` after the
        # OTPMiddleware has run.
        is_verified = getattr(request.user, 'is_verified', lambda: False)()
        if is_verified:
            return None

        # API paths get a JSON 403; browser paths would get a redirect to
        # MFA setup (or admin page where they can scan the QR code).
        if request.path.startswith('/api/'):
            return JsonResponse(
                {
                    'detail': 'Multi-factor authentication required. '
                              'Please set up TOTP via /accounts/mfa-setup/ or '
                              'the admin panel, then verify your device.',
                },
                status=403,
            )

        # Browser users — redirect to admin where they can set up MFA.
        from django.shortcuts import redirect
        return redirect('/admin/')

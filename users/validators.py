"""
Custom Django password validators for TRPM-LIMS.

Wire these in via `AUTH_PASSWORD_VALIDATORS` in settings.py; see the block
added for password aging below.
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordHistoryValidator:
    """
    Reject passwords that match any of the user's last N password hashes.

    Config::
        {
            'NAME': 'users.validators.PasswordHistoryValidator',
            'OPTIONS': {'history_length': 5},
        }
    """

    def __init__(self, history_length: int = 5):
        self.history_length = history_length

    def validate(self, password, user=None):
        if user is None or not user.pk:
            return
        from .models import PasswordHistory

        recent = PasswordHistory.objects.filter(user=user).order_by('-created_at')[: self.history_length]
        for entry in recent:
            if check_password(password, entry.password_hash):
                raise ValidationError(
                    _('You cannot reuse any of your last %(n)d passwords.'),
                    code='password_reused',
                    params={'n': self.history_length},
                )

    def get_help_text(self):
        return _(
            'Your password cannot be one of your last %(n)d passwords.'
        ) % {'n': self.history_length}


class PasswordMaxAgeValidator:
    """
    Enforce that passwords are not older than ``max_age_days`` at validation
    time. Applied when a user attempts to log in with an expired password;
    `users.middleware.PasswordExpiryMiddleware` uses this alongside
    ``UserProfile.last_password_change`` to decide when to force a change.

    This validator does not reject *new* passwords based on age — it is a
    helper used by the middleware; listing it in `AUTH_PASSWORD_VALIDATORS`
    is optional.
    """

    def __init__(self, max_age_days: int | None = None):
        self.max_age_days = max_age_days

    def validate(self, password, user=None):  # pragma: no cover - informational
        return

    def get_help_text(self):
        days = self.max_age_days or getattr(settings, 'PASSWORD_MAX_AGE_DAYS', 90)
        return _('Passwords must be changed at least every %(days)d days.') % {'days': days}

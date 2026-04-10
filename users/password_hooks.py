"""
Password lifecycle hooks.

Captures a PasswordHistory entry every time a user's password changes,
and stamps ``UserProfile.last_password_change``. Wired in via signals
in users.apps.UsersConfig.ready().
"""
from __future__ import annotations

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone


def _get_user_model():
    from django.contrib.auth import get_user_model
    return get_user_model()


@receiver(pre_save)
def _stash_old_password_hash(sender, instance, **kwargs):
    """Capture the existing password hash before save for comparison."""
    User = _get_user_model()
    if sender is not User:
        return
    if not instance.pk:
        instance._trpm_old_password_hash = None
        return
    try:
        old = User.objects.filter(pk=instance.pk).values_list('password', flat=True).first()
    except Exception:
        old = None
    instance._trpm_old_password_hash = old


@receiver(post_save)
def _record_password_change(sender, instance, created, **kwargs):
    """If the password hash changed, record history and stamp profile."""
    User = _get_user_model()
    if sender is not User:
        return
    new_hash = getattr(instance, 'password', '') or ''
    if not new_hash:
        return
    old_hash = getattr(instance, '_trpm_old_password_hash', None)
    if not created and new_hash == old_hash:
        return

    from .models import PasswordHistory, UserProfile

    try:
        PasswordHistory.objects.create(user=instance, password_hash=new_hash)
    except Exception:
        pass
    try:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.last_password_change = timezone.now()
        profile.require_password_change = False
        profile.save(update_fields=['last_password_change', 'require_password_change'])
    except Exception:
        pass

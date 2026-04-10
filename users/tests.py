"""Smoke tests for users app."""
import pytest
from users.models import Role, UserProfile

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_role_create():
    r = Role.objects.create(name='lab_tech', display_name='Laboratory Technician')
    assert r.pk is not None


def test_user_profile_auto_create(user):
    """A UserProfile should either auto-create via signal or be manually creatable."""
    profile, created = UserProfile.objects.get_or_create(user=user)
    assert profile.user == user


def test_password_history_captured_on_change(user):
    """Changing a password should record a PasswordHistory entry."""
    from users.models import PasswordHistory

    PasswordHistory.objects.filter(user=user).delete()
    user.set_password('FreshPassword123!xyz')
    user.save()
    assert PasswordHistory.objects.filter(user=user).exists()


def test_password_reuse_prevented(user):
    """The PasswordHistoryValidator should reject reused passwords."""
    from django.core.exceptions import ValidationError
    from users.validators import PasswordHistoryValidator
    from users.models import PasswordHistory

    PasswordHistory.objects.filter(user=user).delete()
    user.set_password('OldPassword-001!')
    user.save()

    validator = PasswordHistoryValidator(history_length=5)
    with pytest.raises(ValidationError):
        validator.validate('OldPassword-001!', user=user)

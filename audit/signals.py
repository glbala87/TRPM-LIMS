"""
Signal handlers for automatic audit logging.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.contenttypes.models import ContentType

from .models import AuditLog, AuditTrail
from .middleware import get_current_request, get_current_user

# Models to exclude from automatic audit logging
EXCLUDED_MODELS = [
    'Session',
    'LogEntry',
    'AuditLog',
    'AuditTrail',
    'UserSession',
    'ContentType',
    'Permission',
    'MigrationRecorder',
]

# Models that should have full audit trail (snapshots)
AUDITABLE_MODELS = [
    'MolecularSample',
    'MolecularResult',
    'Patient',
    'LabOrder',
    'Instrument',
    'MolecularReagent',
]


def should_audit(instance):
    """Check if a model instance should be audited."""
    model_name = instance.__class__.__name__
    return model_name not in EXCLUDED_MODELS


def should_create_snapshot(instance):
    """Check if a model instance should have full snapshots."""
    model_name = instance.__class__.__name__
    return model_name in AUDITABLE_MODELS


def get_changed_fields(instance, created=False):
    """
    Get the fields that changed on an instance.
    Returns dict of {field_name: {'old': value, 'new': value}}
    """
    if created:
        # For new objects, all fields are "new"
        changed = {}
        for field in instance._meta.fields:
            if field.name in ['id', 'created_at', 'updated_at']:
                continue
            value = getattr(instance, field.name)
            if hasattr(value, 'pk'):
                value = str(value)
            elif hasattr(value, 'isoformat'):
                value = value.isoformat()
            changed[field.name] = {'old': None, 'new': value}
        return changed

    # For updates, compare with stored original values
    if not hasattr(instance, '_original_values'):
        return {}

    changed = {}
    for field_name, old_value in instance._original_values.items():
        new_value = getattr(instance, field_name, None)

        # Handle foreign keys
        if hasattr(new_value, 'pk'):
            new_value_compare = new_value.pk
            new_value_display = str(new_value)
        else:
            new_value_compare = new_value
            new_value_display = new_value

        if hasattr(old_value, 'pk'):
            old_value_compare = old_value.pk
            old_value_display = str(old_value)
        else:
            old_value_compare = old_value
            old_value_display = old_value

        # Convert datetime to string for comparison
        if hasattr(new_value_compare, 'isoformat'):
            new_value_compare = new_value_compare.isoformat()
            new_value_display = new_value_compare
        if hasattr(old_value_compare, 'isoformat'):
            old_value_compare = old_value_compare.isoformat()
            old_value_display = old_value_compare

        if old_value_compare != new_value_compare:
            changed[field_name] = {
                'old': old_value_display,
                'new': new_value_display
            }

    return changed


@receiver(pre_save)
def capture_original_values(sender, instance, **kwargs):
    """Capture original values before save for change detection."""
    if not should_audit(instance):
        return

    if instance.pk:
        try:
            # Get original from database
            original = sender.objects.get(pk=instance.pk)
            instance._original_values = {}
            for field in instance._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at']:
                    instance._original_values[field.name] = getattr(original, field.name)
        except sender.DoesNotExist:
            instance._original_values = {}


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Log object creation and updates."""
    if not should_audit(instance):
        return

    request = get_current_request()
    user = get_current_user()

    action = 'CREATE' if created else 'UPDATE'
    changed_fields = get_changed_fields(instance, created)

    # Only log if there are actual changes (for updates)
    if not created and not changed_fields:
        return

    AuditLog.log_action(
        action=action,
        obj=instance,
        user=user,
        request=request,
        changed_fields=changed_fields
    )

    # Create snapshot for important models
    if should_create_snapshot(instance):
        AuditTrail.create_snapshot(instance, user, action)


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log object deletion."""
    if not should_audit(instance):
        return

    request = get_current_request()
    user = get_current_user()

    AuditLog.log_delete(instance, user, request)


# Authentication event handlers
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Log successful user login."""
    AuditLog.log_login(user, request, success=True)


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user:
        AuditLog.log_logout(user, request)


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempt."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = credentials.get('username', '')

    # Try to find the user for the failed login
    try:
        user = User.objects.get(username=username)
        AuditLog.log_login(user, request, success=False)

        # Update failed login count if user has a profile
        if hasattr(user, 'userprofile'):
            user.userprofile.record_failed_login()
    except User.DoesNotExist:
        # Log failed login for unknown user
        AuditLog.log_action(
            action='LOGIN_FAILED',
            request=request,
            notes=f"Unknown username: {username}"
        )

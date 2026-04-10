"""
Signal handlers for automatic audit logging.
"""
from decimal import Decimal
from django.db.models.fields.files import FieldFile
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.contenttypes.models import ContentType

from .models import AuditLog, AuditTrail
from .middleware import get_current_request, get_current_user


def serialize_value(value):
    """Convert a value to a JSON-serializable format."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    # Django FieldFile / ImageFieldFile — store just the stored name.
    # Accessing `.url` without a file raises ValueError, so check the class.
    if isinstance(value, FieldFile):
        return value.name or None
    if hasattr(value, 'pk'):
        return str(value)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    # Fallback — stringify anything else rather than crashing the save.
    try:
        return str(value)
    except Exception:
        return None

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
    'Migration',  # django.db.migrations.recorder.MigrationRecorder.Migration
]

# Django-internal app labels whose models must never trigger audit logging.
# In particular, the `migrations` app is used by Django's migration recorder,
# and firing signals on its rows during `contenttypes.0001_initial` tries to
# create a ContentType before the `name` column has been removed in 0002,
# which crashes test DB creation.
EXCLUDED_APP_LABELS = {
    'migrations',
    'contenttypes',
    'auth',
    'admin',
    'sessions',
    'token_blacklist',
}

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
    if model_name in EXCLUDED_MODELS:
        return False
    app_label = getattr(instance._meta, 'app_label', None)
    if app_label in EXCLUDED_APP_LABELS:
        return False
    return True


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
            changed[field.name] = {'old': None, 'new': serialize_value(value)}
        return changed

    # For updates, compare with stored original values
    if not hasattr(instance, '_original_values'):
        return {}

    changed = {}
    for field_name, old_value in instance._original_values.items():
        new_value = getattr(instance, field_name, None)

        # Get comparison values (use pk for related objects)
        if hasattr(new_value, 'pk'):
            new_value_compare = new_value.pk
        else:
            new_value_compare = new_value

        if hasattr(old_value, 'pk'):
            old_value_compare = old_value.pk
        else:
            old_value_compare = old_value

        # Convert datetime/decimal for comparison
        if hasattr(new_value_compare, 'isoformat'):
            new_value_compare = new_value_compare.isoformat()
        if hasattr(old_value_compare, 'isoformat'):
            old_value_compare = old_value_compare.isoformat()
        if isinstance(new_value_compare, Decimal):
            new_value_compare = float(new_value_compare)
        if isinstance(old_value_compare, Decimal):
            old_value_compare = float(old_value_compare)

        if old_value_compare != new_value_compare:
            changed[field_name] = {
                'old': serialize_value(old_value),
                'new': serialize_value(new_value)
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

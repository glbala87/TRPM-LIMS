"""
Mixins for adding audit functionality to models and views.
"""
from django.db import models
from .models import AuditLog, AuditTrail
from .middleware import get_current_request, get_current_user


class AuditableMixin(models.Model):
    """
    Mixin that adds audit fields to a model.

    Adds created_at, updated_at, created_by, and updated_by fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        editable=False
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        editable=False
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)


class FullAuditMixin(AuditableMixin):
    """
    Extended mixin that also creates automatic snapshots on save.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)

        # Create snapshot after save
        user = get_current_user()
        action = 'CREATE' if is_new else 'UPDATE'
        AuditTrail.create_snapshot(self, user, action)

    def get_audit_history(self):
        """Get the complete audit history for this object."""
        return AuditTrail.get_history(self)

    def get_audit_logs(self):
        """Get audit logs for this object."""
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self)
        return AuditLog.objects.filter(
            content_type=ct,
            object_id=self.pk
        ).order_by('-timestamp')


class AuditViewMixin:
    """
    Mixin for views to add audit logging for specific actions.
    """

    def log_action(self, action, obj=None, notes=''):
        """Log an action with the current request context."""
        return AuditLog.log_action(
            action=action,
            obj=obj,
            user=self.request.user if self.request.user.is_authenticated else None,
            request=self.request,
            notes=notes
        )

    def log_view(self, obj):
        """Log that an object was viewed."""
        return self.log_action('VIEW', obj)

    def log_export(self, notes=''):
        """Log an export action."""
        return self.log_action('EXPORT', notes=notes)

    def log_print(self, obj, notes=''):
        """Log a print action."""
        return self.log_action('PRINT', obj, notes=notes)


class AuditAPIViewMixin:
    """
    Mixin for DRF views to add audit logging.
    """

    def perform_create(self, serializer):
        """Log creation via API."""
        instance = serializer.save()
        AuditLog.log_create(
            instance,
            user=self.request.user if self.request.user.is_authenticated else None,
            request=self.request
        )

    def perform_update(self, serializer):
        """Log update via API with changed fields."""
        instance = self.get_object()
        old_values = {
            field.name: getattr(instance, field.name)
            for field in instance._meta.fields
            if field.name not in ['id', 'created_at', 'updated_at']
        }

        instance = serializer.save()

        changed_fields = {}
        for field_name, old_value in old_values.items():
            new_value = getattr(instance, field_name)
            if old_value != new_value:
                # Convert values to displayable format
                if hasattr(old_value, 'isoformat'):
                    old_value = old_value.isoformat()
                if hasattr(new_value, 'isoformat'):
                    new_value = new_value.isoformat()
                if hasattr(old_value, 'pk'):
                    old_value = str(old_value)
                if hasattr(new_value, 'pk'):
                    new_value = str(new_value)
                changed_fields[field_name] = {'old': old_value, 'new': new_value}

        if changed_fields:
            AuditLog.log_update(
                instance,
                changed_fields,
                user=self.request.user if self.request.user.is_authenticated else None,
                request=self.request
            )

    def perform_destroy(self, instance):
        """Log deletion via API."""
        AuditLog.log_delete(
            instance,
            user=self.request.user if self.request.user.is_authenticated else None,
            request=self.request
        )
        instance.delete()

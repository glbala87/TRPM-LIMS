# tenants/models.py
"""
Multi-tenant architecture models for TRPM-LIMS.
Inspired by beak-lims multi-tenant design with organization and laboratory scoping.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Organization(models.Model):
    """
    Top-level organization entity (e.g., hospital network, research institution).
    Organizations contain multiple laboratories.
    """

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Short code for the organization")
    description = models.TextField(blank=True)

    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Subscription and limits
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('BASIC', 'Basic'),
            ('PROFESSIONAL', 'Professional'),
            ('ENTERPRISE', 'Enterprise'),
        ],
        default='FREE'
    )
    max_laboratories = models.PositiveIntegerField(default=1)
    max_users = models.PositiveIntegerField(default=10)
    max_samples_per_month = models.PositiveIntegerField(default=1000)

    # Settings stored as JSON
    settings = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def laboratory_count(self):
        return self.laboratories.filter(is_active=True).count()

    @property
    def user_count(self):
        return self.memberships.filter(is_active=True).count()


class Laboratory(models.Model):
    """
    Laboratory entity within an organization.
    All data is scoped to a laboratory for multi-tenant isolation.
    """

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='laboratories'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, help_text="Short code for the laboratory")
    description = models.TextField(blank=True)

    # Laboratory type
    lab_type = models.CharField(
        max_length=50,
        choices=[
            ('CLINICAL', 'Clinical Laboratory'),
            ('RESEARCH', 'Research Laboratory'),
            ('MOLECULAR', 'Molecular Diagnostics'),
            ('PATHOLOGY', 'Pathology'),
            ('MICROBIOLOGY', 'Microbiology'),
            ('BIOBANK', 'Biobank'),
            ('GENOMICS', 'Genomics'),
            ('OTHER', 'Other'),
        ],
        default='CLINICAL'
    )

    # Accreditation
    accreditation_number = models.CharField(max_length=100, blank=True)
    accreditation_body = models.CharField(max_length=255, blank=True)
    accreditation_expiry = models.DateField(null=True, blank=True)

    # Contact information
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Settings and configuration
    settings = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # Feature flags
    features_enabled = models.JSONField(
        default=dict,
        blank=True,
        help_text="Feature flags for this laboratory"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Laboratory"
        verbose_name_plural = "Laboratories"
        ordering = ['organization', 'name']
        unique_together = [['organization', 'code']]

    def __str__(self):
        return f"{self.organization.code}/{self.code} - {self.name}"

    def has_feature(self, feature_name):
        """Check if a feature is enabled for this laboratory."""
        return self.features_enabled.get(feature_name, False)


class OrganizationMembership(models.Model):
    """
    User membership in an organization with role assignment.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=50,
        choices=[
            ('OWNER', 'Owner'),
            ('ADMIN', 'Administrator'),
            ('MANAGER', 'Manager'),
            ('MEMBER', 'Member'),
            ('VIEWER', 'Viewer'),
        ],
        default='MEMBER'
    )

    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organization Membership"
        verbose_name_plural = "Organization Memberships"
        unique_together = [['user', 'organization']]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"


class LaboratoryMembership(models.Model):
    """
    User membership in a laboratory with specific permissions.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='laboratory_memberships'
    )
    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=50,
        choices=[
            ('LAB_DIRECTOR', 'Laboratory Director'),
            ('LAB_MANAGER', 'Laboratory Manager'),
            ('SUPERVISOR', 'Supervisor'),
            ('SENIOR_TECHNICIAN', 'Senior Technician'),
            ('TECHNICIAN', 'Technician'),
            ('TRAINEE', 'Trainee'),
            ('VIEWER', 'Viewer'),
        ],
        default='TECHNICIAN'
    )

    # Department within the laboratory
    department = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Default laboratory for this user"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Laboratory Membership"
        verbose_name_plural = "Laboratory Memberships"
        unique_together = [['user', 'laboratory']]

    def __str__(self):
        return f"{self.user} - {self.laboratory} ({self.role})"

    def save(self, *args, **kwargs):
        # Ensure only one default laboratory per user
        if self.is_default:
            LaboratoryMembership.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class TenantAwareModel(models.Model):
    """
    Abstract base model for tenant-scoped entities.
    All models inheriting from this will be automatically filtered by laboratory.
    """

    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True


class TenantContext:
    """
    Thread-local storage for tenant context.
    Used by middleware and managers to scope queries.
    """

    _context = {}

    @classmethod
    def set_context(cls, user=None, organization=None, laboratory=None, request=None):
        """Set the current tenant context."""
        import threading
        thread_id = threading.current_thread().ident
        cls._context[thread_id] = {
            'user': user,
            'organization': organization,
            'laboratory': laboratory,
            'request': request,
            'timestamp': timezone.now(),
        }

    @classmethod
    def get_context(cls):
        """Get the current tenant context."""
        import threading
        thread_id = threading.current_thread().ident
        return cls._context.get(thread_id, {})

    @classmethod
    def get_laboratory(cls):
        """Get the current laboratory from context."""
        return cls.get_context().get('laboratory')

    @classmethod
    def get_organization(cls):
        """Get the current organization from context."""
        return cls.get_context().get('organization')

    @classmethod
    def get_user(cls):
        """Get the current user from context."""
        return cls.get_context().get('user')

    @classmethod
    def clear_context(cls):
        """Clear the current tenant context."""
        import threading
        thread_id = threading.current_thread().ident
        cls._context.pop(thread_id, None)


class TenantAwareManager(models.Manager):
    """
    Custom manager that automatically filters queries by tenant.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        laboratory = TenantContext.get_laboratory()
        if laboratory:
            queryset = queryset.filter(laboratory=laboratory)
        return queryset

    def unscoped(self):
        """Return unscoped queryset (bypass tenant filtering)."""
        return super().get_queryset()

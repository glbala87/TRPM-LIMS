"""
User management models for TRPM-LIMS.

Provides Role-Based Access Control (RBAC) with multi-tier permissions:
- Admin: Full system access
- Lab Manager: Manage lab operations, approve results
- Supervisor: Oversee technicians, review results
- Technician: Perform tests, enter results
- Reader: View-only access
- Physician: View patient results, request tests
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class Role(models.Model):
    """
    Role definitions for the LIMS system.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('LAB_MANAGER', 'Lab Manager'),
        ('SUPERVISOR', 'Supervisor'),
        ('TECHNICIAN', 'Technician'),
        ('READER', 'Reader'),
        ('PHYSICIAN', 'Physician'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Role identifier"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Human-readable role name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of role responsibilities"
    )

    # Permission flags
    can_view_patients = models.BooleanField(default=True)
    can_edit_patients = models.BooleanField(default=False)
    can_create_patients = models.BooleanField(default=False)

    can_view_samples = models.BooleanField(default=True)
    can_edit_samples = models.BooleanField(default=False)
    can_create_samples = models.BooleanField(default=False)
    can_delete_samples = models.BooleanField(default=False)

    can_view_results = models.BooleanField(default=True)
    can_enter_results = models.BooleanField(default=False)
    can_review_results = models.BooleanField(default=False)
    can_approve_results = models.BooleanField(default=False)
    can_release_reports = models.BooleanField(default=False)

    can_manage_equipment = models.BooleanField(default=False)
    can_manage_reagents = models.BooleanField(default=False)
    can_manage_storage = models.BooleanField(default=False)

    can_view_analytics = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_import_data = models.BooleanField(default=False)

    can_manage_users = models.BooleanField(default=False)
    can_view_audit_logs = models.BooleanField(default=False)
    can_configure_system = models.BooleanField(default=False)

    # Related Django permissions (optional, for integration)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='lims_roles',
        help_text="Django permissions associated with this role"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name

    @classmethod
    def get_default_permissions(cls, role_name):
        """Get default permissions for a role type."""
        defaults = {
            'ADMIN': {
                'can_view_patients': True, 'can_edit_patients': True, 'can_create_patients': True,
                'can_view_samples': True, 'can_edit_samples': True, 'can_create_samples': True, 'can_delete_samples': True,
                'can_view_results': True, 'can_enter_results': True, 'can_review_results': True,
                'can_approve_results': True, 'can_release_reports': True,
                'can_manage_equipment': True, 'can_manage_reagents': True, 'can_manage_storage': True,
                'can_view_analytics': True, 'can_export_data': True, 'can_import_data': True,
                'can_manage_users': True, 'can_view_audit_logs': True, 'can_configure_system': True,
            },
            'LAB_MANAGER': {
                'can_view_patients': True, 'can_edit_patients': True, 'can_create_patients': True,
                'can_view_samples': True, 'can_edit_samples': True, 'can_create_samples': True, 'can_delete_samples': True,
                'can_view_results': True, 'can_enter_results': True, 'can_review_results': True,
                'can_approve_results': True, 'can_release_reports': True,
                'can_manage_equipment': True, 'can_manage_reagents': True, 'can_manage_storage': True,
                'can_view_analytics': True, 'can_export_data': True, 'can_import_data': True,
                'can_manage_users': False, 'can_view_audit_logs': True, 'can_configure_system': False,
            },
            'SUPERVISOR': {
                'can_view_patients': True, 'can_edit_patients': True, 'can_create_patients': True,
                'can_view_samples': True, 'can_edit_samples': True, 'can_create_samples': True, 'can_delete_samples': False,
                'can_view_results': True, 'can_enter_results': True, 'can_review_results': True,
                'can_approve_results': False, 'can_release_reports': False,
                'can_manage_equipment': True, 'can_manage_reagents': True, 'can_manage_storage': True,
                'can_view_analytics': True, 'can_export_data': True, 'can_import_data': False,
                'can_manage_users': False, 'can_view_audit_logs': True, 'can_configure_system': False,
            },
            'TECHNICIAN': {
                'can_view_patients': True, 'can_edit_patients': False, 'can_create_patients': False,
                'can_view_samples': True, 'can_edit_samples': True, 'can_create_samples': True, 'can_delete_samples': False,
                'can_view_results': True, 'can_enter_results': True, 'can_review_results': False,
                'can_approve_results': False, 'can_release_reports': False,
                'can_manage_equipment': False, 'can_manage_reagents': True, 'can_manage_storage': True,
                'can_view_analytics': False, 'can_export_data': False, 'can_import_data': False,
                'can_manage_users': False, 'can_view_audit_logs': False, 'can_configure_system': False,
            },
            'READER': {
                'can_view_patients': True, 'can_edit_patients': False, 'can_create_patients': False,
                'can_view_samples': True, 'can_edit_samples': False, 'can_create_samples': False, 'can_delete_samples': False,
                'can_view_results': True, 'can_enter_results': False, 'can_review_results': False,
                'can_approve_results': False, 'can_release_reports': False,
                'can_manage_equipment': False, 'can_manage_reagents': False, 'can_manage_storage': False,
                'can_view_analytics': True, 'can_export_data': False, 'can_import_data': False,
                'can_manage_users': False, 'can_view_audit_logs': False, 'can_configure_system': False,
            },
            'PHYSICIAN': {
                'can_view_patients': True, 'can_edit_patients': False, 'can_create_patients': False,
                'can_view_samples': True, 'can_edit_samples': False, 'can_create_samples': False, 'can_delete_samples': False,
                'can_view_results': True, 'can_enter_results': False, 'can_review_results': False,
                'can_approve_results': False, 'can_release_reports': False,
                'can_manage_equipment': False, 'can_manage_reagents': False, 'can_manage_storage': False,
                'can_view_analytics': False, 'can_export_data': False, 'can_import_data': False,
                'can_manage_users': False, 'can_view_audit_logs': False, 'can_configure_system': False,
            },
        }
        return defaults.get(role_name, {})


class UserProfile(models.Model):
    """
    Extended user profile for LIMS-specific attributes.
    Links to Django's built-in User model via OneToOneField.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True
    )

    # Professional information
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Employee ID or badge number"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or section"
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Work phone number"
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        help_text="Phone extension"
    )

    # Qualifications
    qualifications = models.TextField(
        blank=True,
        help_text="Professional qualifications and certifications"
    )
    signature_image = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        help_text="Digital signature for reports"
    )

    # Quick permission flags (can override role permissions)
    can_approve_results = models.BooleanField(
        default=False,
        help_text="Override: Allow user to approve test results"
    )
    can_release_reports = models.BooleanField(
        default=False,
        help_text="Override: Allow user to release reports"
    )

    # Account settings
    is_active_lims = models.BooleanField(
        default=True,
        help_text="Whether user can access LIMS features"
    )
    login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Failed login attempt count"
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Account locked due to failed attempts"
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last password change date"
    )
    require_password_change = models.BooleanField(
        default=False,
        help_text="Force password change on next login"
    )

    # Session tracking
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last activity timestamp"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role or 'No Role'})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def has_permission(self, permission_name):
        """Check if user has a specific permission via their role."""
        if self.user.is_superuser:
            return True
        if not self.role:
            return False
        return getattr(self.role, permission_name, False)

    def can_perform_action(self, action):
        """
        Check if user can perform a specific action.
        Maps action names to permission fields.
        """
        action_map = {
            'view_patients': 'can_view_patients',
            'edit_patients': 'can_edit_patients',
            'create_patients': 'can_create_patients',
            'view_samples': 'can_view_samples',
            'edit_samples': 'can_edit_samples',
            'create_samples': 'can_create_samples',
            'delete_samples': 'can_delete_samples',
            'view_results': 'can_view_results',
            'enter_results': 'can_enter_results',
            'review_results': 'can_review_results',
            'approve_results': 'can_approve_results',
            'release_reports': 'can_release_reports',
            'manage_equipment': 'can_manage_equipment',
            'manage_reagents': 'can_manage_reagents',
            'manage_storage': 'can_manage_storage',
            'view_analytics': 'can_view_analytics',
            'export_data': 'can_export_data',
            'import_data': 'can_import_data',
            'manage_users': 'can_manage_users',
            'view_audit_logs': 'can_view_audit_logs',
            'configure_system': 'can_configure_system',
        }

        permission_field = action_map.get(action)
        if not permission_field:
            return False

        # Check override flags first
        if permission_field == 'can_approve_results' and self.can_approve_results:
            return True
        if permission_field == 'can_release_reports' and self.can_release_reports:
            return True

        return self.has_permission(permission_field)

    def reset_login_attempts(self):
        """Reset login attempt counter."""
        self.login_attempts = 0
        self.is_locked = False
        self.save(update_fields=['login_attempts', 'is_locked'])

    def record_failed_login(self, max_attempts=5):
        """Record a failed login attempt."""
        self.login_attempts += 1
        if self.login_attempts >= max_attempts:
            self.is_locked = True
        self.save(update_fields=['login_attempts', 'is_locked'])

    def update_activity(self):
        """Update last activity timestamp."""
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class UserSession(models.Model):
    """
    Track user sessions for security and audit purposes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lims_sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

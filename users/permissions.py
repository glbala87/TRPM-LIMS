"""
Permission classes for LIMS access control.
These can be used with Django REST Framework or in views directly.
"""
from rest_framework import permissions


class HasLIMSPermission(permissions.BasePermission):
    """
    Base permission class that checks LIMS-specific permissions.
    Subclass and override `required_permission` to create specific permission checks.
    """
    required_permission = None
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'userprofile'):
            return False

        if self.required_permission:
            return request.user.userprofile.can_perform_action(self.required_permission)

        return True


# Patient permissions
class CanViewPatients(HasLIMSPermission):
    required_permission = 'view_patients'
    message = "You do not have permission to view patients."


class CanEditPatients(HasLIMSPermission):
    required_permission = 'edit_patients'
    message = "You do not have permission to edit patients."


class CanCreatePatients(HasLIMSPermission):
    required_permission = 'create_patients'
    message = "You do not have permission to create patients."


# Sample permissions
class CanViewSamples(HasLIMSPermission):
    required_permission = 'view_samples'
    message = "You do not have permission to view samples."


class CanEditSamples(HasLIMSPermission):
    required_permission = 'edit_samples'
    message = "You do not have permission to edit samples."


class CanCreateSamples(HasLIMSPermission):
    required_permission = 'create_samples'
    message = "You do not have permission to create samples."


class CanDeleteSamples(HasLIMSPermission):
    required_permission = 'delete_samples'
    message = "You do not have permission to delete samples."


# Result permissions
class CanViewResults(HasLIMSPermission):
    required_permission = 'view_results'
    message = "You do not have permission to view results."


class CanEnterResults(HasLIMSPermission):
    required_permission = 'enter_results'
    message = "You do not have permission to enter results."


class CanReviewResults(HasLIMSPermission):
    required_permission = 'review_results'
    message = "You do not have permission to review results."


class CanApproveResults(HasLIMSPermission):
    required_permission = 'approve_results'
    message = "You do not have permission to approve results."


class CanReleaseReports(HasLIMSPermission):
    required_permission = 'release_reports'
    message = "You do not have permission to release reports."


# Management permissions
class CanManageEquipment(HasLIMSPermission):
    required_permission = 'manage_equipment'
    message = "You do not have permission to manage equipment."


class CanManageReagents(HasLIMSPermission):
    required_permission = 'manage_reagents'
    message = "You do not have permission to manage reagents."


class CanManageStorage(HasLIMSPermission):
    required_permission = 'manage_storage'
    message = "You do not have permission to manage storage."


# Analytics and data permissions
class CanViewAnalytics(HasLIMSPermission):
    required_permission = 'view_analytics'
    message = "You do not have permission to view analytics."


class CanExportData(HasLIMSPermission):
    required_permission = 'export_data'
    message = "You do not have permission to export data."


class CanImportData(HasLIMSPermission):
    required_permission = 'import_data'
    message = "You do not have permission to import data."


# Admin permissions
class CanManageUsers(HasLIMSPermission):
    required_permission = 'manage_users'
    message = "You do not have permission to manage users."


class CanViewAuditLogs(HasLIMSPermission):
    required_permission = 'view_audit_logs'
    message = "You do not have permission to view audit logs."


class CanConfigureSystem(HasLIMSPermission):
    required_permission = 'configure_system'
    message = "You do not have permission to configure system settings."


# Role-based permissions
class IsAdmin(permissions.BasePermission):
    """Check if user has Admin role."""
    message = "Admin access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
            return request.user.userprofile.role.name == 'ADMIN'
        return False


class IsLabManager(permissions.BasePermission):
    """Check if user has Lab Manager or Admin role."""
    message = "Lab Manager access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
            return request.user.userprofile.role.name in ['ADMIN', 'LAB_MANAGER']
        return False


class IsSupervisor(permissions.BasePermission):
    """Check if user has Supervisor, Lab Manager, or Admin role."""
    message = "Supervisor access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
            return request.user.userprofile.role.name in ['ADMIN', 'LAB_MANAGER', 'SUPERVISOR']
        return False


class IsTechnician(permissions.BasePermission):
    """Check if user has Technician or higher role."""
    message = "Technician access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
            return request.user.userprofile.role.name in [
                'ADMIN', 'LAB_MANAGER', 'SUPERVISOR', 'TECHNICIAN'
            ]
        return False


class IsActiveUser(permissions.BasePermission):
    """Check if user has active LIMS access."""
    message = "Your account is not active for LIMS access."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.is_active_lims and not request.user.userprofile.is_locked
        return True  # Allow if no profile (backwards compatibility)


# Combined permissions for common use cases
class CanEditOrDeleteSamples(permissions.BasePermission):
    """Combined permission for editing or deleting samples."""
    message = "You do not have permission to modify samples."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            if request.method == 'DELETE':
                return profile.can_perform_action('delete_samples')
            return profile.can_perform_action('edit_samples')
        return False


def check_permission(user, permission_name):
    """
    Utility function to check if a user has a specific permission.
    Can be used in views or templates.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if hasattr(user, 'userprofile'):
        return user.userprofile.can_perform_action(permission_name)
    return False

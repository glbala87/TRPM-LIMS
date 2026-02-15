"""
Custom permissions for the TRPM-LIMS REST API.
"""
from rest_framework import permissions


class IsLabStaff(permissions.BasePermission):
    """
    Allows access only to authenticated lab staff members.
    """
    message = "You must be a lab staff member to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsLabManager(permissions.BasePermission):
    """
    Allows access only to lab managers and administrators.
    """
    message = "You must be a lab manager to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Check for superuser or lab manager role
        if request.user.is_superuser:
            return True
        # Check for UserProfile role (when users app is implemented)
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.role in ['ADMIN', 'LAB_MANAGER']
        return False


class CanApproveResults(permissions.BasePermission):
    """
    Permission to approve test results.
    """
    message = "You do not have permission to approve results."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.can_approve_results
        return False


class CanReleaseReports(permissions.BasePermission):
    """
    Permission to release reports to patients/physicians.
    """
    message = "You do not have permission to release reports."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.can_release_reports
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `created_by` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return True


class ReadOnlyPermission(permissions.BasePermission):
    """
    Read-only access for all authenticated users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in permissions.SAFE_METHODS


class IsSupervisorOrAbove(permissions.BasePermission):
    """
    Allows access to supervisors, lab managers, and administrators.
    """
    message = "You must be a supervisor or above to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.role in ['ADMIN', 'LAB_MANAGER', 'SUPERVISOR']
        return False

"""
Decorators for permission checking in views.
"""
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def lims_permission_required(permission_name, login_url=None, raise_exception=False):
    """
    Decorator to check LIMS permissions on views.

    Usage:
        @lims_permission_required('approve_results')
        def approve_result_view(request, result_id):
            ...

    Args:
        permission_name: The permission to check (e.g., 'approve_results')
        login_url: URL to redirect to if not authenticated
        raise_exception: If True, raise PermissionDenied instead of redirecting
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            # Superusers always have permission
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check LIMS permission
            if hasattr(request.user, 'userprofile'):
                if request.user.userprofile.can_perform_action(permission_name):
                    return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied(f"Permission required: {permission_name}")

            messages.error(request, f"You do not have permission to perform this action.")
            return HttpResponseForbidden("Permission denied")

        return _wrapped_view
    return decorator


def role_required(role_names, login_url=None, raise_exception=False):
    """
    Decorator to check if user has one of the specified roles.

    Usage:
        @role_required(['ADMIN', 'LAB_MANAGER'])
        def admin_view(request):
            ...

    Args:
        role_names: List of role names (e.g., ['ADMIN', 'LAB_MANAGER'])
        login_url: URL to redirect to if not authenticated
        raise_exception: If True, raise PermissionDenied instead of redirecting
    """
    if isinstance(role_names, str):
        role_names = [role_names]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check role
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
                if request.user.userprofile.role.name in role_names:
                    return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied(f"Role required: {', '.join(role_names)}")

            messages.error(request, f"This action requires one of these roles: {', '.join(role_names)}")
            return HttpResponseForbidden("Permission denied")

        return _wrapped_view
    return decorator


def active_lims_user_required(view_func):
    """
    Decorator to ensure user has active LIMS access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            if profile.is_locked:
                messages.error(request, "Your account is locked. Please contact an administrator.")
                return HttpResponseForbidden("Account locked")
            if not profile.is_active_lims:
                messages.error(request, "Your LIMS access is disabled. Please contact an administrator.")
                return HttpResponseForbidden("LIMS access disabled")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def can_approve_results(view_func):
    """Shortcut decorator for result approval permission."""
    return lims_permission_required('approve_results', raise_exception=True)(view_func)


def can_release_reports(view_func):
    """Shortcut decorator for report release permission."""
    return lims_permission_required('release_reports', raise_exception=True)(view_func)


def can_manage_users(view_func):
    """Shortcut decorator for user management permission."""
    return lims_permission_required('manage_users', raise_exception=True)(view_func)


def can_view_audit_logs(view_func):
    """Shortcut decorator for audit log viewing permission."""
    return lims_permission_required('view_audit_logs', raise_exception=True)(view_func)


def lab_manager_required(view_func):
    """Shortcut decorator requiring Lab Manager or Admin role."""
    return role_required(['ADMIN', 'LAB_MANAGER'], raise_exception=True)(view_func)


def supervisor_required(view_func):
    """Shortcut decorator requiring Supervisor or higher role."""
    return role_required(['ADMIN', 'LAB_MANAGER', 'SUPERVISOR'], raise_exception=True)(view_func)


def technician_required(view_func):
    """Shortcut decorator requiring Technician or higher role."""
    return role_required(['ADMIN', 'LAB_MANAGER', 'SUPERVISOR', 'TECHNICIAN'], raise_exception=True)(view_func)

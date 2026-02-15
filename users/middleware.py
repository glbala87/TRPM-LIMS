"""
Middleware for user session management and activity tracking.
"""
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from datetime import timedelta


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity and update last_activity timestamp.
    """

    def process_request(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile'):
                # Update activity timestamp (but not on every request to reduce DB load)
                profile = request.user.userprofile
                now = timezone.now()

                # Only update if last activity was more than 5 minutes ago
                if not profile.last_activity or (now - profile.last_activity) > timedelta(minutes=5):
                    profile.last_activity = now
                    profile.save(update_fields=['last_activity'])


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware for session security:
    - Track session information
    - Enforce session timeouts
    - Prevent concurrent sessions (optional)
    """

    # Session timeout in minutes (configurable via settings)
    SESSION_TIMEOUT = 60  # 1 hour

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        # Check if user profile is locked
        if hasattr(request.user, 'userprofile') and request.user.userprofile.is_locked:
            logout(request)
            return redirect(reverse('admin:login'))

        # Session timeout check
        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            if profile.last_activity:
                time_since_activity = timezone.now() - profile.last_activity
                if time_since_activity > timedelta(minutes=self.SESSION_TIMEOUT):
                    logout(request)
                    return redirect(reverse('admin:login'))


class PasswordChangeMiddleware(MiddlewareMixin):
    """
    Middleware to enforce password change requirements.
    Redirects users who need to change their password.
    """

    EXEMPT_URLS = [
        '/admin/password_change/',
        '/admin/logout/',
        '/api/',  # Don't enforce on API endpoints
    ]

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.require_password_change:
                # Check if current URL is exempt
                for url in self.EXEMPT_URLS:
                    if request.path.startswith(url):
                        return
                return redirect(reverse('admin:password_change'))


class UserSessionTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track user sessions for security auditing.
    """

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        if not request.session.session_key:
            return

        from .models import UserSession

        session_key = request.session.session_key
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Update or create session record
        UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_address': ip_address,
                'user_agent': user_agent[:500] if user_agent else '',  # Truncate if too long
                'is_active': True,
            }
        )

    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

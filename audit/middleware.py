"""
Middleware for capturing request context for audit logging.
"""
import threading
from django.utils.deprecation import MiddlewareMixin

# Thread-local storage for request context
_request_local = threading.local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_request_local, 'request', None)


def get_current_user():
    """Get the current user from thread-local storage."""
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to capture request context for audit logging.

    This middleware stores the current request in thread-local storage
    so that it can be accessed by signal handlers and other code that
    needs request context but doesn't have direct access to the request.
    """

    def process_request(self, request):
        """Store request in thread-local storage."""
        _request_local.request = request

    def process_response(self, request, response):
        """Clear request from thread-local storage."""
        if hasattr(_request_local, 'request'):
            del _request_local.request
        return response

    def process_exception(self, request, exception):
        """Clear request from thread-local storage on exception."""
        if hasattr(_request_local, 'request'):
            del _request_local.request


class RequestContextMiddleware(MiddlewareMixin):
    """
    Extended middleware that also captures IP address and user agent.
    """

    def process_request(self, request):
        """Store request context in thread-local storage."""
        _request_local.request = request
        _request_local.ip_address = self._get_client_ip(request)
        _request_local.user_agent = request.META.get('HTTP_USER_AGENT', '')

    def process_response(self, request, response):
        """Clear context from thread-local storage."""
        for attr in ['request', 'ip_address', 'user_agent']:
            if hasattr(_request_local, attr):
                delattr(_request_local, attr)
        return response

    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


def get_client_ip():
    """Get the current client IP from thread-local storage."""
    return getattr(_request_local, 'ip_address', None)


def get_user_agent():
    """Get the current user agent from thread-local storage."""
    return getattr(_request_local, 'user_agent', '')

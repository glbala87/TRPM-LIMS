# tenants/middleware.py
"""
Middleware for multi-tenant context management.
"""

from django.utils.deprecation import MiddlewareMixin
from .models import TenantContext, LaboratoryMembership


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that sets the tenant context for each request.
    Extracts laboratory from:
    1. Request header (X-Laboratory-UID)
    2. Session (active_laboratory_uid)
    3. User's default laboratory
    """

    def process_request(self, request):
        """Set tenant context at the start of each request."""
        user = request.user if request.user.is_authenticated else None
        organization = None
        laboratory = None

        if user:
            # Try to get laboratory from header
            lab_uid = request.headers.get('X-Laboratory-UID')

            # Try to get from session
            if not lab_uid:
                lab_uid = request.session.get('active_laboratory_uid')

            if lab_uid:
                # Verify user has access to this laboratory
                try:
                    membership = LaboratoryMembership.objects.select_related(
                        'laboratory', 'laboratory__organization'
                    ).get(
                        user=user,
                        laboratory__uid=lab_uid,
                        is_active=True
                    )
                    laboratory = membership.laboratory
                    organization = laboratory.organization
                except LaboratoryMembership.DoesNotExist:
                    pass

            # Fall back to default laboratory
            if not laboratory:
                default_membership = LaboratoryMembership.objects.select_related(
                    'laboratory', 'laboratory__organization'
                ).filter(
                    user=user,
                    is_default=True,
                    is_active=True
                ).first()

                if default_membership:
                    laboratory = default_membership.laboratory
                    organization = laboratory.organization
                else:
                    # Use first available laboratory
                    first_membership = LaboratoryMembership.objects.select_related(
                        'laboratory', 'laboratory__organization'
                    ).filter(
                        user=user,
                        is_active=True
                    ).first()

                    if first_membership:
                        laboratory = first_membership.laboratory
                        organization = laboratory.organization

        # Set context
        TenantContext.set_context(
            user=user,
            organization=organization,
            laboratory=laboratory,
            request=request
        )

        # Store on request for easy access
        request.tenant_context = {
            'user': user,
            'organization': organization,
            'laboratory': laboratory,
        }

    def process_response(self, request, response):
        """Clear tenant context after response."""
        TenantContext.clear_context()
        return response

    def process_exception(self, request, exception):
        """Clear tenant context on exception."""
        TenantContext.clear_context()
        return None

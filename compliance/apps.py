"""
Compliance app configuration for TRPM-LIMS.

Handles IRB approvals, consent protocols, and regulatory compliance tracking.
"""
from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    """Configuration for the Compliance application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compliance'
    verbose_name = 'Compliance & Consent Management'

    def ready(self):
        """Import signals when the app is ready."""
        try:
            import compliance.signals  # noqa
        except ImportError:
            pass

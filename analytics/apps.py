# analytics/apps.py

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Configuration for the Analytics application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Analytics & Dashboards'

    def ready(self):
        """Perform initialization when the app is ready."""
        # Import signal handlers if needed in the future
        pass

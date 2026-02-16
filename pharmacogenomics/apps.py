# pharmacogenomics/apps.py

from django.apps import AppConfig


class PharmacogenomicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pharmacogenomics'
    verbose_name = 'Pharmacogenomics (PGx)'

    def ready(self):
        # Import signals if needed
        pass

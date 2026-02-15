from django.apps import AppConfig


class SingleCellConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'single_cell'
    verbose_name = 'Single-Cell Genomics'

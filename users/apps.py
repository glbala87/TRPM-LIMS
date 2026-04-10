from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'

    def ready(self):
        # Wire up password lifecycle signals (history capture + profile stamp).
        from . import password_hooks  # noqa: F401

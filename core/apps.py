from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # instantiate cache object
        from core.cache import cache  # noqa: F401

        # connect signals
        from core import signals  # noqa: F401

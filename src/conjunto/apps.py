from django.apps import AppConfig


class ConjuntoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conjunto"

    def ready(self):
        from . import components  # noqa

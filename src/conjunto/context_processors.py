from django.conf import settings as django_settings
from conjunto.menu import Menu

__all__ = ["globals", "settings"]


def globals(request):
    return {
        "globals": {
            "project_title": django_settings.PROJECT_TITLE,
            # "version": __version__,
        },
        "menus": Menu(request),
    }


def settings(request):
    return {
        "settings": request.settings,
        "PRODUCTION": getattr(django_settings, "PRODUCTION", False),
    }

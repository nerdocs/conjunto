from django.conf import settings as django_settings
from conjunto.menu import Menu
from importlib import metadata


__all__ = ["globals", "settings"]

# try to get version using the importlib.metadata module
# you have to set PROJECT_NAME in settings.py for that.
# But this is obligatory anyway, and helps to avoid searching for version strings
# elsewhere.
__version__ = metadata.version(django_settings.PROJECT_NAME)


# FIXME: don't shadow builtin "globals". But change breaks API.
def globals(request):
    return {
        "globals": {
            "project_title": django_settings.PROJECT_TITLE,
            "version": __version__,
        },
        "menus": Menu(request),
    }


def settings(request):
    return {
        "app_settings": request.app_settings,
        "PRODUCTION": getattr(django_settings, "PRODUCTION", False),
        "tabler": getattr(django_settings, "TABLER", {}),
    }

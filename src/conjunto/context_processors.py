from django.conf import settings as django_settings
from conjunto.menu import Menu


def globals(request):
    return {
        "globals": {
            "project_title": django_settings.PROJECT_TITLE,
            # "version": __version__,
        },
        "menus": Menu(request),
        "settings": request.settings,
    }

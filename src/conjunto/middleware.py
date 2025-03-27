from django.apps import apps
from django.http import HttpResponse
from django.shortcuts import reverse, redirect
from django.conf import settings


class MaintenanceMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:
        path = request.META.get("PATH_INFO", "")

        settings_model_name = settings.SETTINGS_MODEL
        request.settings = apps.get_model(settings_model_name).get_instance()

        # if user is logged in and is not staff, redirect to maintenance page
        # check also if requested URL is not one of the following:
        # - login page
        # - maintenance page
        # - media files
        if not request.user.is_staff:
            if (
                request.settings.maintenance_mode
                and (path not in [reverse("login"), reverse("maintenance")])
                and not path.startswith(settings.MEDIA_URL)
            ):
                return redirect(reverse("maintenance") + f"?next={request.path}")
                # FIXME kwargs

        response = self.get_response(request)

        return response


class SettingsMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:
        # Load the model specified in settings.SETTINGS_MODEL asynchronously
        AppSettings = apps.get_model(settings.SETTINGS_MODEL)
        request.settings = AppSettings.objects.all()
        return self.get_response(request)

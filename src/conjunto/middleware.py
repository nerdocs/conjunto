from django.apps import apps
from django.shortcuts import reverse, redirect
from django.conf import settings


class ConjuntoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get("PATH_INFO", "")

        settings_model_name = settings.SETTINGS_MODEL
        request.settings = apps.get_model(settings_model_name).get_instance()
        if not request.user.is_staff:
            maintenance_mode = request.settings.maintenance_mode
            if maintenance_mode and (
                path not in [reverse("login"), reverse("maintenance")]
            ):
                return redirect(reverse("maintenance"))

        response = self.get_response(request)

        return response

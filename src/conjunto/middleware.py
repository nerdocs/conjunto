from django.apps import apps
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.shortcuts import reverse, redirect
from django.conf import settings


class ConjuntoMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:

        # ------ AppSettings ------
        # Load the model specified in settings.SETTINGS_MODEL asynchronously
        AppSettings = apps.get_model(settings.SETTINGS_MODEL)
        try:
            current_site = Site.objects.get_current(request)
        except Site.DoesNotExist:
            current_site = None

        # load settings for current site or use empty default settings if none found

        # first, try to get a site specific setting for current site
        app_settings = AppSettings.objects.filter(site=current_site).first()
        if not app_settings:
            # if not, try to get a global setting
            app_settings = (
                AppSettings.objects.filter(site__isnull=True).first() or AppSettings()
            )
        request.app_settings = app_settings

        # ------ Maintenance mode ------
        # if user is logged in and is not staff, redirect to maintenance page
        # check also if requested URL is not one of the following:
        # - login page
        # - maintenance page
        # - media files
        path = request.path
        if not request.user.is_staff:
            if (
                request.app_settings.maintenance_mode
                and (path not in [reverse("login"), reverse("maintenance")])
                and not path.startswith(settings.MEDIA_URL)
            ):

                return redirect(reverse("maintenance"))
                # FIXME kwargs

        return self.get_response(request)

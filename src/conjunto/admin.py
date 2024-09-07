from django.conf import settings
from django.contrib import admin
from django.apps import apps

from .models import Vendor


class SettingsAdmin(admin.ModelAdmin):
    pass


if hasattr(settings, "SETTINGS_MODEL"):
    settings_model = apps.get_model(settings.SETTINGS_MODEL)
    admin.site.register(settings_model, SettingsAdmin)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not Vendor.objects.exists()

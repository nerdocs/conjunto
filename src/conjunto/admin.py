from django.conf import settings
from django.contrib import admin
from django.apps import apps

from .models import (
    StaticPage,
    StaticVersionedPage,
    LicensePage,
    PrivacyPage,
)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    pass


@admin.register(StaticVersionedPage)
class StaticVersionedPageAdmin(admin.ModelAdmin):
    pass


@admin.register(LicensePage)
class LicensePageAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivacyPage)
class PrivacyPageAdmin(admin.ModelAdmin):
    pass


class SettingsAdmin(admin.ModelAdmin):
    pass


settings_model = apps.get_model(settings.SETTINGS_MODEL)
admin.site.register(settings_model, SettingsAdmin)

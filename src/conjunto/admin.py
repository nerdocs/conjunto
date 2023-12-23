from django.conf import settings
from django.contrib import admin
from django.apps import apps


class SettingsAdmin(admin.ModelAdmin):
    pass


settings_model = apps.get_model(settings.SETTINGS_MODEL)
admin.site.register(settings_model, SettingsAdmin)

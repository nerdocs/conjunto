from django.contrib import admin

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

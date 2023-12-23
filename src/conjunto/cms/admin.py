from django.contrib import admin

from conjunto.cms.models import (
    StaticPage,
    StaticVersionedPage,
    LicensePage,
    PrivacyPage,
)


# Register your models here.
@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    pass


# @admin.register(StaticVersionedPage)
# class StaticVersionedPageAdmin(admin.ModelAdmin):
#     pass


@admin.register(LicensePage)
class LicensePageAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivacyPage)
class PrivacyPageAdmin(admin.ModelAdmin):
    pass

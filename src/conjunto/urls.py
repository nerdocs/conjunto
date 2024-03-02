from django.urls import path, include, re_path
from .views import MaintenanceView, SettingsView, LightboxView
from .api.interfaces import IHtmxElementMixin


urlpatterns = [
    path("maintenance/", MaintenanceView.as_view(), name="maintenance"),
    path(
        "__elements__/",
        include(
            (IHtmxElementMixin.get_url_patterns(), "elements"),
            namespace="elements",
        ),
    ),
    path("settings/", SettingsView.as_view(), name="settings"),
    re_path(r"lightbox/(?P<path>.+)/$", LightboxView.as_view(), name="lightbox"),
]

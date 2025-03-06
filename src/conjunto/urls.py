from django.urls import path, include
from .views import MaintenanceView, SettingsView


urlpatterns = [
    path("maintenance/", MaintenanceView.as_view(), name="maintenance"),
    path("__tetra__/", include("tetra.urls")),
    path("settings/", SettingsView.as_view(), name="settings"),
]

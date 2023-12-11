from django.urls import path
from .views import MaintenanceView

urlpatterns = [
    path("maintenance/", MaintenanceView.as_view(), name="maintenance"),
]

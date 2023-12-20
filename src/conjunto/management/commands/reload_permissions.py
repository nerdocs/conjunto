import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

import conjunto.tools

User = get_user_model()
logger = logging.getLogger(__file__)


class Command(BaseCommand):
    """Reloads permissions of all apps.

    Checks all apps for a group_permissions attribute and creates Group permissions using that schema.
    """

    help = "Reloads group_permissions for all AppConfigs."

    def handle(self, *args, **options):
        # loop through all apps, not only plugins, and recreates their group permissions
        for app in apps.get_app_configs():
            logger.info(f"Creating {app.label} groups/permissions...")
            if hasattr(app, "groups_permissions"):
                self.stdout.write(f" i Creating groups permissions for {app.label}")
                conjunto.tools.create_groups_permissions(app.groups_permissions)

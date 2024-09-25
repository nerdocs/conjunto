import logging

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django_extensions.management.commands.update_permissions import (
    Command as UpdatePermissionsCommand,
)

import conjunto.tools

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(UpdatePermissionsCommand):
    """Reload permissions of all (given) apps.

    Checks all (given) apps for a group_permissions attribute and creates Group permissions using that schema.

    ```python
    # apps.py
    import ...

    class MyPackageCppConfig(AppConfig):
        group_permissions: {
            "Authors": { my_package.MyContentTypeModel: ["view", "change"],
            # on my special site, admins may not change content, just add/delete it!
            "Site admins": { "my_package.MyContentTypeModel": ["view", "add", "delete"],
        }
    ```
    """

    help = "reloads permissions for specified apps, or all apps if no args are specified, and creates group permissions."

    def handle(self, *args, **options):
        super().handle(*args, **options)

        if options["apps"]:
            app_names = options["apps"].split(",")
            apps = [django_apps.get_app_config(x) for x in app_names]
        else:
            apps = django_apps.get_app_configs()

        # loop through all (given) apps, and recreate their group permissions
        for app in apps:
            if hasattr(app, "groups_permissions"):
                conjunto.tools.create_groups_permissions(app.groups_permissions)
                if options["verbosity"] >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created groups permissions for {app.label}"
                        )
                    )

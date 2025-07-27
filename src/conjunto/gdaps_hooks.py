from django.db import models

from conjunto.audit_log.registry import LogActionRegistry
from conjunto.audit_log.models import ModelLogEntry
from gdaps import hooks
from django.utils.translation import gettext as _


@hooks.implements("register_log_actions")
def register_generic_crud_actions(actions: LogActionRegistry):
    actions.register_model(models.Model, ModelLogEntry)

    # define basic generic hooks for CRUD and logging
    actions.register_action("create", _("Create"), _("Created"))
    actions.register_action("view", _("View"), _("Viewed"))
    actions.register_action("update", _("Update"), _("Updated"))
    actions.register_action("delete", _("Delete"), _("Deleted"))

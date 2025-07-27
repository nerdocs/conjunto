import logging
import typing
import uuid
from django.db import models
from django.utils.functional import LazyObject

from gdaps import hooks
from conjunto.audit_log.context import get_active_log_context
from conjunto.audit_log.formatter import LogFormatter
from conjunto.registry import ObjectTypeRegistry, ModelType

logger = logging.getLogger(__name__)
ActionChoices: type = list[tuple[str, str]]


class LogActionRegistry:
    """
    A central store for log actions.
    The expected format for registered log actions: Namespaced action, Action label, Action message (or callable)
    """

    def __init__(self):
        # Has the register_log_actions hook been run for this registry?
        self.has_scanned_for_actions = False

        # Holds the formatter objects, keyed by action
        self.formatters: dict[str, LogFormatter] = {}

        # Holds a list of action, action label tuples for use in filters
        self.choices: ActionChoices = []

        # Tracks which LogEntry model should be used for a given object class
        self.log_entry_models_by_type = ObjectTypeRegistry()

        # All distinct log entry models registered with register_model
        self.log_entry_models = set()

    def scan_for_actions(self) -> None:
        if not self.has_scanned_for_actions:
            for fn in hooks.get_hooks("register_log_actions"):
                fn(self)

            self.has_scanned_for_actions = True

    def register_model(self, cls: ModelType, log_entry_model) -> None:
        self.log_entry_models_by_type.register(cls, value=log_entry_model)
        self.log_entry_models.add(log_entry_model)

    def register_action(
        self, action: str, label: str = None, message: str = None
    ) -> typing.Callable | None:
        def register_formatter_class(formatter_cls: type(LogFormatter)) -> None:
            formatter: LogFormatter = formatter_cls()
            self.formatters[action] = formatter
            self.choices.append((action, formatter.label))

        if label or message:
            if not label or not message:
                raise ValueError("Both label and message must be provided")
            # register_action has been invoked as register_action(action, label, message);
            # create a LogFormatter subclass and register that
            formatter_cls = type(
                "_LogFormatter", (LogFormatter,), {"label": label, "message": message}
            )
            return register_formatter_class(formatter_cls)
        else:
            # register_action has been invoked as a @register_action(action) decorator;
            # return the function that will register the class
            return register_formatter_class

    def get_choices(self) -> ActionChoices:
        """Returns a list of (action, label) tuples for all registered log actions."""
        self.scan_for_actions()
        return self.choices

    def get_formatter(self, log_entry) -> LogFormatter:
        """Returns the formatter for the given log entry's action."""
        self.scan_for_actions()
        return self.formatters.get(log_entry.action)

    def action_exists(self, action: str) -> bool:
        """Returns True if given action exists in the registry."""
        self.scan_for_actions()
        return action in self.formatters

    def __contains__(self, item):
        """Returns True if given action exists in the registry.

        You can use this as a set membership test:
        ```python
        log_action_registry = LogActionRegistry()
        if "action_1" in log_action_registry:
            pass
        ```
        """
        return self.action_exists(item)

    def get_log_entry_models(self) -> set:
        """Returns a set of all distinct log entry models registered with register_model."""
        self.scan_for_actions()
        return self.log_entry_models

    def get_action_label(self, action: str) -> str:
        """Returns the label for the given log entry's action."""
        return self.formatters[action].label

    def get_log_model_for_model(self, model_class: ModelType) -> "BaseLogEntry":
        """
        Return the log entry model registered for the given model class.

        Parameters:
            model_class: The model class to look up

        Returns:
            The log entry model associated with the given model class, or None if not found
        """
        self.scan_for_actions()
        return self.log_entry_models_by_type.get_by_type(model_class)

    def get_log_model_for_instance(
        self, instance: models.Model | LazyObject
    ) -> "BaseLogEntry":
        """Return the log entry model for the given instance, unwrapping LazyObject
        if needed."""
        if isinstance(instance, LazyObject):
            # for LazyObject instances such as request.user, ensure we're looking up the real type
            instance = instance._wrapped

        model_class = type(instance)
        return self.get_log_model_for_model(model_class)

    def log(
        self,
        instance: models.Model,
        action: str,
        user=None,
        uuid: uuid.UUID = None,
        **kwargs,
    ) -> None:
        """
        Logs an action for a given instance.

        Parameters:
            instance: The Model instance for which to log the action.
            action: The action to log (must be registered already!).
            user: The user performing the action (optional, defaults to the active
                    user).
            uuid: The UUID for this log entry (optional, defaults to a new UUID).
        """
        self.scan_for_actions()

        # find the log entry model for the given object type
        log_entry_model = self.get_log_model_for_instance(instance)
        if log_entry_model is None:
            logger.warning(
                f"No logger registered for this object type: {type(instance)}"
            )
            return None

        user = user or get_active_log_context().user
        uuid = uuid or get_active_log_context().uuid
        return log_entry_model.objects.log_action(
            instance, action, user=user, uuid=uuid, **kwargs
        )

    def get_logs_for_instance(self, instance: models.Model) -> "LogEntryQuerySet":
        """Returns a queryset of log entries for the given model instance."""
        log_entry_model = self.get_log_model_for_instance(instance)
        if log_entry_model is None:
            # this model has no logs; return an empty queryset of the basic log model
            from .models import ModelLogEntry

            return ModelLogEntry.objects.none()

        return log_entry_model.objects.for_instance(instance)


log_action_registry = LogActionRegistry()

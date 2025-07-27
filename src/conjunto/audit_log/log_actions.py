import logging
import typing

from .registry import log_action_registry

if typing.TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def log_action(instance, action, user=None, uuid=None, title=None, data=None, **kwargs):
    """This is the main logging function for individual log entries.

    Parameters:

        instance: The model instance that the action is performed on
        action: The code name for the action being performed. This can be one of the
                names listed below or a custom action defined through the
                register_log_actions hook.
        user (optional): the user initiating the action. For actions logged within
                an admin view, this defaults to the logged-in user.
        uuid (optional): log entries given the same UUID indicates that they occurred
                as part of the same user action (for example a page being immediately
                published on creation).
        title: The string representation, of the instance being logged. By default,
                Conjunto will attempt to use the instance’s str representation or
                get_admin_display_title for objects.
        data (optional): a dictionary of additional JSON-serialisable data to store
                against the log entry


    """
    return log_action_registry.log(
        instance=instance,
        action=action,
        user=user,
        uuid=uuid,
        title=title,
        data=data,
        **kwargs,
    )

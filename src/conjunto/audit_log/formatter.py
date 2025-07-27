import typing

if typing.TYPE_CHECKING:
    from conjunto.audit_log.models import BaseLogEntry


class LogFormatter:
    """
    Defines how to format log messages / comments for a particular action type. Messages that depend on
    log entry data should override format_message / format_comment; static messages can just be set as the
    'message' / 'comment' attribute.

    To be registered with log_registry.register_action.
    """

    label = ""
    message = ""
    comment = ""

    def format_message(self, log_entry: "BaseLogEntry"):
        return self.message

    def format_comment(self, log_entry: "BaseLogEntry"):
        return self.comment

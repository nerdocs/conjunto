import uuid

from asgiref.local import Local

_active = Local()


class LogContext:
    """
    Stores data about the environment in which a logged action happens -
    e.g. the active user - to be stored in the log entry for that action.
    """

    def __init__(self, user=None, generate_uuid: bool = True):
        self.user = user
        self.uuid: uuid.UUID | None = uuid.uuid4() if generate_uuid else None

    def __enter__(self):
        self._old_log_context = getattr(_active, "value", None)
        activate(self)
        return self

    def __exit__(self, type, value, traceback):
        if self._old_log_context:
            activate(self._old_log_context)
        else:
            deactivate()


empty_log_context = LogContext(generate_uuid=False)


def activate(log_context):
    _active.value = log_context


def deactivate():
    del _active.value


def get_active_log_context():
    return getattr(_active, "value", empty_log_context)

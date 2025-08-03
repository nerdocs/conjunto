from django.contrib.messages.storage.base import Message

from tetra import Component, public

toast_positions = {
    "top-left": "top-0 start-0",
    "top-center": "top-0 start-50 translate-middle-x",
    "top-right": "top-0 end-0",
    "bottom-left": "bottom-0 start-0",
    "bottom-center": "bottom-0 start-50 translate-middle-x",
    "bottom-right": "bottom-0 end-0",
}


class Toasts(Component):
    messages: list[Message] = public([])
    delay: int = 8000
    position: str = ""

    def load(self, delay: int = None, position: str = None):
        self.delay = int(delay) if delay is not None else self.delay
        self.position = toast_positions.get(position, toast_positions["top-right"])

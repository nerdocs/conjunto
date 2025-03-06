from tetra import BasicComponent

# TODO mutually exclusive tags are sticky and dismissible, handle this.


class Toast(BasicComponent):
    message: str = ""
    tags: list[str] = []
    sticky: bool = False
    dismissible: bool = False

    def load(self, message, *args, **kwargs):
        self.message = message.message
        self.tags = message.tags if message.tags else ""
        self.dismissible = "dismissible" in message.extra_tags
        self.sticky = "sticky" in message.extra_tags

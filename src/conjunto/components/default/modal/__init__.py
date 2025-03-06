from tetra import Component, public


class Modal(Component):
    """A modal component.

    Blocks:
        footer: A footer block. Per default, the footer shows a "Close" button.

    Attributes:
        title (str): The title of the modal.
        static_backdrop (bool): Whether the backdrop is static or not. Defaults to False.
    """

    id: str = ""
    title: str = ""
    static_backdrop: bool = False

    def load(
        self,
        id: str,
        title: str = "",
        success_event: str = "",
        static_backdrop: bool = False,
        *args,
        **kwargs,
    ):
        self.id = id
        self.title = title
        self.static_backdrop = static_backdrop
        self.success_event = success_event

    @public
    def submit(self):
        self.client._dispatch(self.success_event)

from tetra import Component, public


class BaseModal(Component):
    """Base class bor a modal component. Subclass it to create your own modal
    component with custom public methods.

    Blocks:
        footer: A footer block. Per default, the footer shows a "Close" button.

    Attributes:
        id (str): The id of the modal. This must be passed to a ModalButton as
            `target` attribute.
        title (str): The (optional) title of the modal.
        static_backdrop (bool): Whether the backdrop is static or not. Defaults to False.
        scrollable (bool): If True, the content is scrollable. Defaults to False.
        success_event (str): The event that is fired if the modal is submitted.
    """

    __abstract__ = True

    title: str
    success_event: str
    static_backdrop: bool
    scrollable: bool
    autofocus: str

    def load(
        self,
        id: str,
        title: str = "",
        success_event: str = "",
        static_backdrop: bool = False,
        scrollable: bool = False,
        *args,
        **kwargs,
    ):
        self.id = id
        self.title = title
        self.static_backdrop = static_backdrop
        self.success_event = success_event
        self.scrollable = scrollable
        self.autofocus = f"{id}_ok_button"


class Modal(BaseModal):
    """Default implementation of a simple modal dialog.

    As default, it provides "Cancel" and "Ok" buttons that close the dialog. The "OK"
    button dispatches the `success_event` event on the client.
    """

    @public
    def submit(self):
        self.client._dispatch(self.success_event)

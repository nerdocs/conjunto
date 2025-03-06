from tetra import Component
from tetra.exceptions import ComponentError


class Updatable(Component):
    """
    Tetra component that reloads itself when a certain
    Javascript event is triggerd anywhere in its body.

    Attributes:
        id: the id attribute of the div.
        elt: the HTML element that should be rendered. Default: div
        trigger: the Js event that should trigger the update

    Example:
        ```django
        {% @ Updatable id="my-card" trigger="person:changed" %}

        {% @ Updatable elt="ul" id="people-list" trigger="person:changed" %}
        ```
    """

    elt = "div"
    trigger = ""

    def load(self, trigger: str, elt: str = "div", *args, **kwargs):
        if not trigger:
            raise ComponentError("'trigger' event must be provided.")

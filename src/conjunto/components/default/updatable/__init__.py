from tetra import Component
from tetra.exceptions import ComponentError


class Updatable(Component):
    """
    Tetra component that reloads itself when a certain Javascript event is triggered.

    This can be used as parent for other components that need to be all updated,
    but have no direct connection to each other. When one subcomponent triggers this
    event, the Updatable component will re-render itself, and therefore all its
    children will be re-rendered as well.

    Attributes:
        id: the id attribute of the div.
        elt: the HTML element that should be rendered. Default: div
        trigger: the Js event that should trigger the update

    Example:
        ```django
        {% Updatable id="my-card" trigger="person:changed" %}

        {% Updatable elt="ul" id="people-list" trigger="person:changed" %}
        ```
    """

    elt: str = "div"
    trigger: str = ""

    def load(self, trigger: str, elt: str = "div", *args, **kwargs):
        if not trigger:
            raise ComponentError("'trigger' event must be provided.")
        self.trigger = trigger
        self.elt = elt

from django.core.exceptions import FieldDoesNotExist
from django.utils.text import capfirst
from django_web_components import component
from django.utils.translation import gettext_lazy as _

from conjunto.tools import snake_case2spaces


class SlippersFormatter:
    def format_block_start_tag(self, name):
        return f"#{name}"

    def format_block_end_tag(self, name):
        return f"/{name}"

    def format_inline_tag(self, name):
        return name


@component.register("card")
class Card(component.Component):
    template_name = "conjunto/components/card.html"
    tag = "div"

    def get_context_data(self, **kwargs) -> dict:
        if self.attributes.pop("form", False):
            self.tag = "form"
        return {"tag": self.tag}


@component.register("datagrid")
class DataGrid(component.Component):
    """
    The `DataGrid` class is a component that generates a data grid for displaying data
     in a tabular format.

    It automatically determines all regular model fields and shows their translated
    title. It also detects properties/getters instead of fields, the component tries to
    find out a proper name as title here by creating a capitalized version of the
    property name and translating it into the locale language. However, you have to provide
    a proper translation string for your property name in your .po file manually.

    > **Note**
    > To keep Django's `makemessages` from commenting out these "unused" translations,
    > just add an unused `_("...")` string anywhere into your method.
    > E.g. when your property is named "display_name()", just add a `_("Display name")`
    > anywhere into this method block. This keeps Django from garbage collecting this
    > translation.

    Attributes:
        object: the Django model object to display
        fields: a comma separated list of field names to display

    Example usage:
    ```django
    {% #datagrid object=request.user fields="first_name,last_name,email" %}
    ```
    """

    template_name = "conjunto/components/datagrid.html"

    def get_context_data(self, **kwargs) -> dict:
        """renders fields of given object in a datagrid-usable form."""
        object = self.attributes.pop("object")
        field_name_list: str = self.attributes.pop("fields", "")
        fields = []
        for field_name in field_name_list.split(","):
            field_name = field_name.strip()
            field = {}
            try:
                field["title"] = object._meta.get_field(field_name).verbose_name
            except FieldDoesNotExist:
                # You have to add a translation string manually to your project
                # for this to work. @property display_name() -> "Display name"
                field["title"] = _(capfirst(snake_case2spaces(field_name)))

            # check if there are TextChoices or IntegerChoices to map to
            if hasattr(object, f"get_{field_name}_display"):
                field["content"] = getattr(object, f"get_{field_name}_display")
            else:
                field["content"] = getattr(object, field_name) or "-"

            fields.append(field)

        return {"fields": fields}


@component.register("list")
class List(component.Component):
    """A flexible component to display a Tabler.io list.

    Attributes:
        hoverable: whether the list items are hoverable or not.

    Example:
        ```django
        {% list  hoverable=True %}
          {% for item in items %}
            {% #listitem title=item.title %}
          {% endfor %}
        {% endlist %}
        ```
    """

    template_name = "conjunto/components/list.html"

    def get_context_data(self, **kwargs):
        # TODO: should "items" be renamed into "queryset"
        hoverable = self.attributes.pop("hoverable", False)
        return {"hoverable": hoverable}


@component.register("listitem")
class ListItem(component.Component):
    """A flexible component to display a Tabler.io list item.

    Attributes:
            title (str): The title of the list item.
            subtitle (str): The subtitle of the list item. Optional.
            picture: The picture of the list item. Optional.
            badge_color (str): The color of a badge left of the list item. Optional.
            active (bool): whether the list item is active or not. Defaults to False
            url (str): The URL the title links to. Optional.

    Example:
        ```django
        {% #list-item
            title=item.title
            active=False
            badge_color="red"
        %}
        ```
    """

    template_name = "conjunto/components/list_item.html"

    def get_context_data(self, **kwargs):
        return {
            "title": self.attributes.pop("title"),
            "subtitle": self.attributes.pop("subtitle", None),
            "picture": self.attributes.pop("picture", None),
            "badge_color": self.attributes.pop("badge_color", None),
            "active": self.attributes.pop("active", False),
            "url": self.attributes.pop("url", ""),
        }


@component.register("updatable")
class Updatable(component.Component):
    """
    HTML element that updates itself using HTMX when a certain
    Javascript event is triggerd anywhere in the body.

    Attributes:
        id: the id attribute of the div.
        elt: the HTML element that should be rendered. Default: div
        trigger: the Js event that should trigger the update
        url: the URL to call a get request to update the component

    Example:
        ```django
        {% updatable id="my-card" trigger="person:changed" url=request.path %}

        {% url 'person:update' as person_update_url %}
        {% updatable elt="ul" id="people-list" trigger="person:changed" url=person_update_url %}
        ```
    """

    template_name = "conjunto/components/updatable.html"

    def get_context_data(self, **kwargs) -> dict:
        # TODO: allow multiple triggers
        for attr in ["url", "trigger", "id"]:
            if attr not in self.attributes:
                raise AttributeError(
                    f"{self.__class__.__name__} has no '{attr}' attribute."
                )

        method = self.attributes.pop("method", "get")
        return {
            "id": self.attributes["id"],
            "elt": self.attributes.get("elt", "div"),
            "url": self.attributes["url"],
            "trigger": self.attributes["trigger"],
            "method": method,
        }


@component.register("button")
class Button(component.Component):
    """
    HTMX enabled base button.

    This could be a <button> (default), a <div> or a <a> tag, resulting in a visual
    button.

    Attributes:
        dialog: whether the button should open a dialog or not.
        htmx: whether the button should open a HTMX request or not. If dialog is
            True, HTMX is used obligatory. Defaults to False. If only set without value,
            defaults to "get". If set to "post", a post request is used.
        target: the HTMX target element of the button, if HTMX/dialog is used.
        url: the URL to call a get/post request when using HTMX.
        icon: the icon of the button. Optional.
    """

    template_name = "conjunto/components/button.html"
    tag = "button"
    default_class = "btn"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        dialog = self.attributes.pop("dialog", False)
        htmx = self.attributes.pop("htmx", False)
        if dialog and not htmx:
            htmx = True
        if htmx is True:
            htmx = "get"
        url = self.attributes.pop("url", None)
        context.update(
            {
                "icon": self.attributes.pop("icon", None),
                "url": url,
                "htmx": htmx,
                "target": self.attributes.pop("target", None),
                "dialog": dialog,
                "tag": self.tag,
                "default_class": self.default_class,
            }
        )
        return context


@component.register("actionbutton")
class ActionButton(Button):
    default_class = "btn-action"


@component.register("listgroupaction")
class ListGroupAction(Button):
    tag = "a"
    default_class = "list-group-item-actions"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        if "url" not in context:
            raise AttributeError(f"{self.__class__.__name__} has no 'url' attribute.")
        return context

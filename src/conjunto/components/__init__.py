from django.core.exceptions import FieldDoesNotExist
from django.utils.text import capfirst
from django_web_components import component
from django.utils.translation import gettext_lazy as _

from conjunto.tools import snake_case2spaces

from .list import List


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


@component.register("datagrid")
class DataGrid(component.Component):
    """
    The `DataGrid` class is a component that generates a data grid for displaying data
     in a tabular format.

    It automatically determines all regular model fields and shows their translated
    title. It also detects properties/getters instead of fields, the component tries to
    find out a proper name as title here by creating a capitalized version of the
    property name and translating it into the locale language. However you have to provide
    a proper translation string for your property name in your .po file manually.

    > **Note**
    > To keep Django's makemessaes from commenting out these "unused" translations,
    > just add an unused `_("...")` string anywhere into your method.
    > E.g. when your property is named "display_name()", just add a `_("Display name")`
    > anywhere into this method block. This keeps Django from garbage collecting this
    > translation.

    Attributes:
    - object: the Django model object to display
    - fields: a comma separated list of field names to display

    Example usage:
    ```django
    {% datagrid object=request.user fields="first_name,last_name,email" %}
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
            field["content"] = getattr(object, field_name) or "-"
            fields.append(field)

        return {"fields": fields}

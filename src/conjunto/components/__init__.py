from django_web_components import component


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
            field["title"] = object._meta.get_field(field_name).verbose_name
            field["content"] = getattr(object, field_name)
            fields.append(field)

        return {"fields": fields}

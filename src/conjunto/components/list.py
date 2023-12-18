from django_web_components import component


@component.register("list")
class List(component.Component):
    """A flexible component to display a Tabler.io list."""

    template_name = "conjunto/components/list.html"

    def get_context_data(self, items: list, hoverable: bool = False):
        return {"items": "items", "hoverable": hoverable}

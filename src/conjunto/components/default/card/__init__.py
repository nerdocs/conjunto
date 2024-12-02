from tetra import BasicComponent


class Card(BasicComponent):
    template_name = "conjunto/components/card.html"
    tag = "div"
    _extra_context = "__all__"

    def load(self, form=None) -> None:
        if form:
            self.tag = "form"

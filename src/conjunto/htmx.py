from django.http import HttpRequest
from django.urls import reverse

from conjunto.menu import IActionButton

# FIXME: htmx is deprecated


class HxLink:
    """Render a hyperlink using HTMX.

    Attributes:
        url: the URL.
        text: the text to display.
        icon: the (optional) icon to display before the text.
        dialog: whether to open a modal dialog. Defaults to `False`.
    """

    def __init__(
        self,
        url: str,
        text: str,
        icon: str = None,
        dialog: bool = False,
    ):
        self.url = url
        self.text = text
        self.dialog = dialog
        if icon:
            self.text = (
                # f"{Icon(icon)}'></i> {text}"
                f"<i class='ti ti-{icon}'></i> {text}"
            )

    def __str__(self):
        target = ""
        if self.dialog:
            target = " hx-target='#dialog'"
        return f"<a href='#' hx-get='{self.url}'{target}>{self.text}</a>"


class HxButton:
    """Render a HTMX enabled button.

    Attributes:
        url: the text to display
        icon: the (optional) icon to display
        dialog: whether to open a modal dialog (sets `hx-target` to `#dialog`)
        target: the target to open the link in. Cannot be used together with `dialog`.
        css_class: the css classes to apply to the button
        method: the method to call on click ("get" or "post"). Default is "get".
        view_name: the name of the view to call on click, if no url is provided.
            if provided, the render method must be called with url params if they are
            needed to create the url using reverse(view_name, kwargs)

    Example:
        ```django
        {% hx_button url="person:add" method="post" icon="plus" dialog=True css_class="btn"
        ```
    """

    def __init__(
        self,
        url: str = None,
        view_name: str = None,
        icon: str = None,
        dialog: bool = False,
        css_class: str = None,
        method: str = None,
        target: str = None,
        title: str = None,
    ):
        if not url and not view_name:
            raise AttributeError("'url' or 'view_name' must be provided")
        if url and view_name:
            raise AttributeError("'url' and 'view_name' cannot be used together")
        self.url = url
        self.view_name = view_name
        self.icon = icon
        if target and dialog:
            raise AttributeError("'target' and 'dialog' cannot be used together")
        self.dialog = dialog
        self.target = target
        self.css_class = css_class
        self.title = title

        if not method:
            method = "get"
        if method not in ["get", "post"]:
            raise ValueError(f"method must be 'get' or 'post', not '{method}'")
        self.method = method

    def render(self, *args, **kwargs):
        if self.view_name:
            self.url = reverse(self.view_name, args=args, kwargs=kwargs)
        target = ""
        if self.dialog:
            target = " hx-target='#dialog'"
        elif target:
            target = f" hx-target='{target}'"
        title_attr = f" title='{self.title}'" if self.title else ""

        return (
            f"<button hx-{self.method}='{self.url}'{target} "
            f"class='{self.css_class}'{title_attr}><i class='ti ti-"
            f"{self.icon}'></i></a>"
        )

    def __str__(self):
        return self.render()


# FIXME: deprecated
class HxActionButton(HxButton):
    """A renderable action button from an IActionButton instance.

    Arguments:
        request: the current request
        action_button: the IActionButton class
    """

    def __init__(
        self, request: HttpRequest, action_button: IActionButton, *args, **kwargs
    ):
        css_class = kwargs.pop("css_class", "")
        css_class += " btn-action"
        # initialize the button with the IActionButton's values
        kwargs.update(
            dict(
                method=action_button.method,
                icon=action_button.icon,
                css_class=css_class.strip(),
                view_name=action_button.view_name,
                title=action_button.title,
            )
        )
        super().__init__(*args, **kwargs)

    def __str__(self):
        raise NotImplementedError(
            "Please use the render() method directly instead and provide some kwargs."
        )

    def render(self, row_object, *args, **kwargs):
        # button = self.action_button_class(kwargs["request"], row_object)
        return super().render(pk=row_object.pk)

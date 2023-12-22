from django.http import HttpRequest
from django.urls import reverse, URLPattern, path
from gdaps.api import InterfaceRegistry

from conjunto.menu import IActionButton
from conjunto.tools import camel_case2snake
from conjunto.views import HtmxResponseMixin


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
            self.text = f"{Icon(icon)}'></i> {text}"

    def __str__(self):
        target = ""
        if self.dialog:
            target = " hx-target='#dialog'"
        return f"<a href='#' hx-get='{self.url}'{target}>{self.text}</a>"


class Icon:
    """Render an icon using Bootstrap 5.

    Attributes:
        name: the name of the icon
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"<i class='bi bi-{self.name}'></i>"


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
            f"class='{self.css_class}'{title_attr}>{Icon(self.icon)}</a>"
        )

    def __str__(self):
        return self.render()


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


class IHtmxComponentMixin(HtmxResponseMixin):
    """An interface Mixin that describes a component and can be rendered
    as plugin.

    1. Declare an interface for HTMX components
    2. Declare Implementations of that interface which also inherit from `View`.

    Examples:
        ```
        # in your plugin's api/interfaces.py, create an interface for your view
        @Interface
        class IUserProfileSection(IHtmxComponentMixin, ...):
            params = ["pk"]
            template_name = "common/layout/profile_section.html"
            ...

        # in your plugin's views.py
        def PasswordView(IUserProfileSection, UpdateView)
            ...
        def OtherComponentView(IUserProfileSection, TemplateView)
            ...
        ```

        Use them in your template:
        ```django
        {% for plugin in components.IUserProfileSection %}
            <a href="#"
               hx-get="{% url component.get_url_name user.id %}"
               hx-trigger="{% if component.selected %}load, {% endif %}click once"
               {# hx-push-url="{{ component.name }}" #}
               hx-target="#profile-content"
               class="list-group-item list-group-item-action d-flex align-items-center
                active">
                <i class="bi bi-{{ component.icon }} me-2"></i>
                {{ component.title }}
             </a>
        {% endfor %}
        ```

        You can also inherit from other mixins, e.g. PermissionRequiredMixin, etc.

        ```python
        class UserprofilePasswordSection(
            IUserProfileSection, PermissionRequiredMixin, TemplateView
        ):
            name = "password"
            permission_required = "..."
            template_name = "my_app/password_view.html
        ```
    """

    name: str = ""
    """The view name of the component. 
    Must be unique. Used in and URLs. Can be used for HTML attributes."""

    title: str = ""
    """The title this plugin is rendered with.
    It's up to you how the plugin uses that title."""

    icon: str = ""
    """the icon name, if the component is listed in a list, and icons are used."""

    weight: int = 0
    """The weight this component is ranked like menu items. 
    The more weight, the more the component sinks "down" in the list."""

    group = ""
    """The group this component lives under. Can be used to display group headers."""

    params: list[str] = []
    """A list of params the view is using. These must then be passed when calling
    the view from a template, e.g. via hx-get."""

    form_kwargs_request = False
    """Should the evtl. attached form receive a request?"""

    # HTMX is always enforced for components
    enforce_htmx = True

    def __init__(self, *args, **kwargs):
        if not self.name:
            raise AttributeError(
                f"{self.__class__.__name__} does not have a 'name' attribute."
            )
        super().__init__(*args, **kwargs)

    def get_name(self) -> str:
        """Returns the component's view (machine) name."""
        return f"{self.name}"

    def get_title(self) -> str:
        """returns the component's title.

        Use it in templates like {{ component.get_title }}
        """
        return self.title

    def get_url_name(self) -> str:
        """Returns the component's url.'

        Use it as `{% url component.get_url ... %}` in a template.
        """
        return f"components:{self.get_name()}"

    def get_urlpattern(self) -> URLPattern:
        """Calculates the urlpattern where this component is accessible.

        That can be used e.g. in hx-get attributes.
        Returns:
            a URLPattern that can be used in your urls.py
        """
        params = [f"<{p}>" for p in self.params]
        # if in production, hash component name, to hide it from prying eyes...
        component_name = camel_case2snake(self.__class__.__name__)
        if params:
            url = f"{component_name}/{'/'.join(params)}/{self.name}/"
        else:
            url = f"{component_name}/{self.name}/"
        return path(
            url,
            self.__class__.as_view(),
            name=self.name,
        )

    @classmethod
    def get_url_patterns(cls) -> list[URLPattern]:
        """Convenience method to add to your urls.py in an include section:

        Example:
            ```python
            url_patterns = [
                path(...),
                path("profile/",
                    include(
                        (IUserProfileSectionView.get_url_patterns(), "profile"),
                        namespace="profile"
                    )
                ),
            ]

            # or directly add the url_patterns to the main list:

            url_patterns += IUserProfileSectionView.get_url_patterns()
            ```
        """
        patterns = []
        for interface in InterfaceRegistry._interfaces:
            if issubclass(interface, cls):
                for plugin in interface:
                    patterns.append(plugin.get_urlpattern())
        return patterns

    def enabled(self) -> bool:
        # FIXME: rename into "visible"
        """Hook for implementations to define if the component is enabled.

        Returns:
            True if the component is enabled, False if not.
        """
        return True

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        if self.form_kwargs_request:
            kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self):
        return self.request.path


class UseComponentMixin:
    """A mixin that can be added to a View that uses HTMX components.

    This can be used if e.g. a View has tabs, or variable parts of the page
    that are extended by a component. The URL is pushed automatically with the new
    component as configurable GET parameter, e.g.: `example.com/persons/42?tab=account`

    Example:
        ```python
        class MyView(UseComponentMixin, DetailView):
            components = [PersonAccountTab]
        ```


    Attributes:
        components: a list of Interfaces that are used in the template of this
            view, and can be accessed there using `components.IFooInterface`.
    """

    components: list[IHtmxComponentMixin] = []
    default_component_name = ""

    query_variable = "tab"
    """The query variable that is used to indicate the active component."""

    def __init__(self, **kwargs):
        if not self.components:
            raise AttributeError(
                f"{self.__class__.__name__} must define a 'components' attribute "
                f"with a list of of used plugins."
            )
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        component_dict = {}
        active_component = None
        for plugin_class in self.components:
            implementations = list(plugin_class)
            component_dict[plugin_class.__name__] = implementations
            for plugin in implementations:
                if plugin.name == self.request.GET.get(self.query_variable, None):
                    active_component = plugin.name
            # if no component is selected via GET, use the default one
            if not active_component:
                active_component = self.default_component_name

        context.update(
            {"components": component_dict, "active_component": active_component}
        )
        return context

    # @classmethod
    # def component_urls(cls) -> list[URLPattern]:
    #     """Returns urlpatterns for all included plugins.
    #
    #     This is for having easy-to-use URLs for a component
    #     use it in your urls.py:
    #     path("foo/", FooView.as_view(), name="foo),
    #     path("foo/", include(FooView.component_urls())),
    #     """
    #     patterns = []
    #     for components in cls.components:
    #         for component in components:
    #             patterns.append(
    #                 path(
    #                     component.get_path(),
    #                     component.__class__.as_view(),
    #                     name=component.name,
    #                 )
    #             )
    #     return patterns

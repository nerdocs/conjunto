from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import URLPattern, path

from conjunto.tools import camel_case2snake
from gdaps.api import Interface, InterfaceRegistry


User = get_user_model()


class HtmxRequestMixin:
    """Optionally checks if request originates from HTMX.

    Attributes:
        enforce_htmx: if True, all requests that do not come from a HTMX
            element are blocked.

    Raises:
        PermissionDenied: if enforce_htmx==True and request origins from a
            non-HTMX caller.
    """

    enforce_htmx: bool = True

    def dispatch(self, request, *args, **kwargs):
        if self.enforce_htmx and not self.request.htmx:
            raise PermissionDenied(
                f"Permission denied: View {self.__class__.__name__} can only be "
                "called by a HTMX request."
            )
        return super().dispatch(request, *args, **kwargs)


class IHtmxElementMixin(HtmxRequestMixin):
    """An interface mixin that describes an element and can be rendered as plugin.

    1. Declare an interface for HTMX element
    2. Declare Implementations of that interface which also inherit from `View`.

    Examples:
        ```
        # in your plugin's api/interfaces.py, create an interface for your view
        @Interface
        class ISettingsSection(IHtmxElementMixin, ...):
            params = ["pk"]
            template_name = "conjunto/layouts/settings_section.html"
            ...

        # in your plugin's views.py
        def AccountSettingsView(ISettingsSection, TemplateView)
            ...
        def OtherElementView(ISettingsSection, TemplateView)
            ...
        ```

        Use them in your template:
        ```django
        {% for element in elements.ISettingsSection %}
            <a href="#"
               hx-get="{% url element.get_url_name user.id %}"
               hx-trigger="{% if element.selected %}load, {% endif %}click once"
               {# hx-push-url="{{ element.name }}" #}
               hx-target="#profile-content"
               class="list-group-item list-group-item-action d-flex align-items-center
                active">
                <i class="bi bi-{{ element.icon }} me-2"></i>
                {{ element.title }}
             </a>
        {% endfor %}
        ```

        You can also inherit from other mixins, e.g. PermissionRequiredMixin, etc.

        ```python
        class UserprofilePasswordSection(
            ISettingsSection, PermissionRequiredMixin, TemplateView
        ):
            name = "password"
            permission_required = "..."
            template_name = "my_app/password_view.html
        ```
    """

    name: str = ""
    """The view name of the element. 
    Must be unique. Used in URLs. Can be used for HTML attributes."""

    title: str = ""
    """The title this plugin is rendered with.
    It's up to you how the plugin uses that title."""

    icon: str = ""
    """The icon name, if the element is listed in a list, and icons are used."""

    weight: int = 0
    """The weight this element is ranked like menu items. 
    The more weight, the more the element sinks "down" in the list."""

    group = ""
    """The group this element lives under. Can be used to display group headers."""

    params: list[str] = []
    """A list of params the view is using. These must be passed in the URL when calling
    the view from a template, e.g. via hx-get."""

    form_kwargs_request = False
    """Should the evtl. attached form receive a request?"""

    # HTMX is always enforced for elements
    enforce_htmx = True

    # choose the model this element is using, if any.
    model = None

    def __init__(self, *args, **kwargs):
        if not self.name:
            raise AttributeError(
                f"{self.__class__.__name__} does not have a 'name' attribute."
            )
        super().__init__(*args, **kwargs)

    def get_name(self) -> str:
        """Returns the element's view (machine) name."""
        return f"{self.name}"

    def get_title(self) -> str:
        """returns the element's title.

        Use it in templates like {{ element.get_title }}
        """
        return self.title

    def get_url_name(self) -> str:
        """Returns the element's url.'

        Use it as `{% url element.get_url_name ... %}` in a template.
        """
        return f"elements:{self.get_name()}"

    def get_urlpattern(self) -> URLPattern:
        """Calculates the urlpattern where this element is accessible.

        That can be used e.g. in hx-get attributes.
        Returns:
            a URLPattern that can be used in your urls.py
        """
        params = [f"<{p}>" for p in self.params]
        # if in production, hash element name, to hide it from prying eyes...
        element_name = camel_case2snake(self.__class__.__name__)
        if params:
            url = f"{element_name}/{'/'.join(params)}/{self.name}/"
        else:
            url = f"{element_name}/{self.name}/"
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
                        (ISettingsSectionView.get_url_patterns(), "profile"),
                        namespace="profile"
                    )
                ),
            ]

            # or directly add the url_patterns to the main list:

            url_patterns += ISettingsSectionView.get_url_patterns()
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
        """Hook for implementations to define if the element is enabled.

        Returns:
            True if the element is enabled, False if not.
        """
        return True

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        if self.form_kwargs_request:
            kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"element": self})
        return context


class IBaseSettingsSectionMixin(IHtmxElementMixin):
    """Common base mixin for settings sections and subsections."""

    url_pattern = None

    # always return to the current element after successful save
    success_url = "."
    reload_triggers: list[str] = []

    def has_permission(self) -> bool:
        """
        If this view inherits from PermissionRequiredMixin,
        provide standard authentication checks. If this view doesn't inherit from
        PermissionRequiredMixin, you can ignore this method.

        1. only allow authenticated users
        2. if there is an additional "permission_required" attribute, check for this
        perm additionally. If not, allow the user to display the view.
        """
        return self.request.user.is_authenticated and (
            self.request.user.has_perm(self.permission_required)
            if hasattr(self, "permission_required")
            else True
        )

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     if queryset:
    #         return queryset.get(pk=self.kwargs.get("pk"))
    #     elif self.model:
    #         return self.model.objects.get(pk=self.kwargs.get("pk"))
    #     else:
    #         return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.reload_triggers, str):
            self.reload_triggers = [self.reload_triggers]
        context.update(
            {
                "element": self,
                "reload_trigger": ", ".join(
                    [f"{t} from:body" for t in self.reload_triggers]
                ),
            }
        )
        return context


class UseElementMixin:
    """A mixin that can be added to a View that uses HTMX "elements".

    This can be used if e.g. a View has tabs, or variable parts of the page
    that are extended by a element. The URL is pushed automatically with the new
    element as configurable GET parameter, e.g.: `example.com/persons/42?tab=account`

    Example:
        ```python
        class MyView(UseElementMixin, DetailView):
            elements = [IPersonAccountTab]
        ```


    Attributes:
        elements: a list of Interfaces that are used in the template of this
            view, and can be accessed there using `blocks.IFooInterface`.
    """

    elements: list[IHtmxElementMixin] = []
    default_element_name = ""

    query_variable = "tab"
    """The query variable that is used to indicate the active element."""

    def __init__(self, **kwargs):
        if not self.elements:
            raise AttributeError(
                f"{self.__class__.__name__} must define a 'elements' attribute "
                f"with a list of of used plugins."
            )
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        element_dict = {}
        active_element = None
        for plugin_class in self.elements:
            implementations = list(plugin_class)
            element_dict[plugin_class.__name__] = implementations
            for plugin in implementations:
                if plugin.name == self.request.GET.get(self.query_variable, None):
                    active_element = plugin.name
            # if no element is selected via GET, use the default one
            if not active_element:
                active_element = self.default_element_name

        context.update({"elements": element_dict, "active_element": active_element})
        return context

    # @classmethod
    # def element_urls(cls) -> list[URLPattern]:
    #     """Returns urlpatterns for all included plugins.
    #
    #     This is for having easy-to-use URLs for a element
    #     use it in your urls.py:
    #     path("foo/", FooView.as_view(), name="foo),
    #     path("foo/", include(FooView.element_urls())),
    #     """
    #     patterns = []
    #     for elements in cls.elements:
    #         for element in elements:
    #             patterns.append(
    #                 path(
    #                     element.get_path(),
    #                     element.__class__.as_view(),
    #                     name=element.name,
    #                 )
    #             )
    #     return patterns


class ISettingsSubSectionMixin(IBaseSettingsSectionMixin):
    """Mixin class to create interfaces for plugin hooks that are rendered as HTMX
    subsection in the settings page.

    This is fo creating **interfaces**, not implementations. The name could match
    the section name you are using, so that you can associate it with it.
    Create a subsection interface with this mixin for one section. You can add this
    interface then to your Section as `elements`.

    Conjunto provides a standard template for subsections, but you can override this
    using the `template_name` attribute.

    Attributes:
        template_name: the name of the template that is used to render the
            subsection.

    Example:
        ```python
        @Interface
        class IAccountSubSection(ISettingsSubSectionMixin):
            pass
        ```
    """

    template_name = "conjunto/layouts/settings_subsection.html"
    # FIXME: this should not be necessary.
    # But without it, a call to <host>/<path>/?section=account would fail.
    enforce_htmx = False


@Interface
class ISettingsSection(UseElementMixin, IBaseSettingsSectionMixin):
    # FIXME: add PermissionRequiredMixin to this class.
    """
    Plugin hook that is rendered as HTMX view in the settings page section.

    Typically, you create a section for you settings (using the ISettingsSection
    interface), and fill it's `elements` list with subsection interfaces you want to use
    in this section.

    Examples:
        @Interface
        class IAccountSubSection(ISettingsSubSectionMixin):
            '''This is the interface for your subsections'''

        class AccountSection(ISettingsSection, PermissionRequiredMixin, DetailView):
            '''This is the main "account" section of your settings.'''
            name = "account_general"
            group = _("Account")
            title = _("General Account settings")
            elements = [IAccountSubSection]
            permission_required = "<app>.view_<your_model>"

        class PasswordSubSection(IAccountSubSection, PasswordChangeView):
            '''This will be shown as subsection of "Account"'''

        class SocialMediaSubSection(IAccountSubSection, PasswordChangeView):
            '''This will be shown as subsection of "Account"'''
    """

    __sort_attribute__ = "group"
    params = ["pk"]
    template_name = "conjunto/layouts/settings_section.html"

    # FIXME: this should not be necessary.
    # But without it, a call to <host>/<path>/?section=account would fail.
    enforce_htmx = False

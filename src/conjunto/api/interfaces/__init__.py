from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from gdaps import hooks
from gdaps.api import Interface
from django.utils.translation import gettext_lazy as _

User = get_user_model()

from conjunto.audit_log.registry import LogActionRegistry

hooks.define("register_log_actions", (LogActionRegistry,))


class HtmxRequestMixin:
    # FIXME: deprecated

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


class IElementGroup(Interface):
    """A group of settings sections.

    Implementations of this interface should provide a name, title, and weight of the group.
    You can use this group then in IElements to separate concerns.
    """

    name: str = None
    title: str = None
    weight: int = 0

    # def __int__(self) -> int:
    #     return self.weight


class GeneralGroup(IElementGroup):
    """A default group for all elements without a specified group."""

    name = "general"
    title = _("General settings")


class IElementMixin:
    """An interface mixin that describes an element and can be rendered as
    plugin.

    1. Declare a GDAPS Interface for a pluggable element with a subclass of
        IElementMixin, like `class ISettingsSection(IElementMixin, Interface):`.
    2. Create implementations of that interface that describe the element's behavior,
        with filled out name, and optionally group, icon, weight etc. attributes.
    3. Use them in your template by iterating over ISettingsSection

    Examples:
        ```
        # in your plugin's api/interfaces.py, create an interface for your settings
        section:
        class ISettingsSection(IElementMixin, ..., Interface):
            template_name = "conjunto/layouts/settings_section.html"
            ...

        # in your plugin's views.py
        def AccountSettingsView(ISettingsSection, TemplateView)
            ...
        def OtherSettingsView(ISettingsSection, TemplateView)
            ...
        ```

        You can also inherit from other mixins, e.g. PermissionRequiredMixin, etc.

        ```python
        class UserprofilePasswordSection(
            ISettingsSection, PermissionRequiredMixin, TemplateView
        ):
            name = "password"
            permission_required = "..."
        ```
    """

    def __init__(self, *args, **kwargs):
        # if this is a plugin, in must have a name; Interfaces don't.
        if hasattr(self, "_interface") and not self.name:
            raise AttributeError(
                f"{self.__class__.__name__} must have a 'name' attribute."
            )

    name: str
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

    group: IElementGroup = GeneralGroup
    """The group this element lives under. Can be used to display group headers."""

    @classmethod
    def enabled(cls) -> bool:
        """Hook for implementations to define if the element is enabled.

        Returns:
            True if the element is enabled (default), False if not.
        """
        return True

    # @classmethod
    # def visible(cls) -> bool:
    #     """Hook for implementations to define if the element is visible.
    #
    #     Returns:
    #         True if the element is visible (default), False if not.
    #     """
    #     return True

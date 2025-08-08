from conjunto.api.interfaces.settings import ISettingsSection
from gdaps.api import InterfaceMeta, Interface
from tetra import Component, public


class SettingsWidget(Component):
    """A Tabler Settings page widget

    Attributes:
        sections: an IElementMixin plugin hook.
            This is the hook that is used to render the sections
            Default: `ISettingsSection`
        active: The name of the active tab.
            Must correspond to a `name` attribute of an `ISettingsSection` plugin
            implementation
        q: The query parameter to use for URL changes.

    Usage:
    Simple usage with predefined "active" tab
    ```django
    {% SettingsWidget active="account" %}
    ```

    Change tabs using URLs:
    `/settings?tab=account` displays the section with the name "account". You can
    specify the URL parameter by the `q` attribute. Per default "tab" is used.

    ```django
    {% SettingsWidget sections=ISettingsSection q="tab" %}
    ```
    """

    sections = ISettingsSection
    active_section_name: str = ""
    url_param: str = "tab"

    def load(
        self,
        sections: InterfaceMeta = None,
        active: str = None,
        q: str = None,
        *args,
        **kwargs,
    ) -> None:
        self.sections = sections if sections is not None else ISettingsSection
        self.url_param = q or "tab"

        self.active_section_name = self.request.GET.get(self.url_param, None) or active
        if not self.active_section_name or not Interface.get(
            name=self.active_section_name
        ):
            first = self.sections.first()  # default to first section
            self.active_section_name = first.name if first else ""

    @public
    def show_section(self, element_name):
        if element_name:
            selected = self.sections.get(name=element_name)
            if selected is not None:
                self.active_section_name = element_name
                self.push_url(f"?{self.url_param}={element_name}")

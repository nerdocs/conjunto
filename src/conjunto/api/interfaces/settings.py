from typing import Type

from django.utils.translation import gettext_lazy as _

from conjunto.api.interfaces import IElementMixin, IElementGroup
from conjunto.components.settings.account_section_widget import AccountSectionWidget
from gdaps.api import Interface
from tetra.components.base import (
    ComponentMetaClass,
    FormComponentMetaClass,
    ModelFormComponentMetaClass,
)


class IBaseSubSection(IElementMixin):
    """Generic base class for SubSections interfaces.

    This is a base class for creating **interfaces**, not implementations.

    Create at least one SubSection interface per section by inheriting this class.
    You can add this interface then to your Section as `subsections` attribute.

    Example:
        ```python
        class IAccountSubSection(IAbstractSettingsSubSection, Interface):
            pass

        class PasswordSubSection(IAccountSubSection):
            name = "password"
        ```
    """


class IBaseSection(IElementMixin):
    """Generic base class for Sections interfaces.

    This is a base class for creating **interfaces**, not implementations.

    Attributes:
        name: a unique identifier for the section.
        group: the group this section belongs to. Must be an `IElementGroup`.
        title: the title of the section.
        subsections: the interface that subsections can implement to be rendered in this section.
            the `subsections` attribute should be an `IAbstractSubSection` interface.
    """

    __sort_attribute__ = "group"

    subsections: Type[Interface] = None
    """The interface that subsections can implement to be rendered in this section."""


class ISettingsSection(IBaseSection, Interface):
    # FIXME: add PermissionRequiredMixin to this class.
    """
    Plugin hook that is rendered as section in the settings component.

    Typically, you:
    * create a section for your settings (using the ISettingsSection interface),
    * define its interface for subsections as `subsections` attribute:
        `subsections = ISomeSubsection`
    * Create its subsections' implementations you want to use in this section.

    Attributes:
        name: a unique identifier for the section.
        group: the group this section belongs to. Must be an `IElementGroup`.
        title: the title of the section.

        permission_required: a Django permission required to access this section.

    Examples:
        class IAccountSubSection(ISettingsSubSection,Interface):
            '''This is the *interface* for your subsections'''

        class AccountSection(ISettingsSection, PermissionRequiredMixin):
            '''This is the main "account" section of your settings.'''
            name = "account_general"
            group = AccountGroup
            title = _("General Account settings")
            subsections = IAccountSubSection
            permission_required = "<app>.view_<your_model>"

        class PasswordSubSection(IAccountSubSection, PasswordChangeComponent):
            '''This will be shown as subsection of "Account"'''
            ...

        class SocialMediaSubSection(IAccountSubSection, PasswordChangeComponent):
            '''This will be shown as subsection of "Account"'''
            ...
    """


# ----------------- Settings Groups -----------------


class AccountGroup(IElementGroup):
    name = "account"
    weight = 0
    title = _("Account")


class TenantGroup(IElementGroup):
    name = "tenants"
    weight = 20
    title = _("Tenant")


# ----------------- Settings Sections -----------------


class IProfileSubSection(IBaseSubSection, Interface):
    pass


class AccountSection(ISettingsSection):
    name = "account"
    group = AccountGroup
    title = _("Account")
    icon = "user"
    weight = 0
    subsections = IProfileSubSection


# multi-tenancy
# class ITenantSubSection(IBaseSubSection, Interface):
#     pass
#
#
# class TenantSection(ISettingsSection):
#     name = "tenants"
#     group = TenantGroup
#     title = _("Tenants")
#     icon = "user-square"
#     subsections = ITenantSubSection
#
#     def enabled(cls) -> bool:
#         return super().enabled()

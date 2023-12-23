from conjunto.models import Page, VersionedPage
from django.utils.translation import gettext_lazy as _


# Create your models here.
class StaticPage(Page):
    """A page that holds static content."""

    class Meta:
        verbose_name = _("Static page")
        verbose_name_plural = _("Static pages")


class LicensePage(VersionedPage):
    """A page that holds the license information for this software."""

    class Meta:
        verbose_name = _("License page")
        verbose_name_plural = _("License pages")


class PrivacyPage(VersionedPage):
    """A page that holds the privacy information for this software."""

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")


class StaticVersionedPage(VersionedPage):
    class Meta:
        abstract = True

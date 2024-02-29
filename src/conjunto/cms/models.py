from django.db import models

from conjunto.models import Content, VersionedPage
from django.utils.translation import gettext_lazy as _


# Create your models here.
class StaticPage(Content):
    """A page that holds static content.

    You can add a `name` attribute to match it with `conjunto.constants.StaticPages`
    """

    class Meta:
        verbose_name = _("Static page")
        verbose_name_plural = _("Static pages")

    name = models.CharField(
        max_length=255,
        help_text=_("Internal name of the page. Leave empty of in doubt."),
        blank=True,
        null=True,
    )


class TermsConditionsPage(VersionedPage):
    """A page that holds the license information for this software."""

    class Meta:
        verbose_name = _("Terms and conditions page")
        verbose_name_plural = _("Terms and conditions pages")


class PrivacyPage(VersionedPage):
    """A page that holds the privacy information for this software."""

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")


class StaticVersionedPage(VersionedPage):
    class Meta:
        abstract = True

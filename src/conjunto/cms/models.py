from django.db import models

from django.utils.translation import gettext_lazy as _
from versionfield import VersionField


class Content(models.Model):
    """Base class for content pages with a title and body."""

    title = models.CharField(max_length=255)
    body = models.TextField()


class VersionedPageMixin(models.Model):
    """Mixin for versioned pages."""

    class Meta:
        abstract = True

    version = VersionField()


class StaticPage(Content):
    """A page that holds static content.

    You can add a `name` attribute to match it with `conjunto.constants.StaticPages`
    """

    class Meta:
        verbose_name = _("Static page")
        verbose_name_plural = _("Static pages")

    # FIXME: find a better name like "machine_name", "internal_name" etc. as it may
    #  clash with user defined fields (think of Person.name)
    name = models.CharField(
        max_length=255,
        help_text=_("Internal name of the page. Leave empty of in doubt."),
        blank=True,
        null=True,
    )


class VersionedPage(VersionedPageMixin, Content):
    """A page that holds content and version information."""

    class Meta:
        abstract = True


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


# class StaticVersionedPage(VersionedPage):
#     class Meta:
#         abstract = True

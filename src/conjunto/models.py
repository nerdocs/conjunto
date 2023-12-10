from django.db import models
from versionfield import VersionField


class Page(models.Model):
    """Represents a generic page.

    This class is an abstract base class that provides common fields and methods for all page subclasses.
    """

    class Meta:
        abstract = True

    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class VersionedPage(Page):
    """Represents a generic page with versioning.

    This class is an abstract base class that provides common fields and methods for all page subclasses.
    """

    class Meta:
        abstract = True

    version = VersionField(default="1.0.0")

    def __str__(self):
        return f"{self.title} (v{self.version})"


class StaticPage(Page):
    pass


class StaticVersionedPage(VersionedPage):
    pass


class LicensePage(VersionedPage):
    """A page that holds the license information for this software."""


class PrivacyPage(VersionedPage):
    """A page that holds the privacy information for this software."""

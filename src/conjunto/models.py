from django.core.exceptions import ValidationError
from django.db import models
from versionfield import VersionField


# thanks to https://stackoverflow.com/questions/49735906/how-to-implement-singleton-in-django/49736970#49736970
class SingletonModel(models.Model):
    """Singleton Django Model"""

    class Meta:
        abstract = True

    # _aggressive = False

    def save(self, *args, **kwargs):
        """Save object to the database.

        If 'aggressive' Meta attribute is set, remove all other entries if there are any.

        Raises:
            ValidationError if
        """

        # if self._aggressive:
        #     self.__class__.objects.exclude(id=self.id).delete()
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError(
                f"There can be only one {self.__class__.__name__} instance."
            )
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load object from the database.

        Failing that, create a new empty (default) instance of the object and return it
        (without saving it to the database).
        Raises:
            MultipleObjectsReturned if there are more objects saved in the databases.
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


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

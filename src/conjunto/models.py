from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import models, IntegrityError
from versionfield import VersionField
from django.utils.translation import gettext as _


# thanks to https://stackoverflow.com/questions/49735906/how-to-implement-singleton-in-django/49736970#49736970
class SingletonModel(models.Model):
    """Singleton Django Model.

    Allow only one instance of the model to be created.
    To get the instance of the model, use `<YourModel>.get_instance()`.
    """

    class Meta:
        abstract = True

    # _aggressive = False

    def save(self, *args, **kwargs):
        """Save object to the database.

        Raises:
            IntegrityError: if there is already another instance in the database.
        """

        # If '_aggressive' attribute is set, remove all other entries if there are any.
        # if self._aggressive:
        #     self.__class__.objects.exclude(id=self.id).delete()
        if not self.pk and self.__class__.objects.exists():
            raise IntegrityError(
                f"There can be only one {self.__class__.__name__} instance."
            )
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Load object from the database.

        Failing that, create a new empty (default) instance of the object and return it
        (without saving it - you have to do that yourself).

        Raises:
            IntegrityError: if there are more than one objects saved in the databases.
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()
        except MultipleObjectsReturned as e:
            raise IntegrityError(
                f"There are more than one instances of {cls.__name__} saved in the database"
            )


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


class AbstractSettings(SingletonModel):
    """Represents the settings of the application.

    This model is meant to be subclassed by your application.
    Please add application specific settings as needed to this model.
    """

    class Meta:
        abstract = True
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

    site_name = models.CharField(max_length=100, default="", blank=True)
    site_title = models.CharField(max_length=100, default="", blank=True)
    site_description = models.TextField(
        default="",
        blank=True,
        help_text=_("Text to display as site description. Supports Markdown."),
    )
    maintenance_mode = models.BooleanField(default=False)
    maintenance_title = models.CharField(max_length=100, default="", blank=True)
    maintenance_content = models.TextField(
        default="",
        blank=True,
        help_text=_("Text to display on the maintenance page. Supports Markdown."),
    )
    maintenance_mode_image = models.ImageField(
        blank=True, null=True, upload_to="site-images"
    )

    def __str__(self):
        return _("Settings")

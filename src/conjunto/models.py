from django.core.exceptions import MultipleObjectsReturned
from django.db import models, IntegrityError
from django.utils import timezone
from versionfield import VersionField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


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


class Content(models.Model):
    """Represents generic content.

    This class is an abstract base class that provides common fields and methods for
    all page subclasses.
    """

    class Meta:
        abstract = True

    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class VersionedPageManager(models.Manager):
    """Model manager that provides a method for getting the latest version of a page."""

    def get_latest_version(self):
        """Get the latest version of a page.

        Returns:
            The latest version of a page.
        """
        return self.get_queryset().order_by("-version").first()


class VersionedPage(Content):
    """Represents a generic page with versioning.

    This class is an abstract base class that provides common fields and methods for
    all page subclasses.
    """

    class Meta:
        abstract = True

    objects = VersionedPageManager()
    # versions must be unique within one page type.
    version = VersionField(default="1.0.0", unique=True)

    def __str__(self):
        return f"{self.title} (v{self.version})"


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


class Vendor(SingletonModel):
    """The vendor that is responsible for this appliance."""

    # TODO find an easy way to deploy data in Vendor model
    # maybe in a preferences.toml file?

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    phone = PhoneNumberField()
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class CreatedModifiedModel(models.Model):
    """A simple mixin for model classes that need to have created/modified fields."""

    created = models.DateTimeField(_("Created"), editable=False, default=timezone.now)
    modified = AutoDateTimeField(_("Modified"), default=timezone.now)

    class Meta:
        abstract = True

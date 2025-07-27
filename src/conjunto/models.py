from typing import Self

from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext
from phonenumber_field.modelfields import PhoneNumberField


# thanks to https://stackoverflow.com/questions/49735906/how-to-implement-singleton-in-django/49736970#49736970
class SingletonModel(models.Model):
    """Singleton Django Model.

    Allow only one instance of the model to be created.
    To get the instance of the model, use `<YourModel>.get_instance()`.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Save object to the database.

        Raises:
            IntegrityError: if there is already another instance in the database.
        """

        # If '_aggressive' attribute is set, remove all other entries if there are any.
        # if self._aggressive:
        #     self.__class__.objects.exclude(id=self.id).delete()
        if not self.pk:
            pk = self.get_instance().pk
            self.pk = self.get_instance().pk
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls) -> Self:
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


class AbstractSettings(models.Model):
    """Represents the settings of the application.

    This model is meant to be subclassed by your application.
    Please add application specific settings as needed to this model.
    """

    class Meta:
        abstract = True
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

    # if site == null, it is assumed that the settings are "global" settings.
    # there is only ONE settings model allowed per site
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="app_settings",
        blank=True,
        null=True,
    )
    # General site settings
    site_name = models.CharField(max_length=100, default="", blank=True)
    site_title = models.CharField(max_length=100, default="", blank=True)
    site_description = models.TextField(
        default="",
        blank=True,
        help_text=_("Text to display as site description. Supports Markdown."),
    )
    # Maintenance mode settings
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
        if not self.id:
            return gettext("Empty settings")
        if self.site is None:
            return gettext("Global settings")
        else:
            return gettext("Settings for {site}").format(site=self.site)

    def save(self, *args, **kwargs):
        """make sure no other settings exist with site == None"""
        if self.site is None:
            site = self._meta.model.objects.filter(site=None)
            if self.id:
                site = site.exclude(id=self.id)
            if site.exists():
                raise ValueError(
                    gettext(
                        "Cannot save another settings model without a site. There can "
                        "only be one global settings instance."
                    )
                )
        super().save(*args, **kwargs)


class Vendor(SingletonModel):
    """The vendor that is responsible for this appliance."""

    # TODO find an easy way to deploy data in Vendor model
    # maybe in a preferences.toml file?

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

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

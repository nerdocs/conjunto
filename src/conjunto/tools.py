import locale
import secrets
import string
import subprocess

from django.conf import settings
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

import logging

logger = logging.getLogger(__name__)


def str_to_bool(bool_str: str) -> bool:
    """returns True if bool_str is "true", else False."""
    return bool_str.lower() == "true"


def snake_case2spaces(value: str | None):
    """Converts a snake_case string to spaces."""
    value = value or ""
    return value.replace("_", " ")


def spaces2snake_case(value: str | None):
    """Converts a space separated string to snake_case."""
    value = value or ""
    return value.lower().strip().replace(" ", "_")


def camel_case2snake(camel_str: str | None, separator="_"):
    """Converts a CamelCase string to snake_case."""
    if camel_str is None:
        camel_str = ""
    snake_str = ""
    for index, char in enumerate(camel_str):
        if char.islower() or index == 0:
            snake_str += char.lower()
        else:
            snake_str += f"{separator}{char.lower()}"
    return snake_str


def country_code_from_locale(loc: tuple[str, str] | str) -> str:
    """Extracts an (uppercase) country code from a locale"""
    language, country_code, encoding = _split_locale(loc)
    return country_code.upper()


def country_name_from_code(iso3166_code: str) -> str:
    """Returns the country name from a ISO 3166 Alpha2 country code."""

    # TODO: this assumes that LANGUAGES is defined in settings.py
    for code, language in settings.LANGUAGES:
        # if code is in xx-xx format, use the first part only
        if "-" in code:
            code = code.split("-", 1)[0]
        if code == iso3166_code:
            return language
    else:
        return f"{iso3166_code} ({_('not supported')})"


def _split_locale(loc: tuple[str, str] | str) -> tuple[str, str, str]:
    """returns language, country_code, encoding from a locale string."""
    if isinstance(loc, str):
        loc = locale.normalize(loc)
        if "." in loc:
            locale_name, encoding = loc.split(".")
        else:
            locale_name = loc
            encoding = ""
    else:
        locale_name, encoding = loc
    # here we can be sure that loc is in the format "de_AT.UTF8"
    if "_" in locale_name:
        language, country_code = locale_name.split("_")
    else:
        language, country_code = locale_name, ""
    return language, country_code, encoding


def language_from_locale(loc: tuple[str, str] | str) -> str:
    """Extracts a language code from a locale"""
    language, country_code, encoding = _split_locale(loc)
    return language


def get_system_locales(strip_c: bool = True) -> list[str]:
    """Finds locales installed on a POSIX system and returns a list.

    Params:
        strip_c: if True(default), remove C.* and POSIX from result
    """
    # https://stackoverflow.com/a/54787951/818131

    out = subprocess.run(["locale", "-a"], stdout=subprocess.PIPE).stdout
    try:
        res = out.decode("utf-8")
    except UnicodeDecodeError:
        res = out.decode("latin-1")
    locales = res.rstrip("\n").splitlines()
    if strip_c:
        locales = [
            line for line in locales if not line.startswith("C") and not line == "POSIX"
        ]
    return locales


def create_groups_permissions(
    groups_permissions: dict[str, dict[Model | str, list[str]]]
):
    """Creates groups and their permissions defined in given `groups_permissions`
    automatically.

    Attributes:
         groups_permissions: a dict, see also [PluginAppConfig.groups_permissions]


    """
    # Based upon the work here: https://newbedev.com/programmatically-create-a-django-group-with-permissions
    from django.apps import apps
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    for group_name in groups_permissions:
        # Get or create group (even if there are no permissions
        # to save in the dict)
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            group.save()

        # Loop models in group
        for model in groups_permissions[group_name]:
            # if model_class is written as dotted str, convert it to class
            if isinstance(model, str):
                model_class = apps.get_model(model)
            else:
                model_class = model

            # Loop permissions in group/model

            for perm_name in groups_permissions[group_name][model]:
                # Generate permission name as Django would generate it
                codename = f"{perm_name}_{model_class._meta.model_name}"

                try:
                    # Find permission object and add to group
                    content_type = ContentType.objects.get(
                        app_label=model_class._meta.app_label,
                        model=model_class._meta.model_name.lower(),
                    )
                    perm = Permission.objects.get(
                        content_type=content_type,
                        codename=codename,
                    )
                    group.permissions.add(perm)
                    logger.info(
                        f"  Adding permission '{codename}' to group '{group.name}'"
                    )
                except Permission.DoesNotExist:
                    logger.critical(f"  ERROR: Permission '{codename}' not found.")


def generate_password(length=12, human_usable=False, with_punctuation=True) -> str:
    min_length = getattr(settings, "PASSWORD_MIN_LENGTH", 8)
    if not isinstance(length, int) or length < min_length:
        raise ValueError(f"password must have positive length > {min_length}")
    characters = string.ascii_letters + string.digits
    if human_usable:
        if with_punctuation:
            # only use punctuation that is safe for humans to read and write,
            # omit chars like `'
            # characters += r"""!"#$%&()*+-./=?@[]_{|}~"""
            characters += r"""!#$%&()*+-./=?@"""
            # remove characters that can be mixed easily with others when printed in the
            # wrong font, like O/0 or i/l/1
            # This reduces security a bit, but let's face it: Users tend to use the
            # name of their children as passwords, so we don't need to worry about that.
            # Using a strong password with slightly reduced complexity is a good
            # trade-off to human-generated passwords which tend to be very bad.
        characters = characters.replace("O", "")
        characters = characters.replace("o", "")
        characters = characters.replace("0", "")
        characters = characters.replace("l", "")
        characters = characters.replace("i", "")
        characters = characters.replace("1", "")
    else:
        if with_punctuation:
            characters += string.punctuation
    characters = characters.replace("\\", "")
    return "".join(secrets.choice(characters) for _ in range(length))

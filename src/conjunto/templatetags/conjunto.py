from crispy_forms.exceptions import CrispyError
from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from django.forms import boundfield
from django.template.defaultfilters import stringfilter
from django.template.loader import get_template
from django.templatetags.static import static
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag(takes_context=True)
def site_title(context) -> str:
    # Get the current site
    current_site = Site.objects.get_current(context.request)
    return current_site.name if current_site else ""


@register.simple_tag
def conjunto_css() -> str:
    css = [
        "conjunto/css/tabler.min.css",
        "conjunto/css/tabler-icons.css",
        "conjunto/css/dropzone.min.css",
        "conjunto/css/conjunto.css",
    ]

    result = ""
    for css_file in css:
        result += f"<link rel='stylesheet' href='{static(css_file)}'>\n"
    return mark_safe(result)


@register.simple_tag
def conjunto_js_scripts() -> str:
    js = [
        # "conjunto/js/alpine.min.js",
        # "conjunto/js/bootstrap.bundle.min.js",
        "conjunto/js/litepicker.js",
        "conjunto/js/tabler.js",
        "conjunto/js/Sortable.min.js",
        "conjunto/js/conjunto.js",
        "conjunto/js/dropzone.min.js",
        "conjunto/js/fslightbox.js",
        "conjunto/js/chart.min.js",
    ]
    result = ""
    for js_file in js:
        result += (
            "<script type='application/javascript' "
            f"src='{static(js_file)}' defer></script>\n"
        )
    return mark_safe(result)


@register.simple_tag(takes_context=True)
def render_element(context, element, **kwargs):
    """
    Renders a plugin element.

    Examples:
        ```django
        {% render_element my_element %}
        ```
        You can override (existing) attributes from within the template:
        ```django
        {% render_element my_element title="Settings" %}
        ```
    """
    return mark_safe(
        element.__class__.as_view(**kwargs)(context.request).render().content.decode()
    )


@register.filter
def is_image(file) -> bool:
    """Returns True if the file is an image, False otherwise.

    This ATM works just by determining the file extension.
    # TODO: maybe use PIL for this purpose - CAVE speed.
    """
    return isinstance(file, File) and file.name.split(".")[-1] in [
        "png",
        "jpg",
        "jpeg",
        "gif",
    ]


@register.filter(name="display_only")
def as_crispy_display(field, label_class="", field_class=""):
    """
    Renders a form field like a django-crispy-forms field, but read-only, without the input field.

        {% load crispy_forms_tags %}
        {{ form.field|as_crispy_display }}
    """
    if not isinstance(field, boundfield.BoundField) and settings.DEBUG:
        raise CrispyError(
            "|as_crispy_display got passed an invalid or inexistent " f"field: {field}"
        )

    attributes = {
        "field": field,
        "form_show_errors": True,
        "form_show_labels": True,
        "label_class": label_class,
        "field_class": field_class,
    }

    attributes["field"].field.disabled = True
    return get_template("conjunto/widgets/field_display.html").render(attributes)


@register.filter
@stringfilter
def trim(value):
    return value.strip()

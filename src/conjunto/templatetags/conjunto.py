from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django_htmx.jinja import django_htmx_script

register = template.Library()


@register.simple_tag
def conjunto_css_scripts() -> str:
    css = [
        "conjunto/css/tabler.min.css",
        "conjunto/css/tabler-icons.css",
        "conjunto/css/dropzone.min.css",
        "conjunto/css/conjunto.css",
    ]

    result = django_htmx_script()
    for css_file in css:
        result += f"<link rel='stylesheet' href='{static(css_file)}'>\n"
    return mark_safe(result)


@register.simple_tag
def conjunto_js_scripts() -> str:
    js = [
        "conjunto/js/alpine.min.js",
        # "conjunto/js/bootstrap.bundle.min.js",
        "conjunto/js/htmx/htmx.js",
        "conjunto/js/htmx/ext/ws.js",
        "conjunto/js/htmx/ext/debug.js",
        "conjunto/js/litepicker.js",
        "conjunto/js/tabler.js",
        "conjunto/js/Sortable.min.js",
        "conjunto/js/conjunto.js",
        "conjunto/js/toasts.js",
        "conjunto/js/dropzone.min.js",
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
    """Returns True if the file is an image, False otherwise

    This ATM works just by determining the file extension.
    # TODO: maybe use PIL for this purpose - CAVE speed.
    """
    return file.name.split(".")[-1] in ["png", "jpg", "jpeg", "gif"]

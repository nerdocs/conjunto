from django import template
from django.http import HttpRequest
from django.middleware.cache import UpdateCacheMiddleware
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django_htmx.jinja import django_htmx_script

register = template.Library()


@register.simple_tag
def conjunto_css_scripts() -> str:
    css = [
        # "conjunto/css/bootstrap.min.css",
        "conjunto/css/tabler.min.css",
        "conjunto/css/tabler-icons.css",
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
    return mark_safe(
        element.__class__.as_view()(context.request).render().content.decode()
    )
    # ctx["form"] = element.get_form()
    # return render_to_string(element.template_name, ctx)

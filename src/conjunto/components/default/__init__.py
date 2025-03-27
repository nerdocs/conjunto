from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from sourcetypes import django_html, javascript

from conjunto.api.interfaces import IElementMixin
from tetra import Component, BasicComponent, public
from conjunto.tools import snake_case2spaces
from django.contrib import messages


class Alert(BasicComponent):
    title: str = ""
    icon: str = None
    text: str = None
    message_level: int = messages.INFO
    dismissible: bool = False

    def load(self, icon=None, dismissible=False, level=messages.INFO, *args, **kwargs):
        self.icon = icon
        self.dismissible = dismissible
        self.message_level = level
        self.level_tag = messages.DEFAULT_TAGS[self.level]

    # language=html
    template: django_html = """
    <div class="alert alert-{{message_level}}{% if dismissible %} alert-dismissible
    {% endif %}" role="alert">
      <div class="d-flex">
        {% if icon %}
          <div>
          <i class='ti ti-{{icon}}'></i>
          </div>
        {% endif %}
        <div>
          <h4 class="alert-title">{{title}}</h4>
          {% if text %}<div class="text-secondary">{{text}}</div>{% endif %}
        </div>
      </div>
      {% if dismissible %}
      <a class="btn-close" data-bs-dismiss="alert" aria-label="close"></a>
      {% endif %}
    </div>
    """


class DataGrid(BasicComponent):
    """
    The `DataGrid` class is a component that generates a data grid for displaying data
     in a tabular format.

    It automatically determines all regular model fields and shows their translated
    title. It also detects properties/getters instead of fields, the component tries to
    find out a proper name as title here by creating a capitalized version of the
    property name and translating it into the locale language. However, you have to provide
    a proper translation string for your property name in your .po file manually.

    > **Note**
    > To keep Django's `makemessages` from commenting out these "unused" translations,
    > just add an unused `_("...")` string anywhere into your method.
    > E.g. when your property is named "display_name()", just add a `_("Display name")`
    > anywhere into this method block. This keeps Django from garbage collecting this
    > translation.

    Attributes:
        object: the Django model object to display
        fields: a comma separated list of field names to display

    Example usage:
    ```django
    {% #datagrid object=request.user fields="first_name,last_name,email" %}
    ```
    """

    object = None
    fields: list = []

    def load(self, object, fields: str, *args, **kwargs) -> None:
        """Renders fields of given object in a datagrid-usable form."""
        self.object = object
        field_name_list: str = fields
        fields = []
        for field_name in field_name_list.split(","):
            field_name = field_name.strip()
            field = {}
            try:
                field["title"] = self.object._meta.get_field(field_name).verbose_name
            except FieldDoesNotExist:
                # You have to add a translation string manually to your project
                # for this to work. @property display_name() -> "Display name"
                field["title"] = _(capfirst(snake_case2spaces(field_name)))

            # check if there are TextChoices or IntegerChoices to map to
            if hasattr(self.object, f"get_{field_name}_display"):
                field["content"] = getattr(self.object, f"get_{field_name}_display")
            else:
                field["content"] = getattr(self.object, field_name) or "-"
            fields.append(field)

    # language=html
    template: django_html = """
    <div class="datagrid">
        {% for field in fields %}
            <div class="datagrid-item mb-2">
              <div class="datagrid-title">{{ field.title }}</div>
              <div class="datagrid-content">
                {% if field.content.file %}
                    <img src="{{ field.content.url }}" alt="{{ field.content }}"/>
                {% else %}
                  {{ field.content }}
                {% endif %}
              </div>
            </div>
        {% endfor %}
    </div>
    """


class Accordion(BasicComponent):
    """Simple Accordion with a list of items.

    Attributes:
        items: list of dictionaries with keys 'title' and 'text':
            `{'title': 'Item 1', 'text': 'Some content for Item 1' }`
        id: optional id for the accordion, if not provided, a default one will be used
    """

    items: dict = {}

    def load(self, id: str = None, items: dict = None, *args, **kwargs):
        if not id:
            id = "accordion-component"
        self.id = id
        items = items

    # language=html
    template: django_html = """
    <div class="accordion"
    {% ... id=id|if:id|else:"accordion-component" %}>
      {% for item in items %}
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-1">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
           data-bs-target="#collapse-{{forloop.counter}}" aria-expanded="true">
              {{item.title }}
            </button>
          </h2>
          <div id="collapse-{{forloop.counter}}" 
                class="accordion-collapse collapse show" 
                data-bs-parent="#{{id}}" 
                style="">
            <div class="accordion-body pt-0">
              {{ item.text }}
            </div>
          </div>
        </div>
      {% endfor %}
    </div>
    """


class DataGridItemBase(BasicComponent):
    """Tetra base component for datagrid functionality."""

    __abstract__ = True
    title: str = ""
    content: str = ""
    object: models.Model = None

    def load(self, object: models.Model, field_name: str, *args, **kwargs):
        if not object:
            return
        # assert object, f"No object assigned to {self.__class__.__name__}"
        self.object = object
        field_name = field_name.strip()
        assert field_name, f"No field_name assigned to {self.__class__.__name__}"
        try:
            self.title = self.object._meta.get_field(field_name).verbose_name
        except FieldDoesNotExist:
            # You have to add a translation string manually to your project
            # for this to work.
            self.title = _(capfirst(snake_case2spaces(field_name)))

        # check if there are TextChoices or IntegerChoices to map to
        if hasattr(self.object, f"get_{field_name}_display"):
            self.content = getattr(self.object, f"get_{field_name}_display")
        else:
            self.content = getattr(self.object, field_name) or "-"


class DataGridItem(DataGridItemBase):
    """Item in a data grid with a title and a content.

    Attributes:
        object: The Django model instance to display
        field: The name of the field to display. The title will be autogenerated
            from the field's verbose_name.
    Usage:
    ```django
    {% @ DataGridItem object=request.user field="last_name" / %}

    {% @ DataGridItem object=request.user field="last_name" %}
      Mr/Mrs. {{ object.last_name }}
    {% /@ %}
    ```
    """

    # language=html
    template: django_html = """
    <div {% ... attrs %} class="datagrid-item mb-2">
      <div class="datagrid-title">{{ title }}</div>
      <div class="datagrid-content">
      {% block default %}
          {% if content and content.file %}
            <img src="{{ content.url }}" alt="{{ content }}"/>
          {% else %}
                {{ content }}
          {% endif %}
      {% endblock %}
      </div>
    </div>
    """


class DataGridFile(DataGridItemBase):
    # language=html
    template: django_html = """
    {% load conjunto %}
    <div {% ... attrs %} class="datagrid-item mb-2">
      {% csrf_token %}
      <div class="datagrid-title">{{ title }}</div>
      <div class="datagrid-content">
        <p>
          {% if content|is_image %}
            {% @ LightboxImage url=content.url /%}
          {% elif content %}
            <a href="{{ content.url }}">
              <div class="card card-link">
                <div class="card-body d-flex justify-content-center">
                  <i class="ti ti-file-type-pdf fs-1"></i>
                </div>
              </div>
            </a>
          {% endif %}
        </p>
        {% block default %}{% endblock %}
      </div>
    </div>
    """


class LightboxImage(BasicComponent):
    """
    Lightbox image link component.

    Add images to your page with this component. They will be automatically found by the
    FullScreenLightbox plugin and shown in a lightbox when clicked.
    """

    url: str = ""
    alt: str = ""

    def load(self, url: str, alt: str = "", *args, **kwargs) -> None:
        self.url = url
        self.alt = alt

    # language=html
    template: django_html = """
    <a data-fslightbox="gallery" href="{{ url }}">
      <img src="{{ url }}" alt="{{ alt|truncatechars:25 }}"/>
    </a>
    """


# class FormModal(Modal):
#     def load(
#         self,
#         id: str,
#         title: str = "",
#         static_backdrop: bool = False,
#         success_event: str = "",
#         **kwargs,
#     ):
#         self.id = id
#         self.title = title
#         self.static_backdrop = static_backdrop
#         self.success_event = success_event
#         super().load(**kwargs)
#
#     @public
#     def submit(self) -> None:
#         """If the submit button was clicked, dispatch the success_event."""
#         if self.success_event:
#             self.client._dispatch(self.success_event)
#
#     def form_valid(self):
#         pass
#
#     def form_invalid(self):
#         pass


class ModalButton(BasicComponent):
    """Basically a button that opens a modal dialog.

    Attributes:
        target (str): The id of the modal to open.

    The default block is the content of the button.
    """

    target_id: str = ""

    def load(self, target: str = None, *args, **kwargs):
        # take target with and without leading "#"
        if target and target.startswith("#"):
            self.target_id = target[1:]
        else:
            self.target_id = target

    # language=html
    template: django_html = """
    <!-- ModalButton -->
    <button {% ... attrs class="btn" %}
        data-bs-toggle="modal" 
        data-bs-target="#{{target_id}}">
        {% block default %}{% endblock %}
    </button>
    """


class List(Component):
    """A flexible component to display a Tabler.io list.

    Attributes:
        hoverable: whether the list items are hoverable or not.

    Example:
        ```django
        {% list hoverable=True %}
          {% for item in items %}
            {% @ ListItem title=item.title / %}
          {% endfor %}
        {% endlist %}
        ```
    """

    hoverable: bool = False

    # language=html
    template: django_html = """
    <div class="list-group{% if hoverable %} list-group-hoverable{% endif %}">
      {% block default %}
      {% endblock %}
    </div>
"""


class ListItem(Component):
    """A flexible component to display a Tabler.io list item.

    Attributes:
            title (str): The title of the list item.
            subtitle (str): The subtitle of the list item. Optional.
            picture: The picture of the list item. Optional.
            badge_color (str): The color of a badge left of the list item. Optional.
            active (bool): whether the list item is active or not. Defaults to False
            url (str): The URL the title links to. Optional.

    Example:
        ```django
        {% @ ListItem
            title=item.title
            active=False
            badge_color="red"
        %}
        ```
    """

    title = ""
    # template_name = "conjunto/components/list_item.html"

    def load(
        self,
        title: str = None,
        subtitle: str = None,
        picture: str = None,
        badge_color: str = None,
        active: bool = False,
        url: str = None,
        *args,
        **kwargs,
    ):
        self.title = title
        self.subtitle = subtitle
        self.picture = picture
        self.badge_color = badge_color
        self.active = active
        self.url = url

    # language=html
    template: django_html = """
    <div class="list-group-item{% if active %} active{% endif %}">
      <div class="row align-items-center">

        {% if badge_color %}
          <div class="col-auto"><span class="badge bg-{{ badge_color }}"></span></div>
        {% endif %}

        {% if picture %}
          <div class="col-auto">
            {% if url %}<a href="{{ url }}">{% endif %}
            <span class="avatar" {# style="..." #} }></span>
            {% if url %}</a>{% endif %}
          </div>
        {% endif %}

        <div class="col text-truncate">
          {% if url %}<a href="{{ url }}" class="text-reset d-block">
          {% else %}<div class="text-reset d-block">{% endif %}
          {{ title }}
          {% if not url %}</div>{% else %}</a>{% endif %}

          {% if subtitle %}
            <div class="d-block text-muted text-truncate mt-n1">{{ subtitle }}</div>
          {% elif blocks.subtitle %}
            <div class="d-block text-muted text-truncate mt-n1">
            {% block subtitle %}{% endblock %}</div>
          {% endif %}
        </div>

        {% if blocks.actions %}
          <div class="col-auto">
            {% block actions %}{% endblock %}
          </div>
        {% endif %}

      </div>
    </div>
    """


class HtmxLinkElement(BasicComponent):
    """
    HTMX enabled base element.

    This could be a <button> (default), a <div> or a <a> tag, resulting in a visual
    button.

    Attributes:
        dialog: whether the button should open a dialog or not.
        htmx: whether the button should open a HTMX request or not. If dialog is
            True, HTMX is used obligatory. Defaults to False. If only set without value,
            defaults to "get". If set to "post", a post request is used.
        target: the HTMX target element of the button, if HTMX/dialog is used.
        url: the URL to call a get/post request when using HTMX.
        icon: the icon of the button. Optional.
    """

    __abstract__ = True
    # language=html
    template: django_html = """<{{ tag }} {% ... attrs class=default_class %}
  {% if htmx %}
    hx-{{ htmx|lower }}="{{ url }}"{% if dialog %} hx-target="#{{ dialog }}"{% elif 
    target %} hx-target="{{ target }}"{% endif %}{% if select %} hx-select="{{ select }}"{% endif %}
    hx-swap="innerHTML"
    {% if tag == "a" %}href="#"{% endif %}
  {% else %}
    {% if tag == "a" %}href="{{ url }}"{% endif %}
  {% endif %}
>
  {% if icon %}
    <i class="ti ti-{{ icon }} {{ icon_fs }}"></i>
  {% endif %}
  {% block default %}{% endblock %}
</{{ tag }}>"""

    tag: str = "div"
    default_class: str = ""
    icon: str = ""
    icon_fs: str = ""
    url: str = ""
    modal_id: str = ""
    target: str = ""

    def load(
        self,
        tag: str = "div",
        icon: str = "",
        url: str = "",
        *args,
        **kwargs,
    ):
        self.tag = tag
        klass = kwargs.pop("class", "")
        if "-sm" in klass or "-sm" in self.default_class:
            self.icon_fs = ""
        else:
            self.icon_fs = "fs-2"

        self.target = kwargs.pop("target", "")
        htmx = kwargs.pop("htmx", False)
        modal = kwargs.pop("modal", "")
        if modal and not htmx:
            self.dialog_id = ""
        if htmx is True:
            htmx = "get"
        self.default_class = (
            f"{self.default_class} {klass}" if klass else self.default_class
        )


class DisableMixin:  # FIXME: use Tetra
    """Component mixin that adds a disabled class attribute to the component

    It extracts a possible `disabled` attribute and adds it to the class list.
    So you could conveniently write a component like this:
    ```django
    {% #button disabled %}
    ```
    instead of:
    ```django
    {% #button class="disabled" %}
    ```
    It also adds the content of the disabled attribute into the template context, so
    you could react in other ways to it, like hiding the element completely.
    """

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        disabled = self.attributes.pop("disabled", None)
        if disabled:
            self.attributes["class"] = self.attributes.get("class", "")
            self.attributes["class"] += " disabled"
            context["disabled"] = disabled
        return context


class Link(HtmxLinkElement):
    tag = "a"


class Button(DisableMixin, HtmxLinkElement):
    """HTMX enabled button."""

    tag = "button"
    default_class = "btn"


#
#
# @default.register
# class ActionButton(Button):
#     """Action button, e.g. in a `card-actions` section"""
#
#     default_class = "btn btn-action"
#
#
# @default.register
# class ListGroupAction(Link):
#     """HTMX enabled list group action button"""
#
#     # FIXME: maybe hardcoded "text-secondary" here leads to problems, as
#     #   it will be merged with the attributes, which also could include
#     #   class="text-danger"
#     default_class = "list-group-item-actions text-secondary"
#
#     def get_context_data(self, **kwargs) -> dict:
#         context = super().get_context_data(**kwargs)
#         if "url" not in context:
#             raise AttributeError(f"{self.__class__.__name__} has no 'url' attribute.")
#         return context


class AbstractTabCard(BasicComponent):
    """Tab card component with a tab navigation and a tab content area.

    For actual usage, you have to subclass this component and set the "elements"
    attribute to a list of TabElement instances.
    """

    __abstract__ = True
    template_name = "conjunto/components/tab_card.html"
    elements: IElementMixin = None

    def load(self, elements, *args, **kwargs):
        self.elements = elements

    template = """FOO"""

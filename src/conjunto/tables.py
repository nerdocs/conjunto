from collections import OrderedDict

import django_tables2 as tables
from django.db.models import IntegerChoices
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from conjunto.htmx import HxActionButton, HxButton
from conjunto.menu import IActionButton
from conjunto.tools import camel_case2snake


class UpdateTableMixin:
    """A table mixin that that updates itself using HTMX when a javascript event is
    triggered.

    Arguments in Meta class:
        id: The id of the table that should be used as HTML id attribute.
        listen_events: A list of events that the table will listen to.
        update_url: the url to call to update the table.
    """

    class Meta:
        id: str = None
        listen_events: list[str] = []
        update_url: str = ""

    def __init__(self, id=None, listen_events=None, update_url=None, **kwargs):
        attrs = getattr(self.Meta, "attrs", {})
        self._update_url = update_url or getattr(self.Meta, "update_url", ".")

        # set id for table
        table_id = id or getattr(self.Meta, "id", None)
        if not table_id:
            table_id = camel_case2snake(self.__class__.__name__, separator="-")
        attrs["id"] = table_id

        if not listen_events:
            listen_events = getattr(self.Meta, "listen_events", None)
        if listen_events:
            attrs["hx-trigger"] = ", ".join([f"{e} from:body" for e in listen_events])
            attrs["hx-get"] = self._update_url
            attrs["hx-swap"] = "outerHTML"
            attrs["hx-target"] = f"#{table_id}"
            attrs["hx-select"] = f"#{table_id}"
            attrs["hx-disinherit"] = "*"

        super().__init__(attrs=attrs, **kwargs)


class ActionButtonsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(
            verbose_name=_("Actions"),
            empty_values=(),
            attrs={"td": {"class": "text-end"}, "th": {"class": "text-end"}},
            *args,
            **kwargs,
        )
        self.buttons: list[HxActionButton] = kwargs.pop("buttons", [])


class ActionButtonType(IntegerChoices):
    """Action buttons type, and their weights."""

    EDIT = 10
    DELETE = 20
    DELETE_WITH_CONFIRM = 21


class ActionButtonsTable(UpdateTableMixin, tables.Table):
    """A table mixin that provides an "actions" column for row actions.

    The table will update itself if a given event is triggered. Per default,
    the `actions` column is positioned at the end via Meta.sequence. However,
        if you use your own Meta.sequence, don't forget to add the "actions"
    column at the end.

    Arguments:
        record_view_name: View name for the model of the record,
            like `<app_name>:<model_name>`. This is used to determine the action URLs
            for the action buttons, and to create the listen events for the table.
        standard_buttons: List of standard action buttons to render. Change this if you
            e.g. want to use a DELETE_WITH_CONFIRM button instead of a DELETE button.
        action_buttons_menu: Menu name for IActionButtons that should be rendered
            additionally to the standard buttons.
    """

    actions = ActionButtonsColumn()

    class Meta:
        record_view_name: str = ""
        standard_buttons: list[ActionButtonType] = [
            ActionButtonType.EDIT,
            ActionButtonType.DELETE,
        ]
        action_buttons_menu = []

    def __init__(
        self,
        record_view_name: str = None,
        action_buttons_menu: list = None,
        standard_buttons: list[ActionButtonType] = None,
        listen_events=None,
        **kwargs,
    ):
        self._action_buttons = standard_buttons or getattr(
            self.Meta,
            "standard_buttons",
            [ActionButtonType.EDIT, ActionButtonType.DELETE],
        )

        # make sure that record_view_name was set
        self._record_view_name = record_view_name or getattr(
            self.Meta, "record_view_name", ""
        )
        if not self._record_view_name:
            raise AttributeError(
                f"{self.__class__.__name__}.Meta does not provide a "
                f"'record_view_name' attribute"
            )
        # get Meta.listen_events, if available
        if not listen_events:
            listen_events = getattr(self.Meta, "listen_events", [])
            # create a set of default CRUD events to listen on
            listen_events.append(f"{self._record_view_name}:created")
            if ActionButtonType.EDIT in self._action_buttons:
                listen_events.append(f"{self._record_view_name}:changed")
            if (
                ActionButtonType.DELETE in self._action_buttons
                or ActionButtonType.DELETE_WITH_CONFIRM in self._action_buttons
            ):
                listen_events.append(f"{self._record_view_name}:deleted")

        # set "actions" as last column if no sequence was provided in Meta class.
        # Make 100% sure that this is the case, even if other mixins
        # modified the sequence and removed "actions". The priority is as follows:
        # 1. sequence passed in as an argument
        # 2. sequence declared in ``Meta``
        # 3. sequence defaults to ``("...", "actions")``
        default_sequence = ("...", "actions")
        sequence = kwargs.get("sequence", ())
        if sequence:
            if "actions" not in sequence:
                sequence += ("actions",)
        else:
            sequence = getattr(self.Meta, "sequence", default_sequence)
            if "actions" not in sequence:
                sequence += ("actions",)

        super().__init__(sequence=sequence, listen_events=listen_events, **kwargs)

        self._button_classes = []
        # get IActionButtons classes, filtered by menu name
        # and cache them, if there is an action_buttons_menu attribute
        self._action_buttons_menu = action_buttons_menu or getattr(
            self.Meta, "action_buttons_menu", ""
        )
        if self._action_buttons_menu:
            for menu_button_class in IActionButton.filter(self._action_buttons_menu):
                if menu_button_class not in self._button_classes:
                    self._button_classes.append(menu_button_class)

    def render_actions(self, record):
        """sort all desired buttons (standard and IActionMenu generated) by weight, and render them."""
        content_dict: dict[int, str] = {}
        for ActionButtonClass in self._button_classes:
            # instantiate action buttons with request and record
            item: IActionButton = ActionButtonClass(self.request, record)
            button = HxActionButton(self.request, item, dialog=True)
            weight = item.weight
            if weight in content_dict:
                content_dict[weight] += button.render(record)
            else:
                content_dict[weight] = button.render(record)
            del item
        # then render the standard action buttons like edit/delete
        for typ in self._action_buttons:
            button = ""
            match typ:
                case ActionButtonType.EDIT:
                    button = HxButton(
                        url=reverse(
                            f"{self._record_view_name}:update", args=(record.id,)
                        ),
                        icon="pencil",
                        dialog=True,
                        css_class="btn btn-action",
                        method="get",
                        title=_("Edit {object}").format(
                            object=self.Meta.model.__name__
                        ),
                    ).render(pk=record.id)
                case ActionButtonType.DELETE:
                    button = HxButton(
                        url=reverse(
                            f"{self._record_view_name}:delete", args=(record.id,)
                        ),
                        icon="trash",
                        dialog=True,
                        css_class="btn btn-action text-danger",
                        method="post",
                        title=_("Delete {object}").format(
                            object=self.Meta.model._meta.verbose_name
                        ),
                    ).render(pk=record.id)
                case ActionButtonType.DELETE_WITH_CONFIRM:
                    button = HxButton(
                        url=reverse(
                            f"{self._record_view_name}:delete", args=(record.id,)
                        ),
                        icon="trash",
                        dialog=True,
                        css_class="btn btn-action",
                        method="get",
                        title=_("Delete {object} without confirmation").format(
                            object=_(self.Meta.model._meta.verbose_name)
                        ),
                    ).render(pk=record.id)
            if typ in content_dict:
                content_dict[typ] += button
            else:
                content_dict[typ] = button

        ordered_dict = OrderedDict(sorted(content_dict.items()))
        return format_html("".join(ordered_dict.values()))

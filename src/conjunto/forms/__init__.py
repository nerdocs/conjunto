import logging

from django import forms
from django.db.models import IntegerChoices

# FIXME: remove dynamic_forms, not needed with Tetra
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


# class DependencyFormMixin:
#     """A mixin that can be added to a Form, and allows dependent fields on that form.
#
#     Define a `Meta` class with two attributes:
#      `update_url`, which is the URL to update the form.
#      `field_dependencies`, which is a dict of fields {field_name: target} that are
#         dependent on other fields.
#
#     Your view must be capable of handling GET data which prepopulate the form fields.
#     # You can use the PrepopulateFormViewMixin for that.
#     """
#
#     class Meta:
#         # you can define your own Meta class in your inheriting model,
#         # just make sure that these two attributes are defined.
#         update_url: str = None
#
#         field_dependencies: dict[str, str] = {}
#         """dict of fields {field_name: target} that are dependent on other fields."""
#
#     def get_update_url(self):
#         """Returns the URL to update the form"""
#         return self.Meta.update_url
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         dependencies = self.Meta.field_dependencies
#         for field_name, target in dependencies.items():
#             self.fields[field_name].widget.attrs.update(
#                 {
#                     "hx-trigger": "change",
#                     "hx-get": self.get_update_url(),
#                     "hx-target": target,
#                     "hx-select": target,
#                     "hx-swap": "outerHTML",
#                     # explicitly pass the field name as param, so that it shows up in
#                     # the GET request
#                     "hx-params": field_name,
#                 }
#             )
#
#             # check if form has an "on_changed_<field_name>()" method
#             on_changed_method = getattr(self, f"on_changed_{field_name}")
#             if callable(on_changed_method):
#                 # if POST data were sent, take them first
#                 data = kwargs.get("data", None)
#                 if data is not None:
#                     value = data.get(field_name, None)
#                     if value is not None:
#                         on_changed_method(value)
#
#                 # and the field is in the GET params
#                 elif field_name in kwargs.get("initial", []) and hasattr(
#                     self, f"on_changed_{field_name}"
#                 ):
#                     on_changed_method(kwargs.get("initial")[field_name])
#                 else:
#                     # if no pre-populating, check if there is an instance field and
#                     # react to its value
#                     if hasattr(self, "instance") and hasattr(self.instance, field_name):
#                         value = getattr(self.instance, field_name)
#                         on_changed_method(value)


class ErrorLogMixin:
    """A mixin that can be added to a Form during development/debugging, so that it
    logs all form errors."""

    def add_error(self, field, error):
        if field:
            logger.info("Form error on field %s: %s", field, error)
        else:
            logger.info("Form error: %s", error)
        super().add_error(field, error)


# class DynamicHtmxFormMixin(DynamicFormMixin):
#     """
#     Mixin class for creating dynamic forms with HTMX.
#
#     This mixin extends the functionality of the DynamicFormMixin by adding htmx
#     attributes to the form fields that can be used for triggering dynamic updates.
#
#     Attributes:
#         context (dict[str, Any]): The context passed to the form from the view. This
#                 variable can be accessed within the form via `self.context`.
#         form_id (str): The id of the form. This is used to generate the id of the
#                 form, which is needed as HTMX target
#
#         Meta.trigger_fields: A dict with field names as keys that will trigger a
#                 dynamic update on a list of fields (the dict values) on a "change" event.
#         Meta.update_url: The URL to send the dynamic update request to.
#                 Defaults to current URL if not provided.
#         Meta.trigger: the event that triggers the update. Defaults to "change".
#
#     Raises:
#         AttributeError: If the `trigger_fields` attribute is not defined in `Meta`.
#     """
#
#     class Meta:
#         trigger_fields: list[str] = []
#         update_url: str = "."
#         trigger: str = "change"
#
#     def __init__(self, form_id, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.form_id = form_id
#
#         if not hasattr(self.Meta, "trigger_fields"):
#             raise AttributeError(
#                 f"{self.__class__.__name__}.Meta has no 'trigger_fields' attribute."
#             )
#
#         trigger = self.Meta.trigger if hasattr(self.Meta, "trigger") else "changed"
#         include_list = ",".join(
#             [
#                 f"[name={field}]"
#                 for field in self.fields
#                 if not self.fields[field].widget.is_hidden
#             ]
#         )
#         self.context["form_attrs"] = f"hx-include={include_list}"
#
#         for field_name in self.Meta.trigger_fields:
#             field = self.fields.get(field_name)
#             if field:
#                 field.widget.attrs.update(
#                     {
#                         "hx-trigger": trigger,
#                         "hx-post": self.get_update_url(),
#                         "hx-target": f"#{self.form_id}",
#                         "hx-select": f"#{self.form_id}",
#                         "hx-encoding": "multipart/form-data",  # allow file uploads
#                         "hx-vals": '{"_dynamic_reload": true}',
#                         # "hx-push-url": "true",
#                         "hx-swap": "outerHTML",
#                     }
#                 )
#
#         # # check if form has an "on_changed_<field_name>()" method
#         # on_changed_method = getattr(self, f"on_changed_{field_name}")
#         # if callable(on_changed_method):
#         #     # if POST data were sent, take them first
#         #     data = kwargs.get("data", None)
#         #     if data is not None:
#         #         value = data.get(field_name, None)
#         #         if value is not None:
#         #             on_changed_method(value)
#         #
#         #     # and the field is in the GET params
#         #     elif field_name in kwargs.get("initial", []) and hasattr(
#         #         self, f"on_changed_{field_name}"
#         #     ):
#         #         on_changed_method(kwargs.get("initial")[field_name])
#         #     else:
#         #         # if no pre-populating, check if there is an instance field and
#         #         # react to its value
#         #         if hasattr(self, "instance") and hasattr(self.instance, field_name):
#         #             value = getattr(self.instance, field_name)
#         #             on_changed_method(value)
#
#     def get_update_url(self):
#         if hasattr(self.Meta, "update_url"):
#             return self.Meta.update_url
#         else:
#             return "."
#
#     def fields_required(self, fields: str | list[str], msg: str = None) -> None:
#         """Helper method used for conditionally marking fields as required.
#
#         Args:
#             fields: A list of field names, or single field name.
#             msg: A custom error message. Defaults to "This field is required.".
#
#         Example usage:
#         ```python
#         def clean(self):
#             is_person = self.cleaned_data.get("is_person")
#
#             if is_person:
#                 self.field_required(["first_name", "last_name"])
#                 self.field_required("title", "A title is definitely required here.")
#                 self.field_required(["age", "size"], "You forgot this field.")
#             else:
#                 self.cleaned_data["first_name"] = ""
#                 self.cleaned_data["last_name"] = ""
#                 self.cleaned_data["title"] = ""
#
#             return self.cleaned_data
#         ```
#         Credits go to
#         https://www.fusionbox.com/blog/detail/creating-conditionally-required-fields-in-django-forms/577/
#         """
#         if type(fields) is str:
#             fields = [fields]
#         for field in fields:
#             if not self.cleaned_data.get(field, ""):
#                 msg = (
#                     forms.ValidationError(msg)
#                     if msg
#                     else forms.ValidationError(_("This field is required."))
#                 )
#                 self.add_error(field, msg)

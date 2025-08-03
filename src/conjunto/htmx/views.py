from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, CreateView, UpdateView, DetailView

from conjunto.api.interfaces import HtmxRequestMixin
from conjunto.http import HttpResponseEmpty
from conjunto.views import CrispyFormHelperMixin, DialogType, AutoPermissionsViewMixin


class SuccessEventMixin(HtmxRequestMixin):
    """A HTMX view mixin that always returns an empty response.

    Attributes:
        success_event: a Javascript event that is triggered on the client after
            the request is completed.

    Returns:
        A response with a "HX-Trigger" attribute which triggers a Javascript event
        on the client.

    If your view parents have a `post` method, that method is called, and it's response
    is reused and modified, so that the event is triggered on the client.

    If your view has no post method (TemplateView etc.), a HttpResponseEmpty is created.
    """

    success_event: str = ""

    def get_success_event(self):
        """Override this to return (e.g. generated) success event."""
        return self.success_event

    def dispatch(self, request, *args, **kwargs):
        """If POST request and response status is 200, trigger a Javascript event."""
        response = super().dispatch(request, *args, **kwargs)
        if (
            request.htmx
            and self.request.method == "POST"
            and self.get_success_event()
            and 200 <= response.status_code < 300
        ):
            trigger_client_event(response, self.get_success_event())

        return response


class HtmxFormViewMixin(SuccessEventMixin):
    """
    Mixin for a FormView that uses HTMX.

    If any of the parent views return a HttpResponseRedirect, it will be converted
    into a HttpResponseClientRedirect, so that HTMX does the redirection on the client.
    HTMX forms also accept an empty success_url, if a success_event is present,
    e.g. could a form reload itself after a button was pressed. There is not always
    a need to redirect.

    In case of a normal request origin (enforce_htmx must be False then), the original
    HttpResponse(Redirect?) is kept as is.
    """

    def get_success_url(self):
        """Return success_url, even if it is empty.

        FormViews raise an Exception if success_url is empty. We need to capture that.
        """
        return getattr(self, "success_url", "")

    def form_valid(self, form):
        """Trigger a Javascript event on the client."""
        response = super().form_valid(form)
        # if coming from a HTMX request, and there is a success_url, we need to redirect
        # to it's URL using HTMX. So we replace the HttpResponseRedirect with a
        # `HX-Trigger` version.
        # FIXME: this shouldn't be in form_valid(), as it interferes with saving of
        #  form data. Should be in post() or dispatch().
        #  if e.g. a child view decides not to call super().form_valid (which is ok!)
        #  this code isn't called - but it should be.

        success_url = self.get_success_url()
        if self.request.htmx and isinstance(response, HttpResponseRedirect):
            # if neither success_url nor success_event is set, raise original Exception.
            if not success_url and not self.get_success_event():
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a "
                    "success_url, or a success_event."
                )

            if success_url:
                response = HttpResponseClientRedirect(success_url)
            else:
                response = HttpResponseEmpty()

        # in case of a normal request origin, the original HttpResponse(Redirect?) is
        # kept as is.
        return response


class HtmxDeleteView(HtmxFormViewMixin, DeleteView):
    """Enhanced DeleteView that per default returns an empty HttpResponse.

    Uses the `success_url` attribute of the view to get the URL to redirect
    to via HTMX after successful deletion. If `success_url` is None, no redirection is
    made.
    """

    # most of the time, you will use POST, or a modal dialog for deleting,
    # so use this as default template, override as needed.
    template_name = "conjunto/modal_confirm_delete.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.delete()
        return response


class ModalFormViewMixin(HtmxFormViewMixin, CrispyFormHelperMixin):
    """Mixin for FormViews that should live in a modal.

    It relies on crispy-forms intensively, and already provides a form
    helper instance attribute you can use.

    In many cases, you need no template, as this mixin provides a generic one with
    a customizable title. The form is generated using crispy-forms.
    If you want to customize if further, then, extend "conjunto/modal_form.html".
    This template uses a ``header`` with a ``title`` block, a ``body``,
    and a ``footer`` block to override, for your modal dialog. In the
    footer, there is always a "Cancel" button, and as default, a "Save"
    button, You can fully override the buttons using the "footer" block.

    When the modal pops up, the focus is set to the first visible input
    element.

    You can customize the content of the "Save" button by changing the `button_content`
    attribute to another string.

    If the form is saved successfully, it returns an empty HttpResponse(204)
    and emits the event specified in ``success_event`` on the client,
    so that it can reload changed content.

    Attributes:
        modal_title: the title of the modal form
        autofocus_field: the field that gets the autofocus when the modal is shown
        button_content: the content of the 'Save' button. Default: _("Save")
        dialog_type: the type of the dialog: INFO, DELETE, CREATE, UPDATE
        autocomplete: if True, let the browser autocomplete the form. Default: True
    """

    template_name = "conjunto/modal_form.html"
    """The default template name for the modal form. This template provides
    a simple modal form. You can extend it in your own templates too."""

    modal_title: str = ""

    autofocus_field = ""  # FIXME: fix autofocus field

    autocomplete = True

    button_content = _("Save")

    dialog_type: DialogType = DialogType.NOTSET

    def get_modal_title(self) -> str:
        """Returns a string that is used as title of the modal."""
        return self.modal_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        icon = ""
        submit_btn_css_class = ""
        form_attrs = {}
        if self.autocomplete:
            form_attrs["autocomplete"] = "off"
        match self.dialog_type:
            case DialogType.DELETE:
                icon = "trash"
                submit_btn_css_class = "danger danger"
            case DialogType.INFO:
                icon = "info-circle"
                submit_btn_css_class = "info info"
        context.update(
            {
                "modal_title": self.get_modal_title(),
                "button_content": self.button_content,
                "dialog_type": self.dialog_type,
                "DialogType": DialogType,
                "icon": icon,
                "submit_button_css_class": submit_btn_css_class or "primary",
                "form_attrs": " ".join(
                    [f"{key}={value}" for key, value in form_attrs.items()]
                ),
            }
        )
        return context


class _ModalModelViewMixin(AutoPermissionsViewMixin, ModalFormViewMixin):
    """Internal mixin for Create/Update/DeleteViews (with permissions) that lives in a
    Modal.

    You shouldn't have to use this directly.

    It automatically generates the Modal title. Override as needed.

    Attributes:
        _modal_title_template: the title of the modal dialog,
            with an `{instance}` placeholder.
    """

    _modal_title_template = None  # "Edit/Create '{instance}'"

    def get_modal_title(self) -> str:
        if self.modal_title:
            return self.modal_title
        if self._modal_title_template:
            return self._modal_title_template.format(
                instance=self.model._meta.verbose_name
            )
        return ""


class ModalCreateView(_ModalModelViewMixin, CreateView):
    """Convenience CreateView (with permissions) that lives in a Modal.

    It automatically generates the Modal title and sets the "create_<model>" permission
    of the given model as necessary permission. Override as needed.
    """

    _permissions_verb = "add"
    _modal_title_template = _("Create '{instance}'")


class ModalUpdateView(_ModalModelViewMixin, UpdateView):
    """Convenience UpdateView (with permissions) that lives in a Modal.

    It automatically generates the Modal title and sets the "change_<model>" permission
    of the given model as necessary permission. Override as needed.
    """

    button_content = _("Save")
    dialog_type = DialogType.UPDATE
    _permissions_verb = "change"
    _modal_title_template = _("Edit '{instance}'")


class ModalDetailView(_ModalModelViewMixin, DetailView):
    """Convenience DetailView (with permissions) that lives in a Modal."""

    dialog_type = DialogType.NOTSET
    _permissions_verb = "view"
    _modal_title_template = None


class ModalDeleteView(_ModalModelViewMixin, DeleteView):
    """Convenience UpdateView (with permissions) that lives in a Modal.

    It automatically generates the Modal title and sets the "change_<model>" permission
    of the given model as necessary permission. Override as needed.
    """

    button_content = _("Delete")
    template_name = "conjunto/modal_confirm_delete.html"
    dialog_type = DialogType.DELETE
    _permissions_verb = "delete"
    _modal_title_template = _("Delete '{instance}'")

import uuid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import DeleteView, FormView, DetailView

from conjunto.models import PrivacyPage, LicensePage
from conjunto.tools import camel_case2snake


class HtmxResponseMixin:
    """View Mixin to add HTMX functionality.

    optionally checks if request originates from an HTMX request.

    Attributes:
        enforce_htmx: if True, all requests that do not come from a HTMX
            component are blocked
        success_event: a Javascript event that is triggered on the client after
            the request is completed.

    Raises:
        PermissionDenied: if enforce_htmx==True and request origins from a
            non-HTMX caller.
    """

    enforce_htmx: bool = True

    def dispatch(self, request, *args, **kwargs):
        if self.enforce_htmx and not self.request.htmx:
            raise PermissionDenied(
                f"Permission denied: View {self.__class__.__name__} can only be "
                "called by a HTMX request."
            )
        return super().dispatch(request, *args, **kwargs)


class HtmxTemplateMixin:
    """If called from HTMX, this view renders template names with a "_htmx" suffix."""

    def get_template_names(self):
        if self.request.htmx:
            if self.template_name_suffix:
                self.template_name_suffix += "_htmx"
            else:
                self.template_name_suffix = "_htmx"
        return super().get_template_names()


class HtmxFormMixin(HtmxResponseMixin):
    """
    Mixin for a form view that uses HTMX.

    Returns an "Hx-Trigger" attribute which triggers a Javascript event on the client.

    Attributes:
        success_event: a Javascript event that is triggered on the client after
            the request is completed.
    """

    success_event = ""

    def get_success_url(self):
        """Return an empty URL."""
        return ""

    def get_success_event(self):
        """Override this to return (e.g. generated) success event."""
        return self.success_event

    def form_valid(self, form):
        """Trigger a Javascript event on the client."""
        response = super().form_valid(form)
        event = self.get_success_event()
        if event:
            # in case of successful operation, and a success event is available,
            # send this event via hx-trigger
            response.headers["HX-Trigger"] = event
        return response

    # def form_invalid(self, form):
    #     # DEBUG
    #     print(form.errors)
    #     return super().form_invalid(form)


class HtmxDeleteView(HtmxFormMixin, DeleteView):
    response_status = 204

    def form_valid(self, form):
        # don't call DeleteView's form_valid(), as this needs a redirect_url
        # just delete object...
        self.object.delete()
        # ... and create an empty response
        return HttpResponse(status=self.response_status)


class ModalFormViewMixin(HtmxFormMixin):
    """Mixin for FormViews that should live in a modal.

    It relies on crispy-forms intensively, and already provides a form
    helper instance attribute you can use.

    In many cases, you need no template, as this mixin provides a generic one with
    a customizable title. The form is generated using crispy-forms.
    If you want to customize if further, then, extend "conjunto/modal-form.html".
    This template uses a ``header`` with a ``title`` block, a ``body``,
    and a ``footer`` block to override, for your modal dialog. In the
    footer, there is always a "Cancel" button, and as default, a "Save"
    button, which you can override using the "footer" block.

    When the modal pops up, the focus is set to the first visible input
    element.

    If the form is saved successfully, it returns an empty HttpResponse(204)
    and emits the event specified in ``success_event`` on the client,
    so that it can reload changed content.
    """

    template_name = "conjunto/modal-form.html"
    """The default template name for the modal form. This template provides
    a simple modal form. You can extend it in your own templates too."""

    modal_title: str = ""
    """The title of the modal form"""

    form_layout: list = []
    """The crispy forms layout for the form"""

    autofocus_field = ""  # TODO fix autofocus field
    """The field that gets the autofocus when the modal is shown."""

    def get_modal_title(self) -> str:
        """
        Returns:
            A string that is used as title of the modal.
        """
        return self.modal_title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"modal_title": self.get_modal_title()})
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # create a default form helper in case of none is created and remove form tag
        if not hasattr(form, "helper"):
            form.helper = FormHelper()
            form.helper.form_tag = False
            if self.form_layout:
                form.helper.layout = Layout(*self.form_layout)
        return form

    def form_valid(self, form):
        # call the super class, but return empty Response, including (Hx-) headers
        response = super().form_valid(form)
        response.status_code = 204
        return response


def clean_dict(input_dict: dict) -> dict:
    """Clean the input dictionary by removing any key-value pairs where the value is "undefined".

    :param input_dict: The input dictionary to be cleaned.
    :return: A dictionary with the same keys as the input dictionary, but with the "undefined" values removed.
    """
    return {key: value for key, value in input_dict.items() if value != "undefined"}


class PrepopulateFormViewMixin:
    """
    A mixin class that prepopulates form fields with values from the request.GET
    parameters.

    This mixin can be used with any FormView class to automatically prepopulate
    form fields with values from the URL query string parameters.

    Example usage:

    class MyFormView(PrepopulateFormMixin, FormView):
        form_class = MyForm
        template_name = 'my_template.html'
        success_url = reverse_lazy('my_success_url')

    In the above example, the form fields will be prepopulated with values from the URL
    query string parameters when the form view is loaded.
    """

    def get_initial(self):
        """Returns the initial data for the form."""
        initial = super().get_initial()
        initial.update(clean_dict(self.request.GET.dict()))
        return initial


class DynamicHtmxFormViewMixin(PrepopulateFormViewMixin):
    """Mixin class for dynamic form views.

    This mixin can be used with any FormView class to automatically prepopulate fields
    from GET parameters, and adds them to a "context" variable which is available within
    the form instance.

    This view is intended to be used together with `DynamicHtmxFormMixin` for the
    form_class.

    It creates a form_id (if not given) and passes it to the form. This is needed as
    HTMX target id.
    """

    form_id: str = ""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["context"] = self.get_initial()
        kwargs["context"].update(clean_dict(self.request.GET.dict()))
        kwargs["form_id"] = (
            self.form_id or f"form_id_{camel_case2snake(self.__class__.__name__)}"
        )
        return kwargs


class LatestVersionMixin:
    """
    A mixin for views that require fetching the latest version of an object.

    You can override the template in `<your_app_name>/versioned_page.html`.

    Attributes:
        title (str): The title of the view.
        no_object_available (str): The message to display when no object is available.

    """

    title: str = ""
    no_object_available: str = ""

    def get_object(self):
        return super().get_queryset().order_by("-version").last()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {"title": self.title, "no_object_available": self.no_object_available}
        )
        return context

    def get_template_names(self):
        return (
            self.template_name
            if self.template_name
            else [f"{ self.request.resolver_match.app_name}/versioned_page.html"]
        )


class GenericPrivacyView(LatestVersionMixin, DetailView):
    """Generic privacy page view that displays the newest PrivacyPage."""

    model = PrivacyPage


class GenericLicenseView(LatestVersionMixin, DetailView):
    """Generic privacy page view that displays the newest LicensePage."""

    model = LicensePage

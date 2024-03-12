import enum
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import urlsafe_base64_decode
from django.views.generic.detail import (
    SingleObjectMixin,
)
from django.views.static import serve
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import (
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
    CreateView,
)
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from conjunto.api.interfaces import (
    ISettingsSection,
    HtmxRequestMixin,
    UseElementMixin,
)
from conjunto.cms.models import TermsConditionsPage, PrivacyPage, StaticPage
from conjunto.http import HttpResponseEmpty
from conjunto.tools import camel_case2snake
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class HtmxTemplateMixin:
    """If called from HTMX, this view renders template names with a "_htmx" suffix."""

    def get_template_names(self):
        if self.request.htmx:
            if self.template_name_suffix:
                self.template_name_suffix += "_htmx"
            else:
                self.template_name_suffix = "_htmx"
        return super().get_template_names()


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


class DialogType(enum.Enum):
    """Enumeration of possible dialog levels.

    Levels are used from Python's logging module
    """

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    CREATE = NOTSET
    UPDATE = NOTSET
    DELETE = WARNING


class CrispyFormHelperMixin:
    """
    A mixin that helps with Crispy Forms.

    It creates a form helper instance attribute (if it doesn't exist yet) and sets
    form_tag to false. It also provides a form_layout attribute, which is a list of
    Crispy fields which will then be used as layout in the form.
    """

    form_layout: list = []
    """The crispy forms layout for the form"""

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # make sure that Crispy Forms doesn't create its own form tag
        # as this would destroy the modal window.
        # create a default form helper in case of none is created and remove form tag
        if not hasattr(form, "helper"):
            form.helper = FormHelper()
            form.helper.form_tag = False
            if self.form_layout:
                form.helper.layout = Layout(*self.form_layout)
        return form


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


class DynamicHtmxFormViewMixin(HtmxFormViewMixin):
    """Mixin class for dynamic form views.

    This mixin can be used with any FormView class, and adds them to a "context"
    variable which is available within the form instance.

    This view is intended to be used together with `DynamicHtmxFormMixin` for the
    form_class.

    It creates a form_id (if not given) and passes it to the form. This is needed as
    HTMX target id.
    """

    form_id: str = ""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["context"] = self.get_initial()
        kwargs["context"].update(clean_dict(self.request.POST.dict()))
        kwargs["form_id"] = (
            self.form_id or f"form_id_{camel_case2snake(self.__class__.__name__)}"
        )
        return kwargs

    def form_invalid(self, form):
        """When a form is dynamically reloaded by a HTMX trigger, don't show errors.

        This is achieved by adding a special attribute to the HTMX request.
        """
        if self.request.POST.get("_dynamic_reload"):
            form.errors.clear()
        return super().form_invalid(form)


class LatestVersionMixin:
    """
    A mixin for views that require fetching the latest version of an object.

    You can override the template in `<your_app_name>/versioned_page.html`.

    Attributes:
        no_object_available (str): The message to display when no object is available.
        create_url (str): The URL to link to where a new object can be created.
        edit_url (str): The URL to link to where an existing object can be edited.
    """

    no_object_available: str = ""
    create_url: str = ""
    edit_url: str = ""

    def __init__(self):
        super().__init__()
        if not self.model:
            raise AttributeError(
                f"{self.__class__.__name__} must provide a 'model' attribute."
            )
        self.no_object_available = self.no_object_available or (
            f"No {self.model._meta.verbose_name} available."
        )

        if not self.create_url:
            raise AttributeError(
                f"{self.__class__.__name__} must provide a 'create_url' attribute "
                f" to link to a new {self.model._meta.verbose_name} object."
            )

    def get_object(self):
        return super().get_queryset().order_by("-version").last()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {
                "no_object_available": self.no_object_available,
                "create_url": self.create_url,
            }
        )
        return context

    def get_template_names(self):
        """If no template_name is defined, return "versioned_page.html" for the app
        the current view is coming from.

        e.g. if the current view is in the app "my_app" and the template name is not
        defined, it returns "my_app/versioned_page.html".
        """
        return (
            self.template_name
            if self.template_name
            else [f"{ self.request.resolver_match.app_name}/versioned_page.html"]
        )


class GenericPrivacyView(LatestVersionMixin, DetailView):
    """Generic privacy page view that displays the newest PrivacyPage."""

    model = PrivacyPage
    no_object_available = _("No privacy information available yet.")


class GenericTermsConditionsView(LatestVersionMixin, DetailView):
    """Generic T&C page view that displays the newest Terms and conditions."""

    model = TermsConditionsPage
    no_object_available = _("No terms and conditions available yet.")


class GeneralStaticPageView(DetailView):
    """Renders a static page.

    Attributes:
        name: The name of the static page.
        model: The model of the static page. Defaults to StaticPage, but you can
            override it
    """

    name = ""

    model = StaticPage
    template_name = "conjunto/cms/staticpage.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must provide a 'name' attribute."
            )

    def get_object(self, queryset=None):
        return get_object_or_404(self.model._meta.model, name=self.name)


class MaintenanceView(TemplateView):
    template_name = "maintenance.html"


class AutoPermissionsViewMixin(PermissionRequiredMixin):
    """
    Automatically uses view/create/change/delete permissions for the given model.
    To be used with a CRUD view.

    It automatically generates the "<verb>_<model>" permission
    of the given model as necessary permission for this view.

    Attributes:
        _permissions_verb: the verb to create the permissions:
            'view', 'create', 'change', 'delete'. Defaults to "view".
    """

    _permissions_verb = "view"  # create, change, delete

    def get_permission_required(self):
        if self.permission_required is None:
            model = self.model
            if not model:
                raise AttributeError(
                    f"Model {self.__class__.__name__} needs a model attribute to "
                    f"auto-calculate permissions from."
                )
            return (
                f"{model._meta.app_label}.{self._permissions_verb}_{model._meta.model_name}",
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms


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


class HtmxSetModelAttributeView(SuccessEventMixin, SingleObjectMixin, View):
    """View mixin that sets an attribute on the given object and returns an empty
    response.

    This pattern is often needed in HTMX requests, to just set one or more attributes
    of an object when clicking on a button, and just refresh the widget, or page.

    Override the set_attribute method to set the desired attribute on the object.
    """

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed("You can not use a GET request on this URL.")

    def set_attribute(self):
        """Set an attribute on `self.object`. You don't have to save it, as this
        will be done automatically."""
        raise NotImplementedError(
            f"You must implement the 'set_attribute' method in {self.__class__.__name__}."
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.set_attribute()
        self.object.save()
        return HttpResponseEmpty()


class AnonymousRequiredMixin(PermissionRequiredMixin):
    """View mixin that only allows access for anonymous users."""

    def has_permission(self):
        # TODO: instead of a 403, redirect to LOGIN_REDIRECT_URL

        if not self.request.user.is_anonymous:
            redirect(reverse(settings.LOGIN_REDIRECT_URL))
        return True


class SettingsView(PermissionRequiredMixin, UseElementMixin, DetailView):
    """A generic view for application settings.

    This view doesn't update data itself.
    The actual forms processing and user data updating is done in component plugins.

    You can create `ISettingsSection` element plugins to add your own sections.
    """

    model = User
    template_name = "conjunto/settings.html"
    elements = [ISettingsSection]
    query_variable = "section"
    default_element_name = "account"

    def has_permission(self):
        return self.request.user.is_authenticated

    def get_object(self, queryset=None):
        return self.request.user


class ProtectedMediaBaseView(View):
    """Base view that served protected media files.

    Don't use this class directly. Use `PermissionRequiredMediaView` or
    `LoginRequiredMediaView` instead.
    """

    def get(self, request, path, as_download=False):  # noqa
        # Construct the full path to the media file
        response = serve(
            request,
            path,
            document_root=settings.PROTECTED_MEDIA_ROOT,
            show_indexes=False,
        )
        return response


class LoginRequiredMediaView(LoginRequiredMixin, ProtectedMediaBaseView):
    """A view that serves, but protects media files from unauthorized access by
    checking if user is logged in.

    It denies access to the `settings.PROTECTED_MEDIA_ROOT` directory to any
    anonymous user.
    You can directly use it in your urls.py:

    Example usage:
    ```python
    # urls.py
    urlpatterns = [
        path(
            "media/protected/<path>/",
            LoginRequiredMediaView.as_view(),
            name="protected_media",
        ),
        ...,
    ]
    ```
    """


class PermissionRequiredMediaView(PermissionRequiredMixin, ProtectedMediaBaseView):
    """A view that serves, but protects media files from unauthorized access by
    checking user permissions.

    It denies access to the `settings.PROTECTED_MEDIA_ROOT` directory without proper
    permissions.
    As it inherits PermissionRequiredMixin, you have to use the `permission_required`
    attribute to set the required permissions. You can directly use it in your urls.py
    by adding the permission_required attribute as parameter to `as_view()`,
    or subclass the view and set it there.

    Example usage:
    ```python
    # urls.py
    urlpatterns = [
        path(
            "media/protected/<path>/",
            PermissionRequiredMediaView.as_view(
                permission_required="my_project.view_media"),
            name="protected_media",
        ),
        ...,
    ]
    ```
    """


class LightboxView(SuccessEventMixin, TemplateView):
    """Gets path from URL and shows given file in a lightbox.

    The path can be relative to MEDIA_ROOT or PROTECTED_MEDIA_ROOT,
    or even include one of the two paths. LightBoxView will determine the path
    automatically, so it can be used perfectly from within a HTMX request.
    In fact, it does not respond to a non-HTMX request, as it should always open in a
    modal dialog.

    Arguments:
        path (str): path to the file to show in the lightbox.

    Example:
        ```django
        <a href="{% url 'lightbox' object.file.name %}">
            <img src="{% url 'lightbox' object.file.name %}"/>
        </a>
        ```
    """

    template_name = "conjunto/lightbox.html"
    permission_required = "conjunto.view_lightbox"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_path: str = kwargs["path"]
        image_url = ""
        # check if image_path is in MEDIA_ROOT or PROTECTED_MEDIA_ROOT
        if image_path.startswith(settings.PROTECTED_MEDIA_ROOT):
            if self.request.user.is_authenticated:
                image_url = settings.PROTECTED_MEDIA_URL + image_path.replace(
                    settings.PROTECTED_MEDIA_ROOT, ""
                )
        elif image_path.startswith(settings.MEDIA_ROOT):
            image_url = settings.MEDIA_URL + image_path.replace(settings.MEDIA_ROOT, "")
        # or, path is already a media relative path
        elif image_path.startswith(settings.MEDIA_URL) or image_path.startswith(
            settings.PROTECTED_MEDIA_URL
        ):
            image_url = image_path
        context["image_url"] = image_url
        return context


class TokenValidationView(TemplateView):
    """A TemplateView that verifies a token link.

    It renders a template you have to set, which has some context variables available:

    - token_valid (bool): Whether the token is valid or not.

    Attributes:
        template_name: The name of the template to render.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_user = None

    def get_context_data(self, **kwargs) -> dict:
        """Get token from URL and pass it into the template."""
        context = super().get_context_data(**kwargs)
        context["token_user"] = self.token_user
        return context

    def token_valid(self) -> HttpResponse:
        return self.render_to_response(self.get_context_data(token_valid=True))

    def token_invalid(self, **kwargs) -> HttpResponse:
        return self.render_to_response(self.get_context_data(token_valid=False))

    def token_preconditions_met(self) -> bool:
        """Returns True if a precondition for token validity was already met,
        else False.

        It can be assumed that self.token_user is already set.
        E.g., the token could be invalid if clicked a second time on the link,
        The user must be above 16 years, etc.
        """

    def get(self, request, *args, **kwargs) -> HttpResponse:
        try:
            uid = urlsafe_base64_decode(kwargs.get("uidb64")).decode()
            self.token_user = User.objects.get(pk=uid)

            # Check token precondition in subclasses
            if not self.token_preconditions_met():
                return self.token_invalid()

            # if user is just a system user, no MedSpeakAccount -> deny it!
            if not self.token_user:
                raise User.DoesNotExist
            if default_token_generator.check_token(
                self.token_user, kwargs.get("token")
            ):
                return self.token_valid()
            else:
                return self.token_invalid()

        except User.DoesNotExist:
            pass

        return self.token_invalid()

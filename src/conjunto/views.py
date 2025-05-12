import enum
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.static import serve
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (
    DetailView,
    TemplateView,
)

User = get_user_model()


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


class AnonymousRequiredMixin(PermissionRequiredMixin):
    """View mixin that only allows access for anonymous users."""

    def has_permission(self):
        # TODO: instead of a 403, redirect to LOGIN_REDIRECT_URL

        if not self.request.user.is_anonymous:
            redirect(reverse(settings.LOGIN_REDIRECT_URL))
        return True


class SettingsView(PermissionRequiredMixin, DetailView):
    """A generic view for application settings.

    This view doesn't update data itself.
    The actual forms processing and user data updating is done in component plugins.

    You must create `ISettingsSection` element plugins to add your own sections.
    """

    model = User
    template_name = "conjunto/settings.html"  # FIXME HTMX->Tetra

    def has_permission(self):
        return self.request.user.is_authenticated

    def get_object(self, queryset=None):
        return self.request.user


class ProtectedMediaBaseView(View):
    """Base view that served protected media files.

    Don't use this class directly. Use `PermissionRequiredMediaView` or
    `LoginRequiredMediaView` instead.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.__class__.__name__ == "ProtectedMediaBaseView":
            raise NotImplementedError(
                "ProtectedMediaBaseView may not be used directly. "
                "Use PermissionRequiredMediaView or LoginRequiredMediaView instead."
            )

    def get(self, request, path, as_download=False):  # noqa
        # TODO: implement `as_download`
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


class TokenValidationView(TemplateView):
    """A TemplateView that verifies a token link.

    It renders a template you have to set, which has some context variables
    available:
        token_valid (bool): True if the token was verified correctly, else False
        token_user (User): The User object from the token.
        token_already_used (bool): True if the cause of the token being invalid was
            that a certain hashed user attribute checked in the token had been changed.

    You have to provide a template_name.

    Attributes:
        template_name: The name of the template to render.
        token_generator: The obligatory token generator to use.
        token_already_used: Whether the token has already been used. Defaults to
            False, you can set it to true depending on conditions you set for yourself
    """

    token_generator = None
    token_already_used: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token_user: User | None = None

        if not self.token_generator:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires 'token_generator' attribute."
            )

    def get_context_data(self, **kwargs) -> dict:
        """Get token from URL and pass it into the template."""
        context = super().get_context_data(**kwargs)
        context.update(
            token_user=self.token_user, token_already_used=self.token_already_used
        )
        return context

    def token_valid(self) -> None:
        pass

    def token_invalid(self, **kwargs) -> None:
        pass

    def check_token_preconditions(self) -> bool:
        """Returns True if a precondition for token validity was already met,
        else False.

        It can be assumed that self.token_user is already set.
        E.g., the token could be invalid if clicked a second time on the link,
        The user must be above 16 years, etc.
        Use view attributes and include them into your template context if you want to
        show more information about the failing in your template
        """

    def get(self, request, uidb64, token, *args, **kwargs) -> HttpResponse:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.token_user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # user stays None in case of any error
            pass

        # Check token precondition in subclasses
        if self.token_user is not None:
            if self.check_token_preconditions():
                # if user is just a system user, no MedspeakAccount -> deny it!
                if self.token_generator.check_token(self.token_user, token):
                    self.token_valid()
                    return self.render_to_response(
                        self.get_context_data(token_valid=True)
                    )

        self.token_invalid()
        return self.render_to_response(self.get_context_data(token_valid=False))

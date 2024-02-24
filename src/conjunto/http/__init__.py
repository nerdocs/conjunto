from django.http import HttpResponse, HttpResponseRedirect


class HttpResponseEmpty(HttpResponse):
    """An HTTP response that has no content.

    Used for HTMX requests that should not return anything, like delete requests.
    The returned status code is **204** (No Content).
    """

    status_code = 204


class HttpResponseHXRedirect(HttpResponseRedirect):
    """A Http response that redirects a HTMX request to the location given in
    `redirect_to`"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200

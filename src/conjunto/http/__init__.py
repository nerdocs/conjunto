from django.http import HttpResponse, HttpResponseRedirect


class HttpResponseEmpty(HttpResponse):
    status_code = 204


class HttpResponseHXRedirect(HttpResponseRedirect):
    """A Http response that redirects a HTMX request to the location given in
    `redirect_to`"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200

import json

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.apps import apps
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import reverse, redirect
from django.conf import settings


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get("PATH_INFO", "")

        settings_model_name = settings.SETTINGS_MODEL
        request.settings = apps.get_model(settings_model_name).get_instance()

        # if user is logged in and is not staff, redirect to maintenance page
        # check also if requested URL is not one of the following:
        # - login page
        # - maintenance page
        # - media files
        if not request.user.is_staff:
            if (
                request.settings.maintenance_mode
                and (path not in [reverse("login"), reverse("maintenance")])
                and not path.startswith(settings.MEDIA_URL)
            ):
                return redirect(reverse("maintenance") + f"?next={request.path}")
                # FIXME kwargs

        response = self.get_response(request)

        return response


class HtmxMessageMiddleware:
    """Filters out django messages and puts them in to the HX-Trigger header if
    current request is a HTMX request"""

    # bases on Benoit Blanchon's
    # https://blog.benoitblanchon.fr/django-htmx-messages-framework/

    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        response: HttpResponse = await self.get_response(request)
        # TODO: implement device fetching in middleware

        # soup = BeautifulSoup(response.content, "html.parser")
        # body_tag = soup.find("body")
        # body_tag.append(soup.new_tag("div", string="test"))
        # response.content = str(soup)
        # response.content += b"<div id='request-item-15' hx-swap-oob='True'>foo</div>"
        if not request.htmx:
            return response

        # Ignore redirections, HTMX can't read it
        if 300 <= response.status_code < 400:
            return response

        # Ignore client-side redirection, because HTMX drops OOB swaps
        if "HX-Redirect" in response.headers:
            return response

        # Extract the messages, if response is empty
        if response.status_code == 204:  # Empty
            messages = [
                {
                    "message": message.message,
                    "tags": message.tags,
                    "extra_tags": message.extra_tags,
                }
                for message in get_messages(request)
            ]
            # response.write(
            #     render_to_string(
            #         template_name="common/toast.html",
            #         context={"messages": messages},
            #         request=request,
            #     )
            # )

        else:
            messages = []
        if not messages:
            return response

        # Get the existing HX-Trigger that could have been defined by the view
        hx_trigger = response.headers.get("HX-Trigger")

        if hx_trigger is None:
            # If the HX-Trigger is not set, start with an empty object
            hx_trigger = {}
        elif hx_trigger.startswith("{"):
            # If the HX-Trigger uses the object syntax, parse the object
            hx_trigger = json.loads(hx_trigger)
        else:
            # If the HX-Trigger uses the string syntax, convert to the object syntax
            hx_trigger = {hx_trigger: True}

        # Add the messages array in the HX-Trigger object
        hx_trigger["messages"] = messages

        # Add or update the HX-Trigger
        response.headers["HX-Trigger"] = json.dumps(hx_trigger)
        return response

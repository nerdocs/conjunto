from django.conf import settings


def tabler(request):
    """returns the TABLER settings for usage in your templates."""
    return {"tabler": settings.TABLER}

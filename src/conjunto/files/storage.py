from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ProtectedFileSystemStorage(FileSystemStorage):
    """
    Custom storage class for protected files.

    Overrides location and base_url with the custom settings.
    """

    def __init__(self, *args, **kwargs):
        kwargs["location"] = settings.PROTECTED_MEDIA_ROOT
        kwargs["base_url"] = settings.PROTECTED_MEDIA_URL
        super().__init__(*args, **kwargs)

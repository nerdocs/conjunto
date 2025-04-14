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

    def get_valid_name(self, name):
        return super().get_valid_name(name)

    def save(self, name, content, max_length=None):
        print(
            f"ProtectedFileSystemStorage: Saving file: {name} with content length: "
            f"{len(content)} bytes"
        )
        return super().save(name, content, max_length)

    def path(self, name):
        print(f"ProtectedFileSystemStorage: Path requested: {name}")  # Check if full
        # path is correct
        return super().path(name)

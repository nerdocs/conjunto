from django.db.models import FileField, ImageField

from .files.storage import ProtectedFileSystemStorage


class ProtectedFileField(FileField):
    def __init__(self, **kwargs):
        kwargs["storage"] = ProtectedFileSystemStorage()
        super().__init__(**kwargs)


class ProtectedImageField(ImageField):
    def __init__(self, **kwargs):
        kwargs["storage"] = ProtectedFileSystemStorage()
        super().__init__(**kwargs)

import datetime
import os

from django.core.files.utils import validate_file_name
from django.db.models import FileField, ImageField

from .files.storage import ProtectedFileSystemStorage


class ProtectedFileField(FileField):
    def __init__(self, **kwargs):
        # kwargs["storage"] = ProtectedFileSystemStorage()
        super().__init__(**kwargs)

    def generate_filename(self, instance, filename):
        if callable(self.upload_to):
            filename = self.upload_to(instance, filename)
        else:
            dirname = datetime.datetime.now().strftime(str(self.upload_to))
            filename = os.path.join(dirname, filename)
        filename = validate_file_name(filename, allow_relative_path=True)
        print(self.storage.generate_filename(filename))
        return self.storage.generate_filename(filename)

    def pre_save(self, instance, add):
        """
        Ensure Django saves the full relative path (including upload_to).
        """
        file = super().pre_save(instance, add)

        if file and hasattr(file, "name"):
            # Ensure that the stored file path includes the correct subdirectory
            if not file.name.startswith(self.upload_to):
                file.name = f"{self.upload_to}/{file.name}"
        return file


class ProtectedImageField(ImageField):
    def __init__(self, **kwargs):
        kwargs["storage"] = ProtectedFileSystemStorage()
        super().__init__(**kwargs)

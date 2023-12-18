# Settings


Conjunto provides a simple interface for settings. There is an abstract model named "AbstractSettings" which you can inherit from and add your own application settings as fields. It includes some basic fields that every application needs:



```python

from django.db import models
from conjunto.models import AbstractSettings

class MyApplicationSettings(AbstractSettings):
    my_special_setting = models.CharField(max_length=50)
```

### Middleware & Context processor

For the settings to be applied, you have to add conjunto's middlewares and context processors:

```python

MIDDLEWARE = [
    # ...
    "conjunto.middleware.SettingsMiddleware",
]

TEMPLATES = [
    {
        # ...
        "OPTIONS": {
            "context_processors": [
                # ...
                "conjunto.context_processors.globals",
            ]
        }
    }
]
```


At last, you have to provide the model that is used as settings by your application:

```python

SETTINGS_MODEL = "my_app.MyApplicationSettings"
```

This way your application is aware of the settings, and they can be used automatically in all templates by accessing `settings`:

```django
<h1>{{ settings.site_name }}</h1>
```

And in views, you can access the settings objects by using

```python
def my_view(request):
    if request.settings.maintenance_mode:
        ...
```
# Settings



Conjunto provides a simple interface for you application's settings.
There is an abstract model named "AbstractSettings" which you can inherit from and add your own application
settings as fields.

This model is a [SingletonModel][conjunto.models.SingletonModel] and represents simple, global settings or strings your application
needs, and which should be dynamically changable, such as `maintenance_mode`.


```python
from django.db import models
from conjunto.models import AbstractSettings

class MyApplicationSettings(AbstractSettings):
    site_is_cool = models.BooleanField(default=True)
```

Conjunto provides a few fields in `AbstractSettings`:

* site_name: A machine readable site name, like "conjunto"
* site_title: The human readable site name, like "Conjunto" - this is used as `<title>` meta tag, and can be used on your
    starting page, e.g. in a hero.
* site_description: A short description, which e.g. could be displayed on your starter page in a hero.
* maintenance_mode: boolean. Self-explanatory.
* maintenance_title: The title to display on your maintenance page
* maintenance_content: The content to display on your maintenance page



Set the `SettingsMiddleware`  and the model that is used as settings by your application in `settings.py`:

```python

MIDDLEWARE = [
    # ...
    "conjunto.middleware.SettingsMiddleware",
]

...

SETTINGS_MODEL = "my_app.MyApplicationSettings"
```

This way your application is aware of the settings, and they can be used automatically in all templates
by accessing  the `settings` variable:

```django
<h1>{{ settings.site_name }}</h1>
{% if settings.site_is_cool %}<p>This site is cool!</p>{% endif %}
```

Access the settings objects in views by using `request.settings`

```python
def my_view(request):
    if request.settings.maintenance_mode:
        ...
```



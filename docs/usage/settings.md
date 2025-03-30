# Settings

Conjunto provides a simple interface for you application's settings.

## Model

There is an abstract model named "AbstractSettings" which you can inherit from.

```python
from conjunto.models import AbstractSettings
from django.db import models

class MyApplicationSettings(AbstractSettings):
    site_is_cool = models.BooleanField(default=True)
```

This model is a model specific to one site and represents simple, global settings or strings 
that your application needs frequently, and which should be dynamically changeable, such as `maintenance_mode`.


Conjunto provides a few often used fields in `AbstractSettings`:

* **site_name**: A machine-readable site name, like "conjunto"
* **site_title**: The human-readable site name, like "Conjunto" - this is used as `<title>` meta tag, and can be used on your
    starting page, e.g. in a hero.
* **site_description**: A short description, which e.g. could be displayed on your starter page in a hero.
* **maintenance_mode**: boolean. Self-explanatory.
* **maintenance_title**: The title to display on your maintenance page
* **maintenance_content**: The content to display on your maintenance page


## Middleware

Set the `ConjuntoMiddleware` (and `TetraMiddleware`!) and the model that is used as settings by your application in `settings.py`:

```python

MIDDLEWARE = [
    # ...
    "conjunto.middleware.TetraMiddleware",
    "conjunto.middleware.ConjuntoMiddleware",
]

SETTINGS_MODEL = "my_app.MyApplicationSettings"
```

## Usage

This way your application is aware of the settings, and can use them automatically in all templates
by accessing  the `app_settings` variable:

```django
<h1>{{ app_settings.site_name }}</h1>
{% if app_settings.site_is_cool %}<p>This site is cool!</p>{% endif %}
```

Access the settings objects in views by using `request.app_settings`

```python
def my_view(request):
    if request.app_settings.maintenance_mode:
        ...
```



# Installation


Install Conjunto using pip

```bash
python -m pip install conjunto
```

There are a few things to set in your settings.py.

### Middleware & Context processor

For the settings to be applied, you have to add conjunto's middlewares, context processors, and `django-web-component`'s
templatetags as builtins:

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
                "conjunto.context_processors.settings",
            ]
        }
        "builtins": [
            "django_web_components.templatetags.components",
        ],
    }
]
```



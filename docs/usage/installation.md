# Installation


Install Conjunto using pip

```bash
python -m pip install conjunto
```

Add it to your `INSTALLED_APPS`, **before** django_extensions, because it overrides its management command
`update_permissions`.

```python
INSTALLED_APPS =  [
    ...
    "conjunto",
    "django_extensions",
    ...
]
```


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



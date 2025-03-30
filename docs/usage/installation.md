# Installation

### Module install

Install Conjunto in your Django application using pip:

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

For the settings to be applied, you have to add conjunto's middlewares, and context processors:

```python

MIDDLEWARE = [
    # ...
    "tetra.middleware.TetraMiddleware"
    "conjunto.middleware.ConjuntoMiddleware",
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
    }
]
```


### .env file
You have to  provide an `.env` file in your project directory to configure your conjunto application correctly. Use this as example:

```ini
SECRET_KEY="..."

# postgresql, mysql, sqlite3, oracle:
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/home/<user>/.../medspeak_site/db.sqlite3
DATABASE_USER=
DATABASE_PASS=

# your hostname / FQDN
ALLOWED_HOSTS=127.0.0.1,localhost
STATIC_ROOT=/home/<user>/.../medspeak_site/static
MEDIA_ROOT=/home/<user>/.../medspeak_site/media

# remove this on production sites:
DEBUG=True

# shows a red bar at the top to warn you that you are on a testing site
;TESTING=True  
```

To generate a SECRET_KEY, run
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```


### Testing site hint

It could lead to really nasty problems if you change content/settings on a production site while assuming you are on a testing server. Conjunto prevents this by looking for a `PRODUCTION` setting (defaults to `False`). If this is not actively set to `True`, it will render a red bar at the top of the `<body>`tag to indicate that you are on a testing site.

So add this to your settings:

```python
PRODUCTION = env("PRODUCTION", default=False)
```

And set it to `True` **only** in your production environment's `.env` file:
```ini
PRODUCTION=True
```

You can also access this setting via `PRODUCTION` anywhere in your templates:
```django
{% if not PRODUCTION %}
  <div>TESTING SITE!</div>
{% endif %}
```

## Tabler specific settings

You can customize tabler settings. Add the following to your settings.py:

### Layout

### `layout`

Choose between different layouts: `fluid`, `vertical`

### `container_breakpoint`
Select the (bootstrap) container breakpoint: `xl`, `lg`, `md`, `sm`,... (default to `xl`)

```python
TABLER = {
    "layout": "fluid",  
    "container_breakpoint": "md",  
}
```
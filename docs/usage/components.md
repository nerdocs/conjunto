# Components

Conjunto uses `django-web-components` as component library. This supports you to take a component bsed website
building approach. Conjunto provides some components that are often needed, like [Card][conjunto.components.Card].

Make sure your components are loaded at application start:

```python
# apps.py

class MyAppConfig(AppConfig):
    ...

    def ready(self):
        from . import components  # noqa
```



### Card
::: conjunto.components.Card
    show_root_heading: false
    members:

::: conjunto.components.Updateable
    members:
# Audit logging of model actions


Conjunto empowers you with efficient database audit logging functionality that is flexible and effective together.

The logging is done using a special Django model, but no "text" is written down as log string - Conjunto logs using *actions* that need to be defined before.
Django itself is also capable of using its (poorly documented) 
[LogEntry](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#logentry-objects) model. 
But Django only can log three actions: ADDITION, CHANGE, DELETION. 
This is way to few for a complex application, and it is not extendable at all.

Conjunto does not force you to have every model's actions being logged completely, but makes it easy to do so. 
You can implement basic CRUD action logging, but it is flexible enough to log specialized actions 
(*approve*, *email sent*, etc.) if you want.

The `BaseLogEntry` class provides a foundation for logging actions performed on Django models. 
It's designed to track changes and activities within your application with consistent metadata.

## Key Features
* Timestamps for when actions occurred
* (Extendable) action type categorization
* User tracking for accountability
* UUID grouping for related actions
* Customizable through inheritance


## Usage

### The `log_actions()` function

The best way of logging an action on a model is to use the builtin "log_action" function. It uses the correct 
(=registered) logging model for your model automatically. In many cases, this will be the included `ModelLogEntry`.

So whenever your code needs to log an action, call `log_action(<model_instance>, "<action_name>")`.

You can additionally add a `user` as third parameter, if this should be recorded. If ommitted, "System" is assumed as user.
See [log_action][conjunto.audit_log.log_action] for the full API.

```python
from conjunto.audit_log import log_action
from django.views.generic import UpdateView

# the actions "view" and "create" are builtins

class AuthorUpdateView(UpdateView):
    model = Author
    fields = ["name"]
    
    def get(self, *args, **kwargs):
        super().get(*args, **kwargs)
        log_action(self.object, "view")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.object, "create")
        return response
        
```
### Predefined *actions* 

There are a few ("CRUD") actions predefined which you can use instantly:

* *create*
* *view*
* *update*
* *delete*

These can be used without having to define them first in your application:

```python
log_action(any_model_instance, "create")
```

However, you can add your own actions using `LogActionRegistry.register.action()`. To simplfy this process, there is
a GDAPS hook named *"register_log_actions"* available, so you can simply add in your app's `gdaps_hooks.py`:

```python
from gdaps import hooks
from conjunto.audit_log.registry import LogActionRegistry
from django.utils.translation import gettext_lazy as _


@hooks.implements("register_log_actions")
def register_my_log_actions(actions: LogActionRegistry):
    # define basic generic hooks for your app
    actions.register_action("my_app.sale", _("Sell product"), _("Product sold"))
    actions.register_action("my_app.return", _("Return product"), _("Product returned"))
```

## Custom log entries

If you have special necessities for your model's logging, you can create your own LogEntry subclass, and register it.
This may be necessary if you have to log more than CRUD operations, e.g. when another model needs to be referenced.

```python
from django.db import models
from conjunto.audit_log.models import BaseLogEntry
from .models import Product, Customer

# Extending BaseLogEntry for a specific model
class ProductLogEntry(BaseLogEntry):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    def __str__(self):
        if self.action == "my_app.sale":
            return f"{self.product.name} sold to {self.customer}"
        elif self.action == "return":
            return f"{self.product} was returned by {self.customer}"
        else:
            return f"{self.product}: {self.action} (customer: {self.customer})"
```

### Implementation Notes
* The `LogEntry` class is abstract and meant to be extended
* Default ordering is by timestamp (newest first)
* Includes translation support via Django's gettext

### Related Classes
[ModelLogEntry][conjunto.audot_log.models.ModelLogEntry]: A concrete implementation for generic Django models
[ModelLogEntryManager]: Custom manager for model log
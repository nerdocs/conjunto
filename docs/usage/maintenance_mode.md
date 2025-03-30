# Maintenance mode

You can use conjunto's built-in maintenance mode. First, make sure you have installed the [Settings feature](settings.md) and the [URLs](urls.md) correctly.

Then you can set the maintenance mode in your admin panel.

If the maintenance mode is switched on, every request of a user that is not **staff** (meaning `user.is_staff`) will be redirected to `/maintenance/` which is a simple TemplateView.
You must provide a `maintenance.html` file for this to work properly.

You can access `settings.maintenance_title` and `settings.maintenance_content` in that template.


In each view, you can also use the maintenance mode:

```python
def my_view(request):
    if request.app_settings.maintenance_mode:
        ...
```

# URL configuration

Conjunto automatically provides some useful URLs. To use them, you need to add the URL patterns to your main `urls.py` file:

```python
# your main urls.py
from django.urls import path, include

urlpatterns = [
    #...
    path("", include("conjunto.urls"))
]
```


The login page contains a link to a url path named "signup", if it's available.

If you want to  use this feature, make sure you provide a signup path in your root urls.py:

```python
    path("signup/", MySignupView.as_view(), name="signup")
```

The same goes for "password_reset". Just provide an URL path, and the link becomes available.
```python
    path("password_reset/", PasswordResetView.as_view(), name="password_reset")
```
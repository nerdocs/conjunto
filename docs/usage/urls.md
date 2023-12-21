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
# tabler.io for Django

This is a module that includes all necessary items to create web pags using https://tabler.io

Mostly used are layouts, and it is kept free from other technologies like plugin or component systems

If you are searching for a combined set of widgets using Tabler.io, Tetra and GDAPS with django, use conjunto.




## Usage
Add the following to your settings.py:

```python
CONTEXT_PROCESSORS = [
    # ...
    "tabler.context_processors.tabler",
    # ...
]

# settings for tabler
TABLER = {
    "layout": "tabler/layouts/fluid.html", # vertical,...
    "container_breakpoint": "fluid",  # xl, lg, ...
}
```
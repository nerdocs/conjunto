import re
from typing import Iterable, Self

from django.utils.text import slugify
from gdaps.api import Interface


class MenuItemInterfaceMixin:
    """
    A mixin that provides common functionality for menu items or action buttons etc.

    Attributes:
        title: the (translatable) title that should be displayed
            in the menu.
        menu: The menu name where this MenuItem should be rendered. Can be any string.
            This menuitem is then found in templates under the `menu.<this-menu-attr>`
            menu. If you don't specify a menu, "main" is used.
        weight: The "weight" of the menu. The higher the weight, the more it "sinks"
            down in the menu. Default: 0
        icon: The (Bootstrap) icon name to display, if the menu shows icons.
        slug: The slug (machine name) of the item, used for css classes etc.
            If not provided, it is auto-generated from the title.
            To create submenus, you have to provide a slug, e.g. "extras". MenuItems
            that start with this slug + a "__" are considered submenus, e.g.
            "extras__license".
        view_name: The name of the view (in the form 'module:view-name',
            like in urls.py) under which this menu item should show up.
            If left empty, the menu item will show up under all views.
        permission_required: The permissions necessary to view this menu item.
            !!! warning
                this has nothing to do with the required permissions to call the URL
                that this MenuItem points to. You must make sure for yourself that
                the required permissions are checked correctly at the view.
        disabled: bool = False
        visible: If `True`, this item is visible.
        check: A callable that returns `True` if the item should be
            displayed, `False` otherwise.
    """

    CALLABLE_ATTRIBUTES = {"visible", "check", "icon", "title"}

    menu: str = "main"
    weight: int = 0
    title: str = ""
    slug: str = ""
    view_name: str = ""
    icon: str = None
    permission_required: list = []  # FIXME: rename to permissions_required
    disabled: bool = False
    visible: bool = True  # FIXME: `check` and `visible` are more or less duplicated.
    check: bool = True

    def initialize(self, request, *args, **kwargs) -> Self:
        """Helper function that needs to be called when the menu item is initialized
        during the request cycle.
        """
        self.request = request
        self._children = []
        # check permissions, and set visible as needed
        if self.permission_required:
            if isinstance(self.permission_required, str):
                self.permission_required = [self.permission_required]
            if not request.user.has_perms(self.permission_required):
                self.visible = False
                return self

        self._prepare_callable_attributes()

        # create slug form title if not available
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.check:
            self.visible = False
            return self

        return self

    def _prepare_callable_attributes(self):
        """Checks if any of the "callable attributes" are really callable, and sets
        them as static methods"""
        for attr in self.CALLABLE_ATTRIBUTES:
            # if attribute is callable, call it with current request as param
            if callable(getattr(self, attr)):
                # call it as static method to avoid "self" as parameter
                setattr(self, attr, getattr(self.__class__, attr)(self.request))

    def has_children(self) -> bool:
        """Returns `True` if this menu item has children, `False` otherwise."""
        if self._children:
            return True
        found = False
        for item in filter(
            lambda i: i.menu == self.menu and "__" in i.slug, iter(IMenuItem)
        ):
            # TODO improve children handling
            parts = item.slug.split("__")
            if len(parts) > 2:
                raise NotImplementedError(
                    "More than 2 levels of menus are not supported"
                )
            if parts[0] == self.slug:
                child = item(self.request)
                self._children.append(child)
                found = True
        self._children.sort(key=lambda child: child.weight)
        return found

    def has_parent(self) -> bool:
        """Returns `True` if this menu item has a parent, `False` otherwise."""
        return "__" in self.slug

    def children(self) -> Iterable:
        """Returns an iterable of all children of this menu item."""
        if self.has_children():
            for item in self._children:
                yield item
        else:
            return []

    def _underline_to_hyphen(self, attr: str):
        return attr.replace("_", "-")

    @property
    def attrs(self):
        attr_str = ""
        for attr in type(self).__dict__:
            if not attr.startswith("_") and attr not in INTERNAL_ATTRIBUTES:
                attr_str += f" {self._underline_to_hyphen(attr)}={getattr(self, attr)}"
        return attr_str

    @attrs.setter
    def attrs(self, value):
        self._attrs = value

    def enabled(self):
        return True

    def __getattr__(self, item):
        """For all regular attributes that are requested in the template and are
        not defined in the class, don't produce an error, just return an empty
        string."""
        if not item.startswith("_"):
            return ""
        return super().__getattribute__(item)

    @classmethod
    def filter(cls, name: str):
        """Filter the menu items by the 'menu' key name."""
        return filter(lambda item: item.menu == name, cls.plugins())


class IMenuItem(MenuItemInterfaceMixin, Interface):
    """An extendable and versatile MenuItem Interface

    You can use that for creating menu items in a named menu:
    ```python
    class AddUserAction(IMenuItem)
        menu = "page_actions"
        title = _("Add user")
        url = reverse_lazy("user:delete")
        icon = "user-delete"
    ```

    You can then use the menu in your template:
    ```django
    <ul class="list-inline">
    {% for item in menus.page_actions %}
        <li class="list-inline-item">
            <a href="{{ item.url }}"{% if item.selected %} class="active"{% endif %}>
                <i class="ti ti-{{ item.icon }} me-2"></i>
                {{ item.title }}
            </a>
        </li>
    {% endfor %}
    </ul>
    ```

    Attributes:
        url: the URL to call when this menu item is clicked.
        separator: if `True`, this menu item has a separator after it.
        badge: a callable that returns a string to be displayed in a badge.
        exact_url: if `True`, the `active` class will only get added on the menu item
            if the browser path matches exactly the MenuItem URL.
            If `False` (default), it also is active when child items are selected.
        collapsed: If `True`, this menu item is collapsed by default.
    """

    CALLABLE_ATTRIBUTES = ["title", "url", "badge", "icon", "check"]
    url: str = ""
    separator: bool = False
    badge: str = None
    exact_url: bool = False
    collapsed: bool = True
    _attrs: dict = {}

    def initialize(self, request, *args, **kwargs) -> Self:
        super().initialize(request, *args, **kwargs)
        if self.view_name and self.url:
            raise AttributeError("'view_name' and 'url' cannot be used together")
        if self.view_name and not request.resolver_match.view_name == self.view_name:
            self.visible = False
        return self

    def selected(self) -> bool:
        """Check current URL against this item."""
        is_current = False
        if self.exact_url:  # FIXME: exact_url does not work
            if re.match(f"{self.url}$", self.request.path):
                is_current = True
        elif re.match(f"{self.url}", self.request.path):
            is_current = True
        return is_current


class IActionButton(MenuItemInterfaceMixin, Interface):
    """An action button that can be added to an e.g. table row.

    Attributes:
        view_name str: The name of the view that should be called when this
            button is clicked. It will get the current row's object as param.
        method: the method to call the request: "get" (default) or "post".
    """

    CALLABLE_ATTRIBUTES = ["title", "icon", "check"]

    method = "get"
    url_params: list[str] = None

    def __init__(self, request, row_object):
        super(IActionButton, self).__init__(request)
        self.row_object = row_object
        self.method = self.method.lower()
        if self.method not in ["get", "post"]:
            raise ValueError(
                f"Method {self.method} is not supported for {self.__class__.__name__}. "
                "Use 'get' or 'post' instead."
            )


NON_CALLABLE_ATTRIBUTES = [
    "weight",
    "separator",
    "permission_required",
    "view_name",
    "exact_url",
]
INTERNAL_ATTRIBUTES = [
    "menu",
    "url",
    "slug",
    "title",
    "weight",
    "icon",
    "separator",
    "permission_required",
    "view_name",
    "badge",
    "disabled",
    "exact_url",
    "check",
    "visible",
    "collapsed",
]


class Menu:
    """Represents a named menu during a request.

    Usually it is used in Django templates by calling ``menus.<name>``
    which then will return all ``MenuItem``s with a matching "menu" name
    attribute. Therefore, Menu will be instantiated by a context_processor,
    so that the ``menus`` variable in the template is available:

    ```django
    <ul>
    {% for item in menus.user %}
        <li><a href="{{item.url}}">{{ item.title }}</a></li>
    {% endfor %}
    </ul>
    ```
    """

    def __init__(self, request):
        self.request = request
        self._cache = []
        for item in IMenuItem:
            # instantiate a MenuItem with current request as param
            self._cache.append(item.initialize(request))

    def __getitem__(self, name):
        """Returns filtered out menu items with the given '.menu' name."""
        for menu_item in self._cache:
            # TODO: handle submenus
            if (
                menu_item.menu == name  # only items in requested menu
                and "." not in menu_item.slug  # only top level items
                and menu_item.visible  # only visible items
            ):
                yield menu_item

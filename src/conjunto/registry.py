# Credits: copied + modified from wagtail.utils.registry
from typing import Any, TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:
    from django.db import models
    from conjunto.audit_log.models import BaseLogEntry

    ModelType = type[models.Model]
else:
    ModelType = TypeVar("ModelType", bound="type")


class ObjectTypeRegistry:
    """
    Implements a lookup table for mapping objects to values according to the object type.
    The most specific type according to the object's inheritance chain is selected.
    """

    def __init__(self):
        # values in this dict will be returned if the field type exactly matches an item here
        self.values_by_exact_class = {}

        # values in this dict will be returned if any class in the field's inheritance chain
        # matches, preferring more specific subclasses
        self.values_by_class: dict[ModelType, Any] = {}

    def register(self, cls: ModelType, value=None, exact_class=False) -> None:
        if exact_class:
            self.values_by_exact_class[cls] = value
        else:
            self.values_by_class[cls] = value

    def get_by_type(self, cls: ModelType) -> Union["BaseLogEntry", None]:
        try:
            return self.values_by_exact_class[cls]
        except KeyError:
            for ancestor in cls.mro():  # type:ModelType
                try:
                    return self.values_by_class[ancestor]
                except KeyError:
                    pass
        return None

    def get(self, obj) -> Union["BaseLogEntry", None]:
        value = self.get_by_type(obj.__class__)

        if callable(value) and not isinstance(value, type):
            value = value(obj)

        return value

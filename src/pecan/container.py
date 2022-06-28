from __future__ import annotations

from typing import Any, Callable, Dict

from .context import Context
from .providers import Provider, Singleton, Value


def _get_provider(value) -> Provider:

    if isinstance(value, Provider):
        return value

    if isinstance(value, Callable):
        return Singleton(value)

    return Value(value)


def _create_init(resolvers: dict):
    def init(self: Container):
        self._resolved = {}
        self._resolvers = resolvers

    return init


def _create_resolver(name):
    def _resolver(self):
        return self._resolve(name)

    return _resolver


class ContainerMetaclass(type):
    def __new__(cls, class_name, bases, class_dict):

        resolvers = {}

        for name, value in class_dict.items():

            if name.startswith("_"):
                continue

            resolvers[name] = _get_provider(value)
            class_dict[name] = _create_resolver(name)

        class_dict["__init__"] = _create_init(resolvers)

        class_obj = super().__new__(cls, class_name, bases, class_dict)

        return class_obj


class Container(metaclass=ContainerMetaclass):

    _resolved: Dict[str, Any]
    _resolvers: Dict[str, Provider]

    def _resolve(self, name: str) -> Any:
        ctx = Context(self_name=name, container=self)
        return self._resolvers[name].resolve(ctx)

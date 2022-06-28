from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .context import Context
from .providers import Provider, Singleton, Value

# This object is used to distinguish a dependency that is missing from the resolved
# dependencies cache, and an existing dependency with value `None`.
_MISSING = object()


@dataclass
class ResolutionException(Exception):

    chain: List[str]
    message: str

    def __str__(self):
        return f"{self.message}.\nResolution chain: {' -> '.join(reversed(self.chain))}"


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

        cached = self._resolved.get(name, _MISSING)
        if cached is not _MISSING:
            return cached

        resolver = self._resolvers.get(name)
        if resolver is None:
            raise ResolutionException(
                chain=[name], message=f"Missing resolver for name `{name}`"
            )

        ctx = Context(self_name=name, container=self)

        try:
            resolved = resolver.resolve(ctx)
        except ResolutionException as rex:
            rex.chain.append(name)
            raise rex
        except Exception as ex:
            raise

        return resolved

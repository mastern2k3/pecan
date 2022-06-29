from __future__ import annotations

from dataclasses import dataclass
from inspect import Signature
from typing import Any, Callable, Dict, List, Tuple, Type, Union

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


def _create_init(cls, resolvers: dict):
    def init(self: Container, override: Dict[str, Union[Provider, Any]] = {}):

        super(cls, self).__init__()

        self._resolvers.update(resolvers)

        for name, _override in override.items():
            self._resolvers[name] = _get_provider(_override)

    return init


def _create_resolver(name):
    def _resolver(self):
        return self._resolve(name)

    return _resolver


class ContainerMetaclass(type):
    def __new__(cls, class_name, bases: Tuple[Type, ...], class_dict: dict):

        if class_dict["__module__"] == __name__ and class_name == "Container":
            return super().__new__(cls, class_name, bases, class_dict)

        resolvers = {}

        for name, value in class_dict.items():

            if name.startswith("_"):
                continue

            resolvers[name] = _get_provider(value)
            class_dict[name] = _create_resolver(name)

        class_obj = super().__new__(cls, class_name, bases, class_dict)

        setattr(class_obj, "__init__", _create_init(class_obj, resolvers))

        return class_obj


class Container(metaclass=ContainerMetaclass):

    _resolved: Dict[str, Any]
    _resolvers: Dict[str, Provider]

    def __init__(self, override: Dict[str, Union[Provider, Any]] = {}):
        self._resolved = {}
        self._resolvers = {}

    def _fulfill_factory_signature(
        self,
        factory: Callable,
        signature: Signature,
    ) -> Any:

        dependencies = {}

        for param_name, param in signature.parameters.items():
            dependencies[param_name] = self._resolve(param_name)

        resolved = factory(**dependencies)

        return resolved

    def _resolve(self, name: str) -> Any:

        cached = self._resolved.get(name, _MISSING)
        if cached is not _MISSING:
            return cached

        resolver = self._resolvers.get(name)
        if resolver is None:
            raise ResolutionException(
                chain=[name],
                message=f"Missing resolver for name `{name}`",
            )

        try:
            resolved = resolver.resolve(name, self)
        except ResolutionException as rex:
            rex.chain.append(name)
            raise rex
        except Exception as ex:
            raise ResolutionException(
                chain=[name],
                message=f"Exception when trying to resolve name `{name}`",
            ) from ex

        return resolved

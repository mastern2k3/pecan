from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import Signature, signature
from typing import Callable, Generic, TypeVar

import uncontained

TDep = TypeVar("TDep")


class Provider(ABC, Generic[TDep]):
    def __call__(self) -> TDep:
        ...

    @abstractmethod
    def resolve(self, name: str, container: "uncontained.Container") -> TDep:
        pass


@dataclass
class Singleton(Provider[TDep]):

    factory: Callable[..., TDep]
    _signature: Signature = field(init=False)

    def __post_init__(self):
        self._signature = signature(self.factory)

    def resolve(self, name: str, container: "uncontained.Container") -> TDep:

        resolved = container._fulfill_factory_signature(self.factory, self._signature)

        container._resolved[name] = resolved

        return resolved


@dataclass
class Factory(Provider[TDep]):

    factory: Callable[..., TDep]
    _signature: Signature = field(init=False)

    def __post_init__(self):
        self._signature = signature(self.factory)

    def resolve(self, name: str, container: "uncontained.Container") -> TDep:

        resolved = container._fulfill_factory_signature(self.factory, self._signature)

        return resolved


@dataclass
class Value(Provider[TDep]):

    value: TDep

    def resolve(self, name: str, container: "uncontained.Container") -> TDep:
        return self.value

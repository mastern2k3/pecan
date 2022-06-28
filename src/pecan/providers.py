from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import Signature, signature
from typing import Callable, Generic, TypeVar

from .context import Context

# This object is used to distinguish a dependency that is missing from the resolved
# dependencies cache, and an existing dependency with value `None`.
_MISSING = object()


TDep = TypeVar("TDep")


class Provider(ABC, Generic[TDep]):
    def __call__(self) -> TDep:
        ...

    @abstractmethod
    def resolve(self, ctx: Context) -> TDep:
        pass


@dataclass
class Singleton(Provider[TDep]):

    factory: Callable[..., TDep]
    _signature: Signature = field(init=False)

    def __post_init__(self):
        self._signature = signature(self.factory)

    def resolve(self, ctx: Context) -> TDep:

        cached = ctx.container._resolved.get(ctx.self_name, _MISSING)
        if cached is not _MISSING:
            return cached  # type: ignore

        dependencies = {}

        for param_name, param in self._signature.parameters.items():
            dependencies[param_name] = ctx.container._resolve(param_name)

        resolved = self.factory(**dependencies)

        ctx.container._resolved[ctx.self_name] = resolved

        return resolved


@dataclass
class Value(Provider[TDep]):

    value: TDep

    def resolve(self, ctx: Context) -> TDep:
        return self.value

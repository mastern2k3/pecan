from dataclasses import dataclass

from pecan import Container, Singleton


@dataclass
class Inner:
    value: str


@dataclass
class Outer:
    inner: Inner


class _TestContainer(Container):
    value = "123"
    inner = Singleton(Inner)
    outer = Singleton(Outer)


def test_singleton():

    c = _TestContainer()

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "123"

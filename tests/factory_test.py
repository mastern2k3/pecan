from dataclasses import dataclass

from uncontained import Container, Factory, Singleton


@dataclass
class Inner:
    value: str


@dataclass
class Outer:
    inner: Inner


class _TestContainer(Container):
    value = "123"
    inner = Factory(Inner)
    outer = Singleton(Outer)


def test_factory():

    c = _TestContainer()

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is not c.inner()
    assert c.inner() is not c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "123"

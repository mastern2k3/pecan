from dataclasses import dataclass

from uncontained import Container, Factory, Singleton, Value


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


def test_override():

    c = _TestContainer(override={"value": "456"})

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is not c.inner()
    assert c.inner() is not c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "456"


def test_override_with_value_provider():

    c = _TestContainer(override={"value": Value("456")})

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is not c.inner()
    assert c.inner() is not c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "456"


def test_override_with_singleton_provider():

    c = _TestContainer(override={"value": Singleton(lambda: "456")})

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is not c.inner()
    assert c.inner() is not c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "456"

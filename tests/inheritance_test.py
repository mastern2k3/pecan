from dataclasses import dataclass

from uncontained import Container, Singleton, Value


@dataclass
class Inner:
    value: str


@dataclass
class Outer:
    inner: Inner


class _TestContainer(Container):
    value = "123"


class DerivedContainer(_TestContainer):
    inner = Singleton(Inner)
    outer = Singleton(Outer)


class DerivedContainer2(DerivedContainer):
    deep_inner = Singleton(Inner)


def test_inheritance():

    c = DerivedContainer()

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "123"


def test_deep_inheritance():

    c = DerivedContainer2()

    assert c.outer() is not None
    assert c.outer() is c.outer()
    assert c.inner() is c.outer().inner
    assert c.outer().inner is c.outer().inner
    assert c.outer().inner.value == "123"


class MixinContainerA(Container):
    value = "567"


class MixinContainerB(Container):
    inner = Singleton(Inner)


class MultipleInheritanceContainer(MixinContainerA, MixinContainerB):
    something = Value("something")


def test_multiple_inheritance():

    c = MultipleInheritanceContainer()

    assert c.inner() is not None
    assert c.inner().value == "567"
    assert c.something() == "something"


class OverrideValueContainer(_TestContainer):
    value = Value("456")


def test_provider_inheritance_overriding():
    c = OverrideValueContainer()

    assert c.value() == "456"

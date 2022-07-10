from dataclasses import dataclass

from pytest import raises

from uncontained import Container, ResolutionException, Singleton


@dataclass
class Inner:
    value: str


class MissingProviderContainer(Container):
    inner = Singleton(Inner)


def test_missing_provider():

    c = MissingProviderContainer()

    with raises(ResolutionException) as rex:
        c.inner()

    assert rex.value.chain == ["value", "inner"]


expected_exception = Exception("I'm expected")


def _raise_expected_exception():
    raise expected_exception


class ErrorProviderContainer(Container):
    value = _raise_expected_exception
    inner = Singleton(Inner)


def test_error_while_resolving():

    c = ErrorProviderContainer()

    with raises(ResolutionException) as rex:
        c.inner()

    assert rex.value.chain == ["value", "inner"]
    assert rex.value.__cause__ is expected_exception

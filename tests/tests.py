from dataclasses import dataclass
from typing import Optional

from pecan import Container, Singleton


@dataclass
class Inner:
    value: str


@dataclass
class Outer:
    inner: Inner
    sex: Optional[int]
    # jews: str


class Jew(Container):
    value = "123"
    sex = None
    inner = Singleton(Inner)
    outer = Singleton(Outer)


j = Jew()

print(f"{j.outer()}")


ooo = j.outer()

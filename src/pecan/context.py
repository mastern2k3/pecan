from dataclasses import dataclass

import pecan


@dataclass
class Context:
    self_name: str
    container: "pecan.Container"

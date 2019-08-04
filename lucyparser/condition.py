import enum
from dataclasses import dataclass
from typing import Any


class Operator(enum.Enum):
    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()


@dataclass
class Condition:
    """
    A single condition. Designed to be a leaf of condition tree
    """

    operator: Operator
    name: str
    value: Any

    def pprint(self, pad=0):
        print(" " * pad + str(self))

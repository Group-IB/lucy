from dataclasses import dataclass
from typing import Any
import enum

class Operator(enum.Enum):
    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()

@dataclass
class Expression():
    """
    A single expression. Designed to be a leaf of expression tree
    """
    operator: Operator
    name: str
    value: Any

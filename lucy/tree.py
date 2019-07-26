import enum
from dataclasses import dataclass
from typing import List, Union

from .expression import Expression


class LogicalOperator(enum.Enum):
    """
    Logical operators allowed in our tree.
    Order matters. Order defines priority.
    """

    NOT = 0
    AND = 1
    OR = 2


@dataclass
class ExpressionTree:
    operator: LogicalOperator
    children: List[Union[Expression, "ExpressionTree"]]

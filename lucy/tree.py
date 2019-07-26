import enum
from dataclasses import dataclass
from typing import List, Union

from .condition import Condition


class LogicalOperator(enum.Enum):
    NOT = enum.auto()
    AND = enum.auto()
    OR = enum.auto()


@dataclass
class ConditionTree:
    operator: LogicalOperator
    children: List[Union[Condition, "ConditionTree"]]

    def pprint(self, pad=0):
        print(" " * pad + str(self.operator))
        pad += 2
        for child in self.children:
            child.pprint(pad)

    def simplify(self):
        """
        Merge nested ORs and ANDs
        Transform
        AND
            a
            AND
                b
                c
        into
        AND
            a
            b
            c
        """
        for child in self.children:
            if isinstance(child, ConditionTree):
                child.simplify()
        if self.operator != LogicalOperator.NOT:
            new_children = []
            for child in self.children:
                if isinstance(child, ConditionTree) and child.operator == self.operator:
                    new_children.extend(child.children)
                else:
                    new_children.append(child)
            self.children = new_children

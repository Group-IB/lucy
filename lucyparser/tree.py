import enum
from dataclasses import dataclass, field
from typing import List, Any, Optional

from .exceptions import LucyUndefinedOperator


class Operator(enum.Enum):
    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()
    MATCH = enum.auto()


class RawOperator:
    NEQ = "!"
    EQ = ":"
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    MATCH = "~"

    equal_not_required = [EQ, NEQ, MATCH]
    equal_is_possible = [GT, LT]

    EQUAL_SIGN = "="


RAW_OPERATOR_TO_OPERATOR = {
    RawOperator.NEQ: Operator.NEQ,
    RawOperator.EQ: Operator.EQ,
    RawOperator.GT: Operator.GT,
    RawOperator.LT: Operator.LT,
    RawOperator.GTE: Operator.GTE,
    RawOperator.LTE: Operator.LTE,
    RawOperator.MATCH: Operator.MATCH
}


class LogicalOperator(enum.Enum):
    NOT = enum.auto()
    AND = enum.auto()
    OR = enum.auto()


@dataclass
class BaseNode:
    def pprint(self, pad=0):
        print(" " * pad + str(self.operator))


@dataclass
class LogicalNode(BaseNode):
    children: List = field(default_factory=list)

    _logical_operator = Optional[LogicalOperator]

    @property
    def operator(self):
        return self._logical_operator

    def pprint(self, pad=0):
        super().pprint(pad=pad)

        pad += 2
        for child in self.children:
            child.pprint(pad)


@dataclass
class AndNode(LogicalNode):
    _logical_operator = LogicalOperator.AND


@dataclass
class OrNode(LogicalNode):
    _logical_operator = LogicalOperator.OR


@dataclass
class NotNode(LogicalNode):
    _logical_operator = LogicalOperator.NOT


def get_logical_node(logical_operator: LogicalOperator, children: List = field(default_factory=list)):
    node_class = {
        LogicalOperator.AND: AndNode,
        LogicalOperator.OR: OrNode,
        LogicalOperator.NOT: NotNode,
    }.get(logical_operator)

    if node_class is None:
        raise LucyUndefinedOperator(operator=logical_operator)

    return node_class(children=children)


@dataclass
class ExpressionNode(BaseNode):
    name: Optional[str]
    value: Any

    operator: Operator


def simplify(tree: BaseNode) -> BaseNode:
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
    if not isinstance(tree, LogicalNode):
        return tree

    if isinstance(tree, AndNode) and (len(tree.children) == 1):
        return tree.children[0]

    if isinstance(tree, (OrNode, AndNode)):
        changed = True
        while changed:
            changed = False
            new_children: List[BaseNode] = []
            for child in tree.children:
                if isinstance(child, LogicalNode) and type(child) == type(tree):
                    new_children.extend(child.children)
                    changed = True
                else:
                    new_children.append(child)
            tree.children = new_children

    tree.children = [simplify(child) for child in tree.children]


    return tree

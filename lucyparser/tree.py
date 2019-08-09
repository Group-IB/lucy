import enum
from dataclasses import dataclass, field
from typing import List, Any, Optional


class Operator(enum.Enum):
    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()


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
        raise Exception(f"Undefined operator: {logical_operator}")

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

    tree.children = [simplify(child) if isinstance(child, LogicalNode) else child for child in tree.children]

    if not isinstance(tree, NotNode):
        new_children: List[BaseNode] = []
        for child in tree.children:
            if isinstance(child, LogicalNode) and type(child) == type(tree):
                new_children.extend(child.children)
            else:
                new_children.append(child)
        tree.children = new_children

    return tree

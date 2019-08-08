import enum
from dataclasses import dataclass, field
from typing import List, Any, Optional


class TreeType(enum.Enum):
    NOT = enum.auto()
    AND = enum.auto()
    OR = enum.auto()

    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    EQ = enum.auto()
    NEQ = enum.auto()


LOGICAL_TYPES = [TreeType.NOT, TreeType.AND, TreeType.OR]


@dataclass
class Tree:
    tree_type: TreeType
    children: List = field(default_factory=list)

    name: Optional[str] = None
    value: Any = None

    def pprint(self, pad=0):
        print(" " * pad + str(self.tree_type))
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
        if (self.tree_type == TreeType.AND) and (len(self.children) == 1):
            self.tree_type = self.children[0].tree_type
            self.value = self.children[0].value
            self.name = self.children[0].name

            self.children = []

        for child in self.children:
            if child.tree_type in LOGICAL_TYPES:
                child.simplify()
        if self.tree_type != TreeType.NOT:
            new_children = []
            for child in self.children:
                if child.tree_type == self.tree_type:
                    new_children.extend(child.children)
                else:
                    new_children.append(child)
            self.children = new_children

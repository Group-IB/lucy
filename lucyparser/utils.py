from typing import Callable

from lucyparser.tree import BaseNode, ExpressionNode, OPERATOR_TO_RAW_OPERATOR, Operator, OrNode, AndNode, NotNode


def build_query(tree: BaseNode, level=0) -> str:
    """
    :param tree: Parsed tree
    :param level: Current tree level
    :return: query as string
    """
    if isinstance(tree, ExpressionNode):
        raw_op = OPERATOR_TO_RAW_OPERATOR[tree.operator]
        operator = raw_op if tree.operator == Operator.EQ else f" {raw_op}"

        value = tree.value
        if isinstance(value, str) and '"' in value:
            value = value.replace('"', '\\"')

        return f"""{tree.name}{operator} \"{value}\""""

    format_str = "{}" if not level else "({})"
    if isinstance(tree, OrNode):
        return format_str.format(" OR ".join(build_query(child, level + 1) for child in tree.children))
    if isinstance(tree, AndNode):
        return format_str.format(" AND ".join(build_query(child, level + 1) for child in tree.children))

    if isinstance(tree, NotNode):
        return "NOT {}".format(build_query(tree.children[0], level + 1))


def update_tree(tree: BaseNode, handler: Callable[[BaseNode], int]) -> int:
    """
    :param tree: Parsed tree
    :param handler: Function with ExpressionNode as argument.
        That function is able to change current node or do nothing.
        It must return replacement count
    :return: replacement count
    """
    if isinstance(tree, ExpressionNode):
        return handler(tree)

    elif isinstance(tree, (AndNode, OrNode, NotNode)):
        replacement_count = handler(tree)

        for child in tree.children:
            replacement_count += update_tree(tree=child, handler=handler)

        return replacement_count

    return 0

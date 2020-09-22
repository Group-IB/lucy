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

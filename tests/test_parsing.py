import pytest

from lucyparser import parse
from lucyparser.parsing import Cursor
from lucyparser.tree import ExpressionNode, Operator, NotNode, AndNode, OrNode, BaseNode
from lucyparser.utils import build_query, update_tree


@pytest.mark.parametrize(
    "raw, parsed",
    [
        ("a:1", ExpressionNode(operator=Operator.EQ, name="a", value="1")),
        ("  \t  a    : 1   \t\t", ExpressionNode(operator=Operator.EQ, name="a", value="1")),
        (
            "fancy_field_name: '$TrInG \" !,?ad  '",
            ExpressionNode(
                operator=Operator.EQ, name="fancy_field_name", value='$TrInG " !,?ad  '
            ),
        ),
        (
            "NoT x: asd",
            NotNode(
                children=[ExpressionNode(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "NoT (x: asd)",
            NotNode(
                children=[ExpressionNode(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "((((NoT (((x: asd)))))))",
            NotNode(
                children=[ExpressionNode(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "a: x AND NOT b: y",
            AndNode(
                children=[
                    ExpressionNode(operator=Operator.EQ, name="a", value="x"),
                    NotNode(
                        children=[ExpressionNode(name="b", value="y", operator=Operator.EQ)],
                    ),
                ],
            ),
        ),
        (
            "a: x OR b: y AND c  : z OR NOT d: xx",
            OrNode(
                children=[
                    ExpressionNode(operator=Operator.EQ, name="a", value="x"),
                    AndNode(
                        children=[
                            ExpressionNode(name="b", value="y", operator=Operator.EQ),
                            ExpressionNode(name="c", value="z", operator=Operator.EQ),
                        ],
                    ),
                    NotNode(
                        children=[
                            ExpressionNode(name="d", value="xx", operator=Operator.EQ)
                        ],
                    ),
                ],
            ),
        ),
        ("a: 'use \\' quote'", ExpressionNode(operator=Operator.EQ, name="a", value="use ' quote")),
        ('a: "use \\" quote"', ExpressionNode(operator=Operator.EQ, name="a", value='use " quote')),
        ('a: -1', ExpressionNode(operator=Operator.EQ, name="a", value='-1')),
        ('a: 123.456', ExpressionNode(operator=Operator.EQ, name="a", value='123.456')),
        ('(    spaces_before_name   : 123  )', ExpressionNode(operator=Operator.EQ, name="spaces_before_name", value='123')),
        ("a:'*s.om.e-*fancy_string?'", ExpressionNode(operator=Operator.EQ, name="a", value='*s.om.e-*fancy_string?')),
        ('a > -1', ExpressionNode(operator=Operator.GT, name="a", value='-1')),
        ('a>= -1', ExpressionNode(operator=Operator.GTE, name="a", value='-1')),
        ('a      <= -1', ExpressionNode(operator=Operator.LTE, name="a", value='-1')),
        ('(a ! -1)', ExpressionNode(operator=Operator.NEQ, name="a", value='-1')),
        ('mail_from: ululul@ululu.net', ExpressionNode(operator=Operator.EQ, name="mail_from", value='ululul@ululu.net')),
        ('(a ! "ululu||ulul")', ExpressionNode(operator=Operator.NEQ, name="a", value='ululu||ulul')),
    ],
)
def test_simple_case(raw, parsed):
    actual = parse(raw)
    actual.pprint()
    parsed.pprint()
    assert actual == parsed


@pytest.mark.parametrize(
    "string,word,result",
    [
        ("dummy", "test", False),
        ("short", "loooooooong", False),
        ("end", "end", True),
        ("nothing", "not", False),
        ("not a thing", "not", True),
        ("CaSe insensitive", "case", True),
        ("tabs  are ok", "TABS", True),
    ],
)
def test_starts_with_a_word(string, word, result):
    assert Cursor(string).starts_with_a_word(word) is result


@pytest.mark.parametrize(
    "query,expected",
    [
        ('x: y OR y: z AND (NOT n: n OR ((((l: z)))))', 'x: "y" OR (y: "z" AND (NOT n: "n" OR l: "z"))'),
        ('(((NOT (x: y OR b:z))))', 'NOT (x: "y" OR b: "z")'),
        ('(((NOT (x: y) OR b:z)))', 'NOT x: "y" OR b: "z"'),
        ('(((NOT (x: y) OR b:"\\"ululul")))', 'NOT x: "y" OR b: "\\"ululul"'),
        ('NOT x: y', 'NOT x: "y"'),
    ],
)
def test_get_str_from_tree(query, expected):
    assert build_query(parse(query)) == expected


@pytest.mark.parametrize(
    "query,replaced_value_x_query,replaced_key_x_query",
    [
        ('x: "y"', 'x: "y"', 'not_x: "y"'),
        ('y: "x"', 'y: "not_x"', 'y: "x"'),
        ('x: "x"', 'x: "not_x"', 'not_x: "x"'),
    ],
)
def test_update_tree(query, replaced_value_x_query, replaced_key_x_query):
    def replace_value_x(tree: BaseNode) -> int:
        if isinstance(tree, ExpressionNode) and tree.value == "x":
            tree.value = "not_x"
            return 1
        return 0

    # replace value x
    tree = parse(query)
    update_tree(tree=tree, handler=replace_value_x)
    assert build_query(tree) == replaced_value_x_query

    def replace_key_x(tree: BaseNode) -> int:
        if isinstance(tree, ExpressionNode) and tree.name == "x":
            tree.name = "not_x"
            return 1
        return 0

    # replace key x
    tree = parse(query)
    update_tree(tree=tree, handler=replace_key_x)
    assert build_query(tree) == replaced_key_x_query

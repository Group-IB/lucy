import pytest

from lucyparser import parse
from lucyparser.parsing import Cursor
from lucyparser.tree import Tree, TreeType


@pytest.mark.parametrize(
    "raw, parsed",
    [
        ("a:1", Tree(tree_type=TreeType.EQ, name="a", value="1")),
        ("  \t  a    : 1   \t\t", Tree(tree_type=TreeType.EQ, name="a", value="1")),
        (
            "fancy_field_name: '$TrInG \" !,?ad  '",
            Tree(
                tree_type=TreeType.EQ, name="fancy_field_name", value='$TrInG " !,?ad  '
            ),
        ),
        (
            "NoT x: asd",
            Tree(
                tree_type=TreeType.NOT,
                children=[Tree(name="x", value="asd", tree_type=TreeType.EQ)],
            ),
        ),
        (
            "NoT (x: asd)",
            Tree(
                tree_type=TreeType.NOT,
                children=[Tree(name="x", value="asd", tree_type=TreeType.EQ)],
            ),
        ),
        (
            "((((NoT (((x: asd)))))))",
            Tree(
                tree_type=TreeType.NOT,
                children=[Tree(name="x", value="asd", tree_type=TreeType.EQ)],
            ),
        ),
        (
            "a: x AND NOT b: y",
            Tree(
                tree_type=TreeType.AND,
                children=[
                    Tree(name="a", value="x", tree_type=TreeType.EQ),
                    Tree(
                        tree_type=TreeType.NOT,
                        children=[Tree(name="b", value="y", tree_type=TreeType.EQ)],
                    ),
                ],
            ),
        ),
        (
            "a: x OR b: y AND c  : z OR NOT d: xx",
            Tree(
                tree_type=TreeType.OR,
                children=[
                    Tree(name="a", value="x", tree_type=TreeType.EQ),
                    Tree(
                        tree_type=TreeType.AND,
                        children=[
                            Tree(name="b", value="y", tree_type=TreeType.EQ),
                            Tree(name="c", value="z", tree_type=TreeType.EQ),
                        ],
                    ),
                    Tree(
                        tree_type=TreeType.NOT,
                        children=[
                            Tree(name="d", value="xx", tree_type=TreeType.EQ)
                        ],
                    ),
                ],
            ),
        ),
        ("a: 'use \\' quote'", Tree(tree_type=TreeType.EQ, name="a", value="use ' quote")),
        ('a: "use \\" quote"', Tree(tree_type=TreeType.EQ, name="a", value='use " quote')),
    ],
)
def test_simple_case(raw, parsed):
    actual = parse(raw)
    actual.pprint()
    parsed.pprint()
    assert parse(raw) == parsed


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

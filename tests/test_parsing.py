import pytest

from lucy import parse
from lucy.expression import Expression, Operator
from lucy.parsing import Cursor
from lucy.tree import ExpressionTree, LogicalOperator


@pytest.mark.parametrize(
    "raw, parsed",
    [
        ("a:1", Expression(operator=Operator.EQ, name="a", value="1")),
        (
            "  \t  a    : 1   \t\t",
            Expression(operator=Operator.EQ, name="a", value="1"),
        ),
        (
            "fancy_field_name: '$TrInG \" !,?ad  '",
            Expression(
                operator=Operator.EQ, name="fancy_field_name", value='$TrInG " !,?ad  '
            ),
        ),
        (
            "NoT x: asd",
            ExpressionTree(
                operator=LogicalOperator.NOT,
                children=[Expression(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
    ],
)
def test_simple_case(raw, parsed):
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

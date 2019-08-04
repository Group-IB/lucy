import pytest

from lucyparser import parse
from lucyparser.condition import Condition, Operator
from lucyparser.parsing import Cursor
from lucyparser.tree import ConditionTree, LogicalOperator


@pytest.mark.parametrize(
    "raw, parsed",
    [
        ("a:1", Condition(operator=Operator.EQ, name="a", value="1")),
        ("  \t  a    : 1   \t\t", Condition(operator=Operator.EQ, name="a", value="1")),
        (
            "fancy_field_name: '$TrInG \" !,?ad  '",
            Condition(
                operator=Operator.EQ, name="fancy_field_name", value='$TrInG " !,?ad  '
            ),
        ),
        (
            "NoT x: asd",
            ConditionTree(
                operator=LogicalOperator.NOT,
                children=[Condition(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "NoT (x: asd)",
            ConditionTree(
                operator=LogicalOperator.NOT,
                children=[Condition(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "((((NoT (((x: asd)))))))",
            ConditionTree(
                operator=LogicalOperator.NOT,
                children=[Condition(name="x", value="asd", operator=Operator.EQ)],
            ),
        ),
        (
            "a: x AND NOT b: y",
            ConditionTree(
                operator=LogicalOperator.AND,
                children=[
                    Condition(name="a", value="x", operator=Operator.EQ),
                    ConditionTree(
                        operator=LogicalOperator.NOT,
                        children=[Condition(name="b", value="y", operator=Operator.EQ)],
                    ),
                ],
            ),
        ),
        (
            "a: x OR b: y AND c  : z OR NOT d: xx",
            ConditionTree(
                operator=LogicalOperator.OR,
                children=[
                    Condition(name="a", value="x", operator=Operator.EQ),
                    ConditionTree(
                        operator=LogicalOperator.AND,
                        children=[
                            Condition(name="b", value="y", operator=Operator.EQ),
                            Condition(name="c", value="z", operator=Operator.EQ),
                        ],
                    ),
                    ConditionTree(
                        operator=LogicalOperator.NOT,
                        children=[
                            Condition(name="d", value="xx", operator=Operator.EQ)
                        ],
                    ),
                ],
            ),
        ),
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

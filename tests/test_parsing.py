import pytest

from lucyparser import parse
from lucyparser.parsing import Cursor
from lucyparser.tree import ExpressionNode, Operator, NotNode, AndNode, OrNode


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
        ('string.field ~ "[a-z]{0-9}.*test"', ExpressionNode(
            operator=Operator.MATCH,
            name="string.field",
            value="[a-z]{0-9}.*test",
        )),
        ('a: 123.456', ExpressionNode(operator=Operator.EQ, name="a", value='123.456')),
        ('(    spaces_before_name   : 123  )',
         ExpressionNode(operator=Operator.EQ, name="spaces_before_name", value='123')),
        ("a:'*s.om.e-*fancy_string?'", ExpressionNode(operator=Operator.EQ, name="a", value='*s.om.e-*fancy_string?')),
        ('a > -1', ExpressionNode(operator=Operator.GT, name="a", value='-1')),
        ('a>= -1', ExpressionNode(operator=Operator.GTE, name="a", value='-1')),
        ('a      <= -1', ExpressionNode(operator=Operator.LTE, name="a", value='-1')),
        ('(a ! -1)', ExpressionNode(operator=Operator.NEQ, name="a", value='-1')),
        ('mail_from: ululul@ululu.net',
         ExpressionNode(operator=Operator.EQ, name="mail_from", value='ululul@ululu.net')),
        ('(a ! "ululu||ulul")', ExpressionNode(operator=Operator.NEQ, name="a", value='ululu||ulul')),
        (
                'x: 1 AND ( (y: 2) OR (y: 3) )',
                AndNode(
                    children=[
                        ExpressionNode(name="x", value="1", operator=Operator.EQ),
                        OrNode(
                            children=[
                                ExpressionNode(name="y", value="2", operator=Operator.EQ),
                                ExpressionNode(name="y", value="3", operator=Operator.EQ),
                            ]
                        )
                    ]
                )
        ),
        (
                'x: 1 AND ((y: 2) OR (y: 3))',
                AndNode(
                    children=[
                        ExpressionNode(name="x", value="1", operator=Operator.EQ),
                        OrNode(
                            children=[
                                ExpressionNode(name="y", value="2", operator=Operator.EQ),
                                ExpressionNode(name="y", value="3", operator=Operator.EQ),
                            ]
                        )
                    ]
                )
        ),
        (
                'x: [\'1\', \'2\', \'    33333  \']',
                OrNode(
                    children=[
                        ExpressionNode(name="x", value='1', operator=Operator.EQ),
                        ExpressionNode(name="x", value='2', operator=Operator.EQ),
                        ExpressionNode(name="x", value='    33333  ', operator=Operator.EQ),
                    ]
                )
        ),
        (
                'x: [1,2,3]',
                OrNode(
                    children=[
                        ExpressionNode(name="x", value='1', operator=Operator.EQ),
                        ExpressionNode(name="x", value='2', operator=Operator.EQ),
                        ExpressionNode(name="x", value='3', operator=Operator.EQ),
                    ]
                )
        ),
        (
                'x: [1,2,3,       "4 here"      ] AND z: z',
                AndNode(
                    children=[
                        OrNode(
                            children=[
                                ExpressionNode(name="x", value='1', operator=Operator.EQ),
                                ExpressionNode(name="x", value='2', operator=Operator.EQ),
                                ExpressionNode(name="x", value='3', operator=Operator.EQ),
                                ExpressionNode(name="x", value='4 here', operator=Operator.EQ),
                            ]
                        ),
                        ExpressionNode(name='z', value='z', operator=Operator.EQ)
                    ]
                )
        ),
        (
                'field1: value1 OR (field2: value2 AND     x: [       1,2,3, 4 ])',
                OrNode(
                    children=[
                        ExpressionNode(name='field1', value='value1', operator=Operator.EQ),
                        AndNode(
                            children=[
                                ExpressionNode(name='field2', value='value2', operator=Operator.EQ),
                                OrNode(
                                    children=[
                                        ExpressionNode(name="x", value='1', operator=Operator.EQ),
                                        ExpressionNode(name="x", value='2', operator=Operator.EQ),
                                        ExpressionNode(name="x", value='3', operator=Operator.EQ),
                                        ExpressionNode(name="x", value='4', operator=Operator.EQ),
                                    ]
                                )
                            ]
                        )
                    ]
                )
        ),
        (
                'x: ["]", "["]',
                OrNode(
                    children=[
                        ExpressionNode(name='x', value=']', operator=Operator.EQ),
                        ExpressionNode(name='x', value='[', operator=Operator.EQ),
                    ]
                )
        ),
    ],
)
def test_simple_case(raw, parsed):
    actual = parse(raw)
    actual.pprint()
    parsed.pprint()
    assert actual == parsed


def test_simplify_recursion():
    query = ' OR '.join(["a: 1"] * 1000)
    parse(query)


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


def test_to_dict():
    tree = parse("ululu: ululu")
    assert tree.to_dict() == {'type': 'expr', 'operator': 'eq', 'name': 'ululu', 'value': 'ululu'}

    tree = parse("field1: value1 OR field2: value2")
    assert tree.to_dict() == {
        'type': 'or',
        'operator': 'OR',
        'children': [
            {'type': 'expr', 'operator': 'eq', 'name': 'field1', 'value': 'value1'},
            {'type': 'expr', 'operator': 'eq', 'name': 'field2', 'value': 'value2'}
        ]
    }

import string
from dataclasses import dataclass
from typing import Union

from .cursor import Cursor
from .expression import Expression, Operator
from .tree import ExpressionTree, LogicalOperator


def parse(string: str) -> Union[ExpressionTree, Expression]:
    """
    User facing parse function. All user needs to know about
    """
    cursor = Cursor(string)
    cursor.consume_spaces()
    parser = Parser()
    tree = parser.read_tree(cursor)
    cursor.consume_spaces()
    if not cursor.empty():
        raise Exception("Input should've been finished by now!")
    return tree


class Parser:
    name_chars = string.ascii_letters + string.digits + "_."
    name_first_chars = string.ascii_letters + "_"
    value_chars = string.ascii_letters + string.digits

    def read_tree(self, cur: Cursor) -> Union[ExpressionTree, Expression]:
        """
        Actual base function to parse expressions.
        Expression can start with one of the:
            - opening brace
            - NOT
            - field name:field_value
        """
        if cur.starts_with_a_char("("):
            cur.consume_known_char("(")
            tree = self.read_tree(cur)
            cur.consume_known_char(")")
            return tree
        if cur.starts_with_a_word("not"):
            cur.consume(3)
            cur.consume_spaces()
            tree = ExpressionTree(
                operator=LogicalOperator.NOT, children=[self.read_tree(cur)]
            )
            cur.consume_spaces()
            return tree
        return self.read_expressions(cur)

    def read_expressions(self, cur: Cursor) -> Union[ExpressionTree, Expression]:
        """
        Main purpose is handling ands and ors and their priorities
        """
        expression = self.read_expression(cur)
        cur.consume_spaces()
        if cur.starts_with_a_word("and") or cur.starts_with_a_word("or"):
            raise NotImplementedError(": (")
        else:
            return expression

    def read_expression(self, cur: Cursor) -> Expression:
        """
        Read a single entry of "name: value"
        """
        name = self.read_field_name(cur)
        cur.consume_spaces()
        cur.consume_known_char(":")
        cur.consume_spaces()
        value = self.read_field_value(cur)
        return Expression(name=name, value=value, operator=Operator.EQ)

    def read_field_name(self, cur: Cursor) -> str:
        name = cur.pop()
        if name not in self.name_first_chars:
            raise Exception(
                f"Unexpected character {name}. Expected one of {self.name_first_chars}"
            )
        while 1:
            next_char = cur.peek()
            if next_char and next_char in self.name_chars:
                name += cur.pop()
            else:
                return name

    def read_field_value(self, cur: Cursor) -> str:
        def read_until(terminator: str) -> str:
            value = ""
            while 1:
                if not cur.empty():
                    char = cur.pop()
                    if char == terminator:
                        return value
                    value += char
                else:
                    raise Exception("Unexpected end of input")

        if cur.starts_with_a_char('"'):
            cur.consume_known_char('"')
            return read_until('"')
        if cur.starts_with_a_char("'"):
            cur.consume_known_char("'")
            return read_until("'")
        next_char = cur.peek()
        if not next_char:
            raise Exception("Unexpected end of input")
        if next_char not in self.value_chars:
            raise Exception(
                f"Unexpected character {next_char}, expected one of {self.value_chars}"
            )
        value = cur.pop()
        while 1:
            next_char = cur.peek()
            if not next_char or next_char not in self.value_chars:
                return value
            value += cur.pop()
